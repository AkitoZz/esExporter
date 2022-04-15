#!/usr/bin/python
import os
import re

from setuptools import setup

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Environment :: Console',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 2 :: Only',
    'Programming Language :: Python :: 2.7',
    'Topic :: System :: Systems Administration',
    'Topic :: Database',
    'Topic :: Text Processing',
    'Topic :: Internet',
    'Topic :: Utilities',
]


def read_file(*paths):
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, *paths)) as f:
        return f.read()


src_file = read_file('esExporter_cli.py')
url = 'https://github.com/AkitoZz/esExporter'


def get_version():
    """
    Pull version from module without loading module first. This was lovingly
    collected and adapted from
    https://github.com/pypa/virtualenv/blob/12.1.1/setup.py#L67.
    """

    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              src_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def get_description():
    try:
        return src_file.split('\n')[2].split(':')[1].strip()
    except:
        raise RuntimeError("Unable to find description string.")


version = get_version()

with open('README.rst') as file_readme:
    readme = file_readme.read()
    readme = re.sub(r'.(/docs/[A-Z]+.rst)', r'%s/blob/%s\1' % (url, version), readme)

with open('docs/HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as file_requirements:
    requirements = file_requirements.read().splitlines()

settings = dict()
settings.update(
    name='esExporter',
    version=version,
    description=get_description(),
    long_description='%s\n\n%s' % (readme, history),
    author='AkitoZz',
    author_email='chenzg1996@gmail.com',
    license='Apache 2.0',
    url=url,
    classifiers=classifiers,
    python_requires='==2.7.*',
    keywords='elasticsearch export to file',
    py_modules=['esExporter', 'esExporter_cli'],
    entry_points={
        'console_scripts': [
            'esExporter = esExporter_cli:main'
        ]
    },
    install_requires=requirements,
)

setup(**settings)
