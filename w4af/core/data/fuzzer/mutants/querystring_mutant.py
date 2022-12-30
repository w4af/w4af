"""
QSMutant.py

Copyright 2006 Andres Riancho

This file is part of w4af, http://w4af.org/ .

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
from w4af.core.data.fuzzer.mutants.mutant import Mutant


class QSMutant(Mutant):
    """
    This class is a query string mutant.
    """
    def __init__(self, freq):
        Mutant.__init__(self, freq)

    def set_dc(self, data_container):
        self._freq.get_uri().querystring = data_container

    def get_dc(self):
        return self._freq.get_uri().querystring

    @staticmethod
    def get_mutant_type():
        return 'query string'
