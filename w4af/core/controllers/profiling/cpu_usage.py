"""
cpu_usage.py

Copyright 2012 Andres Riancho

This file is part of w4af, http://w4af.net/ .

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
import yappi

from .utils import get_filename_fmt, dump_data_every_thread, cancel_thread


PROFILING_OUTPUT_FMT = '/tmp/w4af-%s-%s.cpu'
DELAY_MINUTES = 2
SAVE_THREAD_PTR = []


def user_wants_cpu_profiling():
    _should_profile = os.environ.get('w4af_CPU_PROFILING', '0')

    if _should_profile.isdigit() and int(_should_profile) == 1:
        return True

    return False


def should_profile_cpu(wrapped):
    def inner():
        if user_wants_cpu_profiling():
            return wrapped()

    return inner


@should_profile_cpu
def start_cpu_profiling():
    """
    If the environment variable w4af_PROFILING is set to 1, then we start
    the CPU and memory profiling.

    :return: None
    """
    dump_data_every_thread(dump_data, DELAY_MINUTES, SAVE_THREAD_PTR)


def dump_data():
    # pylint: disable=E1101
    yappi.get_func_stats().save(PROFILING_OUTPUT_FMT % get_filename_fmt(),
                                type="pstat")
    # pylint: enable=E1101


@should_profile_cpu
def stop_cpu_profiling():
    """
    Save profiling information (if available)
    """
    cancel_thread(SAVE_THREAD_PTR)
    dump_data()
