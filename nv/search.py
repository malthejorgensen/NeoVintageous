# Copyright (C) 2018 The NeoVintageous Team (NeoVintageous).
#
# This file is part of NeoVintageous.
#
# NeoVintageous is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# NeoVintageous is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NeoVintageous.  If not, see <https://www.gnu.org/licenses/>.

import re

from sublime import IGNORECASE
from sublime import LITERAL

from NeoVintageous.nv.options import get_option
from NeoVintageous.nv.settings import get_setting_neo
from NeoVintageous.nv.ui import ui_region_flags


def clear_search_highlighting(view):
    view.erase_regions('_nv_search_occ')
    view.erase_regions('_nv_search_cur')
    view.erase_regions('_nv_search_inc')


def get_search_occurrences(view):
    return view.get_regions('_nv_search_occ')


def add_search_highlighting(view, occurrences, incremental=None):
    # Incremental search match string highlighting: while typing a search
    # command, where the pattern, as it was typed so far, matches.
    if incremental and get_option(view, 'incsearch'):
        view.add_regions(
            '_nv_search_inc',
            incremental,
            scope='support.function neovintageous_search_inc',
            flags=ui_region_flags(get_setting_neo(view, 'search_inc_style'))
        )

    # Occurrences and current search match string highlighting: when there are
    # search matches, highlight all the matches and the current active one too.
    if occurrences and get_option(view, 'hlsearch'):
        view.add_regions(
            '_nv_search_occ',
            occurrences,
            scope='string neovintageous_search_occ',
            flags=ui_region_flags(get_setting_neo(view, 'search_occ_style'))
        )

        sels = []
        for sel in view.sel():
            if sel.empty():
                sel.b += 1
            sels.append(sel)

        current = []
        for region in occurrences:
            for sel in sels:
                if region.contains(sel):
                    current.append(region)

        if current:
            view.add_regions(
                '_nv_search_cur',
                current,
                scope='support.function neovintageous_search_cur',
                flags=ui_region_flags(get_setting_neo(view, 'search_cur_style'))
            )


def process_search_pattern(view, pattern):
    flags = 0

    if get_option(view, 'ignorecase'):
        flags |= IGNORECASE

    # Changes the special characters that can be used in search patterns.
    is_magic = get_option(view, 'magic')

    # Some characters in the pattern are taken literally. They match with the
    # same character in the text. When preceded with a backslash however, these
    # characters get a special meaning. See :help magic for more details.
    #
    # Patterns can be prefixed by a "mode" that overrides the 'magic' option:
    #
    #   \m    'magic' on for the following chars in the pattern.
    #   \M    'magic' off for the following chars in the pattern.
    #   \v    the following chars in the pattern are "very magic".
    #   \V    the following chars int the pattern are "very nomagic".
    mode = None
    match = re.match('^\\\\(m|M|v|V)(.*)$', pattern)
    if match:
        mode = match.group(1)
        pattern = match.group(2)

    def _process_magic(pattern, flags):
        # When magic is on some characters in a pattern are interpreted
        # literally depending on context. For example [0-9 is interpreted
        # literally and [0-9] is interpreted as a regular expression.
        # XXX The following is a quick and dirty implementation to support some
        # very basic 'magic' literal interpretations.
        if pattern:
            if re.match('^[a-zA-Z0-9_\'"\\[\\]]+$', pattern):
                if '[' not in pattern or ']' not in pattern:
                    flags |= LITERAL

            elif re.match('^[a-zA-Z0-9_\'"\\(\\)]+$', pattern):
                if '(' not in pattern or ')' not in pattern:
                    flags |= LITERAL

        return pattern, flags

    # magic
    if mode == 'm' or (is_magic and not mode):
        pattern, flags = _process_magic(pattern, flags)

    # very magic
    elif mode == 'v':
        pattern, flags = _process_magic(pattern, flags)

    # nomagic
    elif mode == 'M' or (not is_magic and not mode):
        flags |= LITERAL

    # very nomagic
    elif mode == 'V':
        flags |= LITERAL

    return pattern, flags


def calculate_word_search_flags(view, pattern):
    flags = 0

    if get_option(view, 'ignorecase'):
        flags |= IGNORECASE

    return flags


def create_word_search_pattern(view, pattern):
    return r'\b{0}\b'.format(re.escape(pattern))


def find_all_buffer_search_occurrences(view, pattern, flags):
    return view.find_all(pattern, flags)


def find_all_word_search_occurrences(view, pattern):
    return view.find_all(
        create_word_search_pattern(view, pattern),
        calculate_word_search_flags(view, pattern)
    )
