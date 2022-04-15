=========
Arguments
=========

============================================================  ==================================================================== 
                         Argument                                                        Description 
============================================================  ==================================================================== 
`-q, --query <#query>`_ QUERY                                 Query string in Lucene syntax.               [required]
`-o, --output-file <#output-file>`_ FILE                      CSV file location.                           [required]
`-u, --url <#url>`_ URL                                       Elasticsearch host URL. Default is "http://localhost:9200".
`-a, --auth <#auth>`_                                         Elasticsearch basic authentication in the form of username:password.
`-i, --index-prefixes <#index-prefixes>`_ INDEX [INDEX ...]   Index name prefix(es). Default is ['logstash-\*'].
`-f, --fields <#fields>`_ FIELDS [FIELDS ...]                 List of selected fields in output. Default is ['_all'].
`-s, --sort <#sort>`_ FIELDS [FIELDS ...]                     List of <field>:<direction> pairs to sort on. Default is [].
`-d, --delimiter <#delimiter>`_ DELIMITER                     Delimiter to use in CSV file. Default is ",".
`-m, --max <#max>`_ INTEGER                                   Maximum number of results to return. Default is 0.
-s, --scroll-size INTEGER                                     Scroll size for each batch of results. Default is 1000.
`--verify-certs <#verify-certs>`_                             Verify SSL certificates. Default is False.
`--ca-certs CA_CERTS <#ca-certs>`_                            Location of CA bundle.
--client-cert CLIENT_CERT                                     Location of Client Auth cert.
--client-key CLIENT_KEY                                       Location of Client Cert Key.
-v, --version                                                 Show version and exit.
--debug                                                       Debug mode on.
--header-on                                                   Export file with header.
-h, --help                                                    show this help message and exit
============================================================  ==================================================================== 

========
Examples
========

query
-----
Searching on http://localhost:9200, by default

.. code-block:: bash

  $ esExporter -q '{"query": {"match_all": {}}}' -o example.txt

output-file
-----------
Save to example.txt file

.. code-block:: bash

  $ esExporter -q '{"query": {"match_all": {}}}' -o example.txt

url
---
On custom Elasticsearch host

.. code-block:: bash

  $ esExporter -u my.cool.host.com:9200 -q '{"query": {"match_all": {}}}' -o example.txt

You are using secure Elasticsearch with nginx? No problem!

.. code-block:: bash

  $ esExporter -u http://my.cool.host.com/es/ -q '{"query": {"match_all": {}}}' -o example.txt

Not default port?

.. code-block:: bash

  $ esExporter -u my.cool.host.com:6666/es/ -q '{"query": {"match_all": {}}}' -o example.txt

auth
----
With Authorization

.. code-block:: bash

  $ esExporter -u http://login:password@my.cool.host.com:6666/es/ -q '{"query": {"match_all": {}}}' -o example.txt


With explicit Authorization

.. code-block:: bash

  $ esExporter -a login:password -u http://my.cool.host.com:6666/es/ -q '{"query": {"match_all": {}}}' -o example.txt

index-prefixes
--------------
Specifying index

.. code-block:: bash

  $ esExporter -i logstash-2015-07-07 -q '{"query": {"match_all": {}}}' -o example.txt

More indexes

.. code-block:: bash

  $ esExporter -i logstash-2015-07-07 logstash-2015-08-08 -q '{"query": {"match_all": {}}}' -o example.txt

Or index mask

.. code-block:: bash

  $ esExporter -i logstash-2015-* -q '{"query": {"match_all": {}}}' -o example.txt

And now together

.. code-block:: bash

  $ esExporter -i logstash-2015-01-0* logstash-2015-01-10 -q '{"query": {"match_all": {}}}' -o example.txt


Collecting all data on all indices

.. code-block:: bash

  $ esExporter -i _all -q '*' -o example.txt


fields
------
Selecting some fields, what you are interesting in, if you don't need all of them (query run faster)

.. code-block:: bash

  $ esExporter -f host status date -q '{"query": {"match_all": {}}}' -o example.txt


Or field mask

.. code-block:: bash

  $ esExporter -f 'ho*' 'st*us' '*ate' -q '{"query": {"match_all": {}}}' -o example.txt

Selecting all fields, by default

.. code-block:: bash

  $ esExporter -f _all -q '{"query": {"match_all": {}}}' -o example.txt


Selecting nested fields

.. code-block:: bash

  $ esExporter -f comments.comment comments.date comments.name -q '{"query": {"match_all": {}}}' -o example.txt

sort
----
Sorting by fields, in order what you are interesting in, could contains only field name (will be sorted in ascending order)

.. code-block:: bash

  $ esExporter -S key -q '*' -o example.txt

Or field pair: field name and direction (desc or asc)

.. code-block:: bash

  $ esExporter -S status:desc -q '*' -o example.txt

Using multiple pairs

.. code-block:: bash

  $ esExporter -S key:desc status:asc -q '*' -o example.txt

Selecting some field(s), but sorting by other(s)

.. code-block:: bash

  $ esExporter -S key -f user -q '*' -o example.txt

delimiter
---------
Changing column delimiter in CSV file, by default ','

.. code-block:: bash

  $ esExporter -d ';' -q '*' -i twitter -o example.txt

max
---
Max results count

.. code-block:: bash

  $ esExporter -m 10 -q '*' -i twitter -o example.txt

Retrieve 2000 results in just 2 requests (two scrolls 1000 each):

.. code-block:: bash

  $ esExporter -m 2000 -s 1000 -q '*' -i twitter -o example.txt


verify-certs
------------
With enabled SSL certificate verification (off by default)

.. code-block:: bash

  $ esExporter --verify-certs -u https://my.cool.host.com/es/ -q '*' -i twitter -o example.txt

ca-certs
--------
With your own certificate authority bundle

.. code-block:: bash

  $ esExporter --ca-certs '/path/to/your/ca_bundle' --verify-certs -u https://host.com -q '*' -i twitter -o example.txt
