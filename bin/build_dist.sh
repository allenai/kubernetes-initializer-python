#!/usr/bin/env bash

# Build the distributed package.
cd $(dirname $0)/..
rm -rf dist
python3 setup.py sdist bdist_wheel
