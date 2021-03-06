# coding=utf-8
#
# This file is part of Hypothesis, which may be found at
# https://github.com/HypothesisWorks/hypothesis-python
#
# Most of this work is copyright (C) 2013-2017 David R. MacIver
# (david@drmaciver.com), but it contains contributions by others. See
# CONTRIBUTING.rst for a full list of people who may hold copyright, and
# consult the git log if you need to determine who owns an individual
# contribution.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.
#
# END HEADER

from __future__ import division, print_function, absolute_import

from hypothesis.errors import InvalidArgument
from hypothesis.internal import charmap
from hypothesis.internal.compat import hunichr, text_type, binary_type
from hypothesis.internal.intervalsets import IntervalSet
from hypothesis.internal.conjecture.utils import integer_range
from hypothesis.searchstrategy.strategies import SearchStrategy, \
    MappedSearchStrategy


class OneCharStringStrategy(SearchStrategy):

    """A strategy which generates single character strings of text type."""
    specifier = text_type
    zero_point = ord('0')

    def __init__(self,
                 whitelist_categories=None,
                 blacklist_categories=None,
                 blacklist_characters=None,
                 min_codepoint=None,
                 max_codepoint=None,
                 whitelist_characters=None):
        intervals = charmap.query(
            include_categories=whitelist_categories,
            exclude_categories=blacklist_categories,
            min_codepoint=min_codepoint,
            max_codepoint=max_codepoint,
            include_characters=whitelist_characters,
        )
        if not intervals:
            raise InvalidArgument(
                'No valid characters in set'
            )
        self.intervals = IntervalSet(intervals)
        if whitelist_characters:
            self.whitelist_characters = set(whitelist_characters)
        else:
            self.whitelist_characters = set()
        if blacklist_characters:
            self.blacklist_characters = set(
                b for b in blacklist_characters if ord(b) in self.intervals
            )
            if (len(self.whitelist_characters) == 0 and
                    len(self.blacklist_characters) == len(self.intervals)):
                raise InvalidArgument(
                    'No valid characters in set'
                )
        else:
            self.blacklist_characters = set()
        self.zero_point = self.intervals.index_above(ord('0'))

    def do_draw(self, data):
        while True:
            i = integer_range(
                data, 0, len(self.intervals) - 1,
                center=self.zero_point,
            )
            c = hunichr(self.intervals[i])
            if c not in self.blacklist_characters:
                return c


class StringStrategy(MappedSearchStrategy):

    """A strategy for text strings, defined in terms of a strategy for lists of
    single character text strings."""

    def __init__(self, list_of_one_char_strings_strategy):
        super(StringStrategy, self).__init__(
            strategy=list_of_one_char_strings_strategy
        )

    def __repr__(self):
        return 'StringStrategy()'

    def pack(self, ls):
        return u''.join(ls)


class BinaryStringStrategy(MappedSearchStrategy):

    """A strategy for strings of bytes, defined in terms of a strategy for
    lists of bytes."""

    def __repr__(self):
        return 'BinaryStringStrategy()'

    def pack(self, x):
        assert isinstance(x, list), repr(x)
        ba = bytearray(x)
        return binary_type(ba)


class FixedSizeBytes(SearchStrategy):

    def __init__(self, size):
        self.size = size

    def do_draw(self, data):
        return binary_type(data.draw_bytes(self.size))
