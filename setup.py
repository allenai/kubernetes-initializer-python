# Adapted from https://github.com/pypa/sampleproject/blob/master/setup.py .

from setuptools import setup, find_packages
from codecs import open
import os

dirname = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file.
with open(os.path.join(dirname, 'PyPiReadme.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ai2-kubernetes-initializer',
    version='0.1.0b4',
    description='A simple Kubernetes initializer library.',
    long_description=long_description,
    url='https://github.com/allenai/kubernetes-initializer-python',
    author='Jesse Kinkead',
    author_email='jesse.kinkead@gmail.com',
    license='Apache License 2.0',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Systems Administration',
        'License :: OSI Approved :: Apache Software License',

        # TODO(jkinkead): Figure out which Python 3.x version we really depend on. We can probably
        # run on 3.5 or 3.4.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='kubernetes initializer',
    packages=find_packages(exclude=['test']),
    install_requires=['kubernetes>=3.0.0b1', 'requests[security]', 'urllib3'])
