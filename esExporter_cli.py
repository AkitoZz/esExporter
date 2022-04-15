#!/usr/bin/env python
"""
title:           A CLI tool for exporting data from Elasticsearch.
description:     Baseed on https://github.com/taraslayshchuk/es2csv developed. Command line utility, for querying Elasticsearch(7.x) in Lucene query syntax or Query DSL syntax and exporting result as documents into a file with custom fields.
usage:           esExporter -q '*' -i *idx* -o ~/file.txt -m 100
                 esExporter -q '{"query": {"match_all": {}}}' -i *idx* -o ~/file.txt
                 esExporter -q '{"query": {"match_all": {}}}' -i *idx* -m 10 --header-on -o ~/file.txt
                 esExporter -q @'~/long_query_file.json' -i *idx* -o ~/file.txt
                 esExporter -q '*' -i *idx* -f @timestamp log kubernetes.host -o ~/file.txt -m 100
                 esExporter -q '{"query": {"match_all": {}}, "filter":{"term":{"tags":"dev"}}}' -u http://elasticsearch-master:9200 -o ~/file.txt
"""
import sys
import argparse
import esExporter

__version__ = '7.5.1'


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('-q', '--query', dest='query', type=str, required=True, help='Query string in Lucene syntax.')
    p.add_argument('-u', '--url', dest='url', default='http://localhost:9200', type=str, help='Elasticsearch host URL. Default is %(default)s.')
    p.add_argument('-a', '--auth', dest='auth', type=str, required=False, help='Elasticsearch basic authentication in the form of username:password.')
    p.add_argument('-i', '--index-prefixes', dest='index_prefixes', default=['logstash-*'], type=str, nargs='+', metavar='INDEX', help='Index name prefix(es). Default is %(default)s.')
    p.add_argument('-o', '--output-file', dest='output_file', type=str, required=True, metavar='FILE', help='CSV file location.')
    p.add_argument('-f', '--fields', dest='fields', default=['_all'], type=str, nargs='+', help='List of selected fields in output. Default is %(default)s.')
    p.add_argument('-S', '--sort', dest='sort', default=[], type=str, nargs='+', metavar='FIELDS', help='List of <field>:<direction> pairs to sort on. Default is %(default)s.')
    p.add_argument('-d', '--delimiter', dest='delimiter', default=',', type=str, help='Delimiter to use in CSV file. Default is "%(default)s".')
    p.add_argument('-m', '--max', dest='max_results', default=0, type=int, metavar='INTEGER', help='Maximum number of results to return. Default is %(default)s.')
    p.add_argument('-s', '--scroll-size', dest='scroll_size', default=1000, type=int, metavar='INTEGER', help='Scroll size for each batch of results. Default is %(default)s.')
    p.add_argument('--verify-certs', dest='verify_certs', action='store_true', help='Verify SSL certificates. Default is %(default)s.')
    p.add_argument('--ca-certs', dest='ca_certs', default=None, type=str, help='Location of CA bundle.')
    p.add_argument('--client-cert', dest='client_cert', default=None, type=str, help='Location of Client Auth cert.')
    p.add_argument('--client-key', dest='client_key', default=None, type=str, help='Location of Client Cert Key.')
    p.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__, help='Show version and exit.')
    p.add_argument('--header-on', dest='header_on', action='store_true', help='Export file with header.')
    p.add_argument('--debug', dest='debug_mode', action='store_true', help='Debug mode on.')

    if len(sys.argv) == 1:
        p.print_help()
        exit()

    opts = p.parse_args()
    es = esExporter.EsExporter(opts)
    es.create_connection()
    es.check_indexes()
    es.search_query()
    es.clean_scroll_ids()
    es.compress_file()

if __name__ == '__main__':
    main()
