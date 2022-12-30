"""
utils.py

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
import random

from string import ascii_letters, digits


LETTERS_DIGITS = ascii_letters + digits


def get_random_instance(seed):
    if seed is None:
        return random.Random()

    rnd = random.Random()
    rnd.seed(seed)
    return rnd


def rand_alpha(length=0, seed=None):
    """
    Create a random string ONLY with letters

    :return: A random string only composed by letters.
    """
    rnd = get_random_instance(seed)
    length = length or rnd.randint(10, 30)

    return ''.join(rnd.choice(ascii_letters) for _ in range(length))


def rand_alnum(length=0, seed=None):
    """
    Create a random string with random length

    :return: A random string of with length > 10 and length < 30.
    """
    rnd = get_random_instance(seed)
    length = length or rnd.randint(10, 30)

    return ''.join(rnd.choice(LETTERS_DIGITS) for _ in range(length))


def rand_number(length=0, exclude_numbers=(), seed=None):
    """
    Create a random string ONLY with numbers

    :return: A random string only composed by numbers.
    """
    rnd = get_random_instance(seed)
    length = length or rnd.randint(10, 30)

    _digits = digits[:]
    for excluded_number in set(exclude_numbers):
        _digits = _digits.replace(str(excluded_number), '')

    if not _digits:
        raise ValueError('Failed return random number')

    ru = ''.join(rnd.choice(_digits) for _ in range(length))
    return ru


def create_format_string(length):
    """
    :return: A string with $length %s and a final %n
    """
    result = '%n' * length
    return result
