# Python Kubernetes Initializer

The goal of this project is to make it very easy to write an [initializer for Kubernetes 1.7](https://kubernetes.io/docs/admin/extensible-admission-controllers/).

If you're interested in editing the project, see [the developer getting-started page](./GettingStartedDeveloper.md).

## Description

This library is written using Python 3.6, and isn't distributed as a Python 2 package. Much of it
should work in Python 2.

The main entrypoint is the `InitializerController`, which wraps per-type `ResourceController`s. A
`ResourceController` is responsible for fetching resources of a specific type from the Kubernetes
API, handling them (per the initializer contract), and then updating them in Kubernetes. API
communication is delegated to the `ResourceHandler` class, which has a few helper methods for
creating common API objects.
