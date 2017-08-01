# Python Kubernetes Initializer

This project is a library to aid in writing [initializers for Kubernetes 1.7](https://kubernetes.io/docs/admin/extensible-admission-controllers/).

## Getting Started

This was written using Python 3.6, and likely depends on features in Python 3.

On OS X, it also [requires having OpenSSL at least version 1.0](https://github.com/kubernetes-incubator/client-python/tree/6b555de1c7a1a291d0afcba91823ff419a044ca0#sslerror-on-macos). You can check your current OpenSSL version by running:
```
python3 -c "import ssl; print(ssl.OPENSSL_VERSION)"
```

You also almost certainly want to set up a virtual environment using [`venv`](https://docs.python.org/3/library/venv.html) or another tool. For example:
```bash
# From the project root.
python3 -m venv venv
# Or source the file appropriate to your shell.
source venv/bin/activate
```

After optionally setting up a virtual environment, you should install the requirements in [requirements.txt](./requirements.txt):
```
pip3 install -r requirements.txt
```

## Style & Formatting

This project uses [yapf](https://github.com/google/yapf) for formatting. Configuration is in
[.style.yapf](./.style.yapf).

For style checking, this uses [pylint](https://www.pylint.org/). Configuration is in
[.pylintrc](./.pylintrc).

Both of these will be installed from requirements.txt.

You can run both on all project files by executing [presubmit.sh](./presubmit.sh).

## Unit Tests

You can run all unit tests from the base directory by running:

```bash
python3 -m unittest
```
