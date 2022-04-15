======
esExporter
======

A CLI tool for exporting data from Elasticsearch into a file
----------------------------------------------------------------

Baseed on https://github.com/taraslayshchuk/es2csv developed. Command line utility, for querying Elasticsearch(7.x) in Lucene query syntax or Query DSL syntax and exporting result as documents into a file with custom fields.

Requirements
------------
| This tool should be used with Elasticsearch 7.x version.
| You also need `Python 2.7.x <https://www.python.org/downloads/>`_ and `pip <https://pip.pypa.io/en/stable/installing/>`_.

Installation
------------

From source:

.. code-block:: bash

    $ git clone https://github.com/AkitoZz/esExporter.git && python setup.py install


Usage
-----
.. code-block:: bash

 $ esExporter [-h] -q QUERY [-u URL] [-a AUTH] [-i INDEX [INDEX ...]] -o FILE
          [-f FIELDS [FIELDS ...]] [-S FIELDS [FIELDS ...]] [-d DELIMITER]
          [-m INTEGER] [-s INTEGER] [--verify-certs]
          [--ca-certs CA_CERTS] [--client-cert CLIENT_CERT]
          [--client-key CLIENT_KEY] [-v] [--debug] [--header-on]

 Arguments:
  -q, --query QUERY                        Query string in Lucene syntax.               [required]
  -o, --output-file FILE                   file location.                               [required]
  -u, --url URL                            Elasticsearch host URL. Default is http://localhost:9200.
  -a, --auth                               Elasticsearch basic authentication in the form of username:password.
  -i, --index-prefixes INDEX [INDEX ...]   Index name prefix(es). Default is ['logstash-*'].
  -f, --fields FIELDS [FIELDS ...]         List of selected fields in output. Default is ['_all'].
  -S, --sort FIELDS [FIELDS ...]           List of <field>:<direction> pairs to sort on. Default is [].
  -d, --delimiter DELIMITER                Delimiter to use in CSV file. Default is ",".
  -m, --max INTEGER                        Maximum number of results to return. Default is 0.
  -s, --scroll-size INTEGER                Scroll size for each batch of results. Default is 100.
  --verify-certs                           Verify SSL certificates. Default is False.
  --ca-certs CA_CERTS                      Location of CA bundle.
  --client-cert CLIENT_CERT                Location of Client Auth cert.
  --client-key CLIENT_KEY                  Location of Client Cert Key.
  -v, --version                            Show version and exit.
  --debug                                  Debug mode on.
  -h, --help                               show this help message and exit
  --header-on                              Export file with header

[ `Usage Examples <./docs/EXAMPLES.rst>`_ | `Release Changelog <./docs/HISTORY.rst>`_ ]
