[![Unit tests](https://github.com/w4af/w4af/actions/workflows/python-app.yml/badge.svg)](https://github.com/w4af/w4af/actions/workflows/python-app.yml)
## w4af - Web Advanced Application Attack and Audit Framework for Python3

[w4af](https://w4af.readthedocs.io/en/latest/) is an [open source](https://www.gnu.org/licenses/gpl-2.0.txt)
web application security scanner which helps developers and penetration testers
identify and exploit vulnerabilities in their web applications.

The scanner is able to identify [200+ vulnerabilities](w3af/core/data/constants/vulns.py),
including [Cross-Site Scripting](w3af/plugins/audit/xss.py),
[SQL injection](w3af/plugins/audit/sqli.py) and
[OS commanding](w3af/plugins/audit/os_commanding.py).

## Python3 Port Progress

The original w3af code only supports python up to version 2.7. This repository is an
attempt to add python3 support.

At time of writing, a subsection of the core tests are running and passing:

```
nosetests -A 'not moth and not internet and not fails' -w ./w3af/core/data/ -x -v
```

You might have some limited success running scans with the current code, but very likely it will fail with mysterious errors. More updates as they become available.

## Installation

### Python

The project's Python dependencies can be install with pipenv:

```
python -m pip install --upgrade pipenv wheel
pipenv install
```

Running `pipenv shell` with then launch a shell from which it is possible to run w3af.

### Node

The project uses NodeJS libraries for some features. To install those dependencies, run:

```
npm install
```

## Development

Use `nosetests` to run the unit tests:

```
$ nosetests
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
