`eventscore`: Power up your application with event-driven design!
=======================================

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Coverage Status](https://coveralls.io/repos/github/MatveyIvanov/eventscore/badge.svg?branch=main)](https://coveralls.io/github/MatveyIvanov/eventscore?branch=main)
![GitHub License](https://img.shields.io/github/license/MatveyIvanov/eventscore)
![PyPI - Version](https://img.shields.io/pypi/v/eventscore)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/eventscore)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/eventscore)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/MatveyIvanov/eventscore/test-ci.yml?branch=main)

What is `eventscore`?
-------------

See [the documentation](https://eventscore.readthedocs.io/en/latest/) for
more examples and information.

Quick start
-----------

`eventscore` can be installed using pip:

```bash
python3 -m pip install -U eventscore
```

If you want to run the latest version of the code, you can install from the
github directly:

```bash
python3 -m pip install -U git+https://github.com/MatveyIvanov/eventscore.git
```

Contributing
------------

Help in testing, development, documentation and other tasks is
highly appreciated and useful to the project.

To get started with developing `eventscore`, see [CONTRIBUTING.md](CONTRIBUTING.md).

First (0.1.0) release roadmap
-----------------------------
* 90%+ unit-test coverage
* e2e tests with basic flows
* integration tests for consumer discovering, threading, multiprocessing and redis stream
* CI for PRs, main and release branches
* CD for release branches

Stable (1.0.0) release roadmap
------------------------------

* 100% unit-test coverage
* integration tests for threading and multiprocessing
* e2e tests
* 100% docs coverage
* Kafka support
* outbox pattern support
* at least once semantic support
* at most once semantic support
* stress-tests, with/without eventscore performance comparison
* multiple event types per consumer group
* 
