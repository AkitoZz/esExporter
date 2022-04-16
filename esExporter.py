import os
import gzip
import signal
import time
import json
import codecs
import elasticsearch
import progressbar
import thread
from functools import wraps


FLUSH_BUFFER = 1000  # Chunk of docs to flush in temp file
CONNECTION_TIMEOUT = 120
TIMES_TO_TRY = 3
RETRY_DELAY = 60


# Retry decorator for functions with exceptions
def retry(ExceptionToCheck, tries=TIMES_TO_TRY, delay=RETRY_DELAY):
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries = tries
            while mtries > 0:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    print(e)
                    print('Retrying in {} seconds ...'.format(delay))
                    time.sleep(delay)
                    mtries -= 1
                else:
                    print('Done.')
            try:
                return f(*args, **kwargs)
            except ExceptionToCheck as e:
                print('Fatal Error: {}'.format(e))
                exit(1)

        return f_retry

    return deco_retry


class EsExporter:

    def __init__(self, opts):
        self.opts = opts

        self.num_results = 0
        self.scroll_ids = []
        self.scroll_time = '2m'
        self.fields = []
        self.file = opts.output_file
        
        for sig in [signal.SIGINT, signal.SIGTERM]:
            signal.signal(sig, self.exit_by_signal)

    @retry(elasticsearch.exceptions.ConnectionError, tries=TIMES_TO_TRY)
    def create_connection(self):
        es = elasticsearch.Elasticsearch(self.opts.url, timeout=CONNECTION_TIMEOUT, http_auth=self.opts.auth,
                                         verify_certs=self.opts.verify_certs, ca_certs=self.opts.ca_certs,
                                         client_cert=self.opts.client_cert, client_key=self.opts.client_key)
        es.cluster.health()
        self.es_conn = es

    @retry(elasticsearch.exceptions.ConnectionError, tries=TIMES_TO_TRY)
    def check_indexes(self):
        indexes = self.opts.index_prefixes
        if '_all' in indexes:
            indexes = ['_all']
        else:
            indexes = [index for index in indexes if self.es_conn.indices.exists(index)]
            if not indexes:
                print('Any of index(es) {} does not exist in {}.'.format(', '.join(self.opts.index_prefixes), self.opts.url))
                exit(1)
        self.opts.index_prefixes = indexes

    @retry(elasticsearch.exceptions.ConnectionError, tries=TIMES_TO_TRY)
    def search_query(self):
        @retry(elasticsearch.exceptions.ConnectionError, tries=TIMES_TO_TRY)
        def next_scroll(scroll_id):
            return self.es_conn.scroll(scroll=self.scroll_time, scroll_id=scroll_id)

        search_args = dict(
            index=','.join(self.opts.index_prefixes),
            sort=','.join(self.opts.sort),
            scroll=self.scroll_time,
            size=self.opts.scroll_size,
            terminate_after=self.opts.max_results
        )

        if self.opts.query.startswith('@'):
            query_file = self.opts.query[1:]
            if os.path.exists(query_file):
                with codecs.open(query_file, mode='r', encoding='utf-8') as f:
                    self.opts.query = f.read()
            else:
                print('No such file: {}.'.format(query_file))
                exit(1)
        
        try:
            query = json.loads(self.opts.query)
        except ValueError as e:
            print('Invalid JSON syntax in query. {}'.format(e))
            exit(1)
        search_args['body'] = query
        
        if '_all' not in self.opts.fields:
            search_args['_source'] = ','.join(self.opts.fields)

        if self.opts.debug_mode:
            print('Using these indices: {}.'.format(', '.join(self.opts.index_prefixes)))
            print('Query[{0[0]}]: {0[1]}.'.format(
                ('Query DSL', json.dumps(query, ensure_ascii=False).encode('utf8')) if self.opts.raw_query else ('Lucene', query))
            )
            print('Output field(s): {}.'.format(', '.join(self.opts.fields)))
            print('Sorting by: {}.'.format(', '.join(self.opts.sort)))

        res = self.es_conn.search(**search_args)
        self.num_results = res['hits']['total']['value']

        print('Found {} results.'.format(self.num_results))
        if self.opts.debug_mode:
            print(json.dumps(res, ensure_ascii=False).encode('utf8'))

        if self.num_results > 0:
            codecs.open(self.file, mode='w', encoding='utf-8').close()
            
            if res['hits']['hits']:
                if '_source' in res['hits']['hits'][0] and len(res['hits']['hits'][0]['_source']) > 0:
                    def get_header(source, ancestors=[], header_delimeter='.'):
                        def is_list(arg):
                            return type(arg) is list
                        
                        def is_dict(arg):
                            return type(arg) is dict
                        
                        if is_dict(source):
                            for key in source.keys():
                                get_header(source[key], ancestors + [key])
                        elif is_list(source):
                            [get_header(item, ancestors + [str(index)]) for index, item in enumerate(source)]
                        else:
                            header = header_delimeter.join(ancestors)
                            self.fields.append(header)
            
                    get_header(res['hits']['hits'][0]['_source'])
                    if self.opts.header_on:
                        with codecs.open(self.file, mode='a', encoding='utf-8') as tmp_file:
                            tmp_file.write("\t\t".join(self.fields).rstrip("\n") + "\n")
                            
            hit_list = []
            total_lines = 0

            widgets = ['Run query ',
                       progressbar.Bar(left='[', marker='#', right=']'),
                       progressbar.FormatLabel(' [%(value)i/%(max)i] ['),
                       progressbar.Percentage(),
                       progressbar.FormatLabel('] [%(elapsed)s] ['),
                       progressbar.ETA(), '] [',
                       progressbar.FileTransferSpeed(unit='docs'), ']'
                       ]
            bar = progressbar.ProgressBar(widgets=widgets, maxval=self.num_results).start()

            while total_lines != self.num_results:
                if res['_scroll_id'] not in self.scroll_ids:
                    self.scroll_ids.append(res['_scroll_id'])

                if not res['hits']['hits']:
                    print('Scroll[{}] expired(multiple reads?). Saving loaded data.'.format(res['_scroll_id']))
                    break
                for hit in res['hits']['hits']:
                    total_lines += 1
                    bar.update(total_lines)
                    hit_list.append(hit)
                    if len(hit_list) == FLUSH_BUFFER:
                        self.flush_to_file(hit_list)
                        hit_list = []
                    if self.opts.max_results:
                        if total_lines == self.opts.max_results:
                            self.flush_to_file(hit_list)
                            print('Hit max result limit: {} records'.format(self.opts.max_results))
                            return
                res = next_scroll(res['_scroll_id'])
            self.flush_to_file(hit_list)
            bar.finish()

    def flush_to_file(self, hit_list):
        def to_keyvalue_pairs(source, ancestors=[], header_delimeter='.'):
            def is_list(arg):
                return type(arg) is list

            def is_dict(arg):
                return type(arg) is dict

            if is_dict(source):
                for key in source.keys():
                    to_keyvalue_pairs(source[key], ancestors + [key])

            elif is_list(source):
                [to_keyvalue_pairs(item, ancestors + [str(index)]) for index, item in enumerate(source)]
            else:
                header = header_delimeter.join(ancestors)
                out[header] = source

        with codecs.open(self.file, mode='a', encoding='utf-8') as tmp_file:
            for hit in hit_list:
                if '_source' in hit and len(hit['_source']) > 0:
                    out = {}
                    to_keyvalue_pairs(hit['_source'])
                    tmp_file.write("\t\t".join([str(out[field]) for field in self.fields]).rstrip("\n") + "\n")
        tmp_file.close()

    def clean_scroll_ids(self):
        try:
            for sid in self.scroll_ids:
                self.es_conn.clear_scroll(scroll_id=sid)
        except Exception as e:
            print(str(e))
            
    def exit_by_signal(self, signum, frame):
        self.clean_scroll_ids()
        
    def compress_file(self):
        gz_file = self.file + '.gz'
        with open(self.file, "rb") as f_in:
            with gzip.open(gz_file, "wb") as f_out:
                f_out.write(f_in.read())
        os.remove(self.file)
