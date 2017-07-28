#!/usr/bin/env bash

# Very simple presubmit format + lint.
yapf -i --recursive initializer
pylint initializer
