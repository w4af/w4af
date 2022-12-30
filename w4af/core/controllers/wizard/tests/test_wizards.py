"""
test_wizards.py

Copyright 2012 Andres Riancho

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

import pytest

from w4af.core.controllers.w4afCore import w4afCore
from w4af.core.controllers.misc.factory import factory
from w4af.core.controllers.exceptions import BaseFrameworkException
from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.options.bool_option import BoolOption


class test_wizards(object):

    unique_wizard_ids = []

    @pytest.mark.smoke
    def test_all_wizards(self):
        mod = 'w4af.core.controllers.wizard.wizards.%s'
        w4af_core = w4afCore()

        for filename in os.listdir('w4af/core/controllers/wizard/wizards/'):
            wizard_id, ext = os.path.splitext(filename)

            if wizard_id in ('__init__', '.git', '__pycache__') or ext == '.pyc':
                continue

            klass = mod % wizard_id
            wizard_inst = factory(klass, w4af_core)

            yield self._test_wizard_correct, wizard_inst

            wizard_inst = factory(klass, w4af_core)
            yield self._test_wizard_fail, wizard_inst

    @pytest.mark.smoke
    def _test_wizard_correct(self, wizard_inst):
        """
        @see test_questions.py for a complete test of questions.py and all the
             instances of that class that live in the questions directory.
        """
        wid = wizard_inst.get_name()
        assert wid != ''
        assert wid not in self.unique_wizard_ids
        self.unique_wizard_ids.append(wid)

        assert len(wizard_inst.get_wizard_description()) > 30

        while True:
            question = next(wizard_inst)
            if question is None:
                break
            else:
                opt = question.get_option_objects()
                filled_opt = self._correctly_fill_options(opt)
                wizard_inst.set_answer(filled_opt)

    @pytest.mark.smoke
    def _test_wizard_fail(self, wizard_inst):
        """
        @see test_questions.py for a complete test of questions.py and all the
             instances of that class that live in the questions directory.
        """
        while True:

            question = next(wizard_inst)

            if question is None:
                break
            else:
                opt = question.get_option_objects()
                try:
                    filled_opt = self._incorrectly_fill_options(opt)
                    wizard_inst.set_answer(filled_opt)
                except BaseFrameworkException:
                    # Now we correctly fill these values
                    filled_opt = self._correctly_fill_options(opt)
                    wizard_inst.set_answer(filled_opt)
                except Exception:
                    # The idea is that even when the user puts invalid
                    # values in the answer, we handle it with a BaseFrameworkException
                    # and show something to him. If we get here then something
                    # went wrong
                    assert False

    def _correctly_fill_options(self, option_list):
        """
        :return: A correctly completed option list, simulates a user that knows
                 what he's doing and doesn't make any mistakes.
        """
        values = {
            'target': URL('http://www.w4af.org'),
            'target_os': 'Unix',
            'target_framework': 'PHP'
        }

        for option in option_list:
            if isinstance(option, BoolOption):
                value = 'true'
            else:
                value = values.get(option.get_name(), 'abc')
            option.set_value(value)

        return option_list

    def _incorrectly_fill_options(self, option_list):
        """
        :return: Inorrectly completed option list, simulates a user that
                 doesn't know what he's doing and makes all the mistakes.
        """
        values = {
            'target': URL('foo://www.w4af.org'),
            'target_os': 'Minix',
            'target_framework': 'C++'
        }

        for option in option_list:
            if isinstance(option, BoolOption):
                value = 'true'
            else:
                value = values.get(option.get_name(), '#FAIL')
            option.set_value(value)

        return option_list
