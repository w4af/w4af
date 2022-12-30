"""
test_form_id_list_option.py

Copyright 2017 Andres Riancho

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
import os
import unittest
import json

from w4af import ROOT_PATH
from w4af.core.controllers.exceptions import BaseFrameworkException
from w4af.core.data.options.opt_factory import opt_factory
from w4af.core.data.options.option_types import FORM_ID_LIST

def normalise_json(string):
    return json.dumps(json.loads(string), sort_keys=True)

class TestFormIDListOptionOption(unittest.TestCase):

    INPUT_FILE = os.path.relpath(os.path.join(ROOT_PATH, 'core', 'data',
                                              'options', 'tests', 'test.txt'))

    def test_valid_form_id_list_one(self):
        value = '[{"action": "/"}]'
        opt = opt_factory('name', value, 'desc', FORM_ID_LIST, 'help', 'tab')

        self.assertEqual(opt.get_value_for_profile(), value)

        form_id_list = opt.get_value().get_form_ids()

        self.assertEqual(len(form_id_list), 1)
        self.assertEqual(form_id_list[0].action.pattern, '/')

    def test_valid_form_id_list_fail(self):
        value = '[{"action": "/foo"}, {"action": "/bar", "method--FAIL": "get"}]'
        self.assertRaises(BaseFrameworkException, opt_factory,
                          'name', value, 'desc', FORM_ID_LIST, 'help', 'tab')

    def test_valid_form_id_list_many(self):
        value = '[{"action": "/foo"}, {"action": "/bar", "method": "get"}]'
        opt = opt_factory('name', value, 'desc', FORM_ID_LIST, 'help', 'tab')

        self.assertEqual(normalise_json(opt.get_value_for_profile()), normalise_json(value))

        form_id_list = opt.get_value().get_form_ids()

        self.assertEqual(len(form_id_list), 2)
        self.assertEqual(form_id_list[0].action.pattern, '/foo')
        self.assertEqual(form_id_list[1].action.pattern, '/bar')
        self.assertEqual(form_id_list[1].method, 'get')