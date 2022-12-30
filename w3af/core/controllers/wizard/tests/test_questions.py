"""
test_questions.py

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

from w4af.core.data.options.option_list import OptionList


class test_questions(object):

    unique_question_ids = []

    @pytest.mark.smoke
    def test_all_questions(self):
        """
        This is a very basic test where we perform the following:
            * Create an instance
            * Exercise all getters
            * Exercise all setters
            * Make sure "back" works
        """
        mod = 'w4af.core.controllers.wizard.questions.%s'
        w4af_core = w4afCore()

        for filename in os.listdir('w4af/core/controllers/wizard/questions/'):
            question_id, ext = os.path.splitext(filename)

            if question_id in ('__init__', '.git', '__pycache__') or ext == '.pyc':
                continue

            klass = mod % question_id
            question_inst = factory(klass, w4af_core)

            yield self._test_qid, question_inst

    @pytest.mark.smoke
    def _test_qid(self, question_inst):
        """
        Ahhh, nose's magic of test generators :D
        """
        orig = question_inst.get_question_title()
        question_inst.set_question_title('New')
        new = question_inst.get_question_title()
        assert 'New' == new

        orig = question_inst.get_question_string()
        question_inst.set_question_string('New')
        new = question_inst.get_question_string()
        assert 'New' == new

        opt = question_inst.get_option_objects()
        assert isinstance(opt, OptionList) == True

        qid = question_inst.get_question_id()
        assert qid not in self.unique_question_ids
        self.unique_question_ids.append(qid)

        question_inst.set_previously_answered_values(opt)
        stored_opt = question_inst.get_option_objects()
        assert id(stored_opt) == id(opt)
