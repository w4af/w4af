"""
requirements.py

Copyright 2013 Andres Riancho

This file is part of w4af, https://w4af.net/ .

w4af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w4af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w4af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
from w4af.core.controllers.dependency_check.pip_dependency import PIPDependency

CORE = 1

CORE_PIP_PACKAGES = [
                     # acora speeds up string search, for regular expressions
                     # we use esmre to extract the string literals from the re
                     # and acora to match those against the target string
                     PIPDependency('ahocorasick', 'pyahocorasick', '2.0.0'),
                     PIPDependency('bloom-filter2', 'bloom-filter2', '2.0.0'),
                     # OpenAPI documentation parser
                     PIPDependency('bravado_core', 'bravado-core', '5.17.1'),
                     PIPDependency('chardet', 'chardet', '5.1.0'),
                     PIPDependency('cluster', 'cluster', '1.4.1.post3'),
                     PIPDependency('darts.lib.utils', 'darts-util-lru', '0.5'),
                     # String diff by Google
                     PIPDependency('diff_match_patch', 'diff-match-patch', '20200713'),
                     # Added for the crawl.ds_store plugin
                     PIPDependency('ds_store', 'ds-store', '1.3.1'),
                     # Only used by the REST API, but in the future the console
                     # and GUI will consume it so it's ok to put this here
                     PIPDependency('Flask', 'Flask', '2.2.2'),
                     PIPDependency('git.util', 'GitPython', '3.1.30'),
                     PIPDependency('github', 'PyGithub', '1.57'),
                     PIPDependency('ipaddresses', 'ipaddresses', '0.0.2'),
                     PIPDependency('jinja2', 'Jinja2', '3.1.2'),
                     PIPDependency('lxml', 'lxml', '4.9.2'),
                     # Fast compression library
                     PIPDependency('lz4', 'lz4', '4.3.2'),
                     PIPDependency('markdown', 'markdown', '3.4.1'),
                     # We "outsource" the HTTP proxy feature to mitmproxy
                     PIPDependency('mitmproxy', 'mitmproxy', '0.13'),
                     # For language detection
                     PIPDependency('morfessor', 'morfessor', '2.0.6'),
                     PIPDependency('msgpack', 'msgpack', '1.0.4'),
                     PIPDependency('ndg', 'ndg-httpsclient', '0.5.1'),
                     PIPDependency('nltk', 'nltk', '3.8.1'),
                     PIPDependency('nocasedict', 'nocasedict', '1.1.0'),
                     PIPDependency('ntlm', 'python-ntlm3', '1.0.2'),
                     # For language detection
                     PIPDependency('numpy', 'numpy', '1.24.2'),
                     PIPDependency('OpenSSL', 'pyOpenSSL', '22.1.0'),
                     PIPDependency('pdfminer', 'pdfminer', '20191125'),
                     # pebble multiprocessing
                     PIPDependency('pebble', 'pebble', '5.0.3'),
                     PIPDependency('phply', 'phply', '1.2.6'),
                     # For language detection
                     PIPDependency('polyglot', 'polyglot', '16.7.4'),
                     # This was used for testing, but now it's required for
                     # regular users too, do not remove!
                     PIPDependency('psutil', 'psutil', '5.9.4'),
                     PIPDependency('pyasn1', 'pyasn1', '0.4.8'),
                     PIPDependency('pyclamd', 'pyClamd', '0.4.0'),
                     # For language detection
                     PIPDependency('pycld2', 'pycld2', '0.41'),
                     # For language detection
                     PIPDependency('pyicu', 'pyicu', '2.10.2'),
                     PIPDependency('scapy.config', 'scapy', '2.5.0'),
                     PIPDependency('tblib', 'tblib', '1.7.0'),
                     # Console colors
                     PIPDependency('termcolor', 'termcolor', '2.2.0'),
                     # tldextract extracts the tld from any domain name
                     PIPDependency('tldextract', 'tldextract', '3.4.0'),
                     PIPDependency('vulndb', 'vulndb', '0.1.3'),
                     # Vulners API plugin needs this lib
                     PIPDependency('vulners', 'vulners', '2.0.8'),
                     PIPDependency('yaml', 'PyYAML', '6.0'),
                     ]