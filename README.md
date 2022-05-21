[![Unit tests](https://github.com/w4af/w4af/actions/workflows/python-app.yml/badge.svg)](https://github.com/w4af/w4af/actions/workflows/python-app.yml)
[![Code Coverage](https://codecov.io/gh/w4af/w4af/branch/main/graph/badge.svg?token=GCXS9IDNKM)](https://codecov.io/gh/w4af/w4af)
[![License](https://img.shields.io/github/license/w4af/w4af.svg)](https://img.shields.io/github/license/w4af/w4af.svg)
## w4af - Web Advanced Application Attack and Audit Framework for Python3

[w4af](https://w4af.readthedocs.io/en/latest/) is an [open source](https://www.gnu.org/licenses/gpl-2.0.txt)
web application security scanner which helps developers and penetration testers
identify and exploit vulnerabilities in their web applications.

The scanner is able to identify [200+ vulnerabilities](w4af/core/data/constants/vulns.py),
including [Cross-Site Scripting](w4af/plugins/audit/xss.py),
[SQL injection](w4af/plugins/audit/sqli.py) and
[OS commanding](w4af/plugins/audit/os_commanding.py).

## Python3 Port Progress

The original w4af code only supports python up to version 2.7. This repository is an
attempt to add python3 support.

At time of writing, most of the core unit tests are running and passing:

```
nosetests -A "not moth and not internet and not fails and not git and not gui and not suspect and not integration and not ci_ignore" -x -v .
```

You might have some limited success running scans with the current code, but very likely it will fail with mysterious errors. More updates as they become available.

## Installation

### Python

The project expects to use Python 3.9, but is compatible with later versions. The project's Python dependencies can be install with pipenv:

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

Use `nosetests` to run the unit tests:

```
$ nosetests --help
```

By default, nosetests will run all tests, including tests that depend on internet connection, a clean git checkout, and a running integration environment. We will add more detailed information about how to run the tests as the porting work progresses.

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
