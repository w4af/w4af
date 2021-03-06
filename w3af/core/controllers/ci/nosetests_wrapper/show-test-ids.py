#!/usr/bin/env python



import os
import sys
import pickle

# Need this hack in order to be able to re-add the current path to the
# python-path, since running a script seems to change it (?)
sys.path.insert(0, os.path.abspath(os.curdir))

from w3af.core.controllers.ci.nosetests_wrapper.utils.test_stats import get_test_ids
from w3af.core.controllers.ci.nosetests_wrapper.constants import ID_FILE, NOSE_RUN_SELECTOR


def nose_strategy():
    """
    :return: A list with the nosetests commands to run.
    """
    # This will generate the ID_FILE
    get_test_ids(NOSE_RUN_SELECTOR)
    with open(ID_FILE) as id_fh:
        nose_data = pickle.load(id_fh)

        for key, value in nose_data['ids'].items():
            _, _, test_class_method = value
            print('%s:%s' % (key, test_class_method))


if __name__ == '__main__':
    nose_strategy()
