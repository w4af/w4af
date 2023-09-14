[![Unit tests](https://github.com/w4af/w4af/actions/workflows/python-app.yml/badge.svg)](https://github.com/w4af/w4af/actions/workflows/python-app.yml)
[![Code Coverage](https://codecov.io/gh/w4af/w4af/branch/main/graph/badge.svg?token=GCXS9IDNKM)](https://codecov.io/gh/w4af/w4af)
[![License](https://img.shields.io/github/license/w4af/w4af.svg)](https://img.shields.io/github/license/w4af/w4af.svg)
![Release](https://img.shields.io/badge/release-Alpha-blue)
## w4af - Web Advanced Application Attack and Audit Framework for Python3

[w4af](https://w4af.readthedocs.io/en/latest/) is an [open source](https://www.gnu.org/licenses/gpl-2.0.txt)
web application security scanner which helps developers and penetration testers identify and exploit vulnerabilities in their web applications. It is originally based on [w3af](https://github.com/andresriancho/w3af) and is currently in an early **alpha** development phase. We welcome early user experience and bug reports, but we don't make any warranties about the software - it's still a work in progress.

The scanner is able to identify [200+ vulnerabilities](w4af/core/data/constants/vulns.py),
including [Cross-Site Scripting](w4af/plugins/audit/xss.py),
[SQL injection](w4af/plugins/audit/sqli.py) and
[OS commanding](w4af/plugins/audit/os_commanding.py).

## Documentation

We recommend you to read the [user guide](https://w4af.readthedocs.io/en/latest/) before starting to use w4af, there
are many FAQs, tips and tricks and other important pieces of information in
the manual.

## Installation

### Python

The project expects to use Python 3.11, currently only Ubuntu 22.04 LTS is supported. The project's Python dependencies can be installed by running pipenv in the project's root folder:

```
python -m pip install --upgrade pipenv wheel
pipenv install
```

Running `pipenv shell` with then launch a shell from which it is possible to run w4af.

### Node

The project uses NodeJS libraries for some features. To install those dependencies, run:

```
npm install
```

## Development

Use `pytest` to run the unit tests:

```
$ pytest --help
```

By default, pytest will run all tests, including tests that depend on internet connection, a clean git checkout, and a running integration environment.

### Unit tests

The unit tests should run without any integration environment (though some do rely on a live internet connection):

```
pytest -m "not moth and not wavsep and not w4af_moth and not sqlmap and not mcir and not wivet and not phpmoth and not fails and not git and not gui and not integration and not ci_ignore and not slow and not wordpress and not modsecurity"
```

### Integration tests

You can launch the integration environment with docker-compose:

```
./w4af/tests/add-test-routes.sh
docker-compose -f ./w4af/tests/docker-compose.yml up
```

With that running, the integration tests should also pass. Integration tests are tagged according to which environment they rely on - the tag of the test matches the label for the docker service in `docker-compose.yml`. This will be one of `moth`, `w4af_moth`, `sqlmap`, `mcir`, `wivet`, or `phpmoth`, for example:

```
docker-compose -f ./w4af/tests/docker-compose.yml up w4af_moth
pytest -m "w4af_moth and not fails"
```

### Building documentation

First install sphinx within a virtual environment and then build documentation
```
python -m pip install sphinx
sphinx-build -b html doc/sphinx/ doc/sphinx/_build/
```

## Vision

The purpose of this software is to help security researches to scan their sites to find vulnerabilities.

## Disclaimer

You are only allowed to scan websites that you own and/or have permissions to scan. The developers can not be made responsible for any damage that occurs by using this software. Use at your own risk.

## Contributing

Pull requests are always welcome! If you're not sure where to start, please take
a look at the TODO [First steps as a contributor](w4af/wiki/First-steps-as-a-contributor)
document in our wiki. All contributions, no matter how small, are welcome.

## Links and documentation
 * [Project documentation](https://w4af.readthedocs.io/en/latest/)
