.. :changelog:

Release Changelog（developed based on https://github.com/taraslayshchuk/es2csv 5.5.2）
=================

7.5.1 (2022-03-03)
------------------
- Delete -D -t -k -r -e argument.
- Added --header-on argument for exported file with header or not.
- Updateing version elasticsearch to 7.x

5.5.2 (2018-03-21)
------------------
- Fixed encoding in field name to UTF-8. (Issue `#35 <https://github.com/taraslayshchuk/es2csv/issues/35>`_)
- Added --sort(-S) argument for sorting data by selected field. (Issue `#41 <https://github.com/taraslayshchuk/es2csv/issues/41>`_)
- Added requirement for version of python 2.7.*. (Issue `#8 <https://github.com/taraslayshchuk/es2csv/issues/8>`_, `#12 <https://github.com/taraslayshchuk/es2csv/issues/12>`_, `#20 <https://github.com/taraslayshchuk/es2csv/issues/20>`_, `#29 <https://github.com/taraslayshchuk/es2csv/issues/29>`_, `#33 <https://github.com/taraslayshchuk/es2csv/issues/33>`_ and `#38 <https://github.com/taraslayshchuk/es2csv/issues/38>`_)
- Update documentation with examples.
- Updating version elasticsearch-py to 5.5.*.
