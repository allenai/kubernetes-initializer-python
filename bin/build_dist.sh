#!/usr/bin/env bash

# Build the distributed package.
cd $(dirname $0)/..
rm -rf dist build ai2_kubernetes_initializer.egg-info
python3 setup.py sdist bdist_wheel
