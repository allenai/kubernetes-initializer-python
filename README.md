# Python Kubernetes Initializer

The goal of this project is to make it very easy to write an [initializer for Kubernetes 1.7](https://kubernetes.io/docs/admin/extensible-admission-controllers/).

If you're interested in editing the project, see [the developer getting-started page](./GettingStartedDeveloper.md).

## Examples

Example initializers are in the [examples folder](./examples).

## Description

This library is written using Python 3.6, and isn't distributed as a Python 2 package. Much of it
should work in Python 2.

The main entrypoint is the `InitializerController`, which wraps per-type `ResourceController`s. A
`ResourceController` is responsible for fetching resources of a specific type from the Kubernetes
API, handling them (per the initializer contract), and then updating them in Kubernetes. API
communication is delegated to the `ResourceHandler` class, which has a few helper methods for
creating common API objects.

## The Dangers of Pod Initializers

### Controller-Created Pods Require Initialization

When an initializer is created on pods, all pods created through the API are affected. This includes
pods created by built-in controllers, like the Job controller and the ReplicaSet controller.

Because of this, it's important to design any pod initializer to be low-latency, and to handle both
user-created (i.e. `kubectl`) pods, as well as automatically-created pods.

### Unbounded Pod Creation

As of Kubernetes 1.7, the API server will wait for all initializers to complete before returning a
newly-created object. This means that slow or failing initializers will result in a client-side
timeout during object creation.

Some controllers (like the Job controller) will retry creation indefinitely on client error,
including for timeouts. This means that a pod-targeted initializer that's slow or broken can result
in an unbounded number of pods awaiting initialization. Because of this, you should be careful
assigning an initializer to pods, and should be very sure that it's robust if you do. You also
should ensure your initializer is looking for uninitialized pods frequently enough that
clients won't time out.
