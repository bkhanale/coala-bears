import autopep8
import logging

from bears.python.PycodestyleBear import PycodestyleBear
from coalib.bearlib.spacing.SpacingHelper import SpacingHelper
from coalib.bears.LocalBear import LocalBear
from coalib.results.Diff import Diff
from coalib.results.Result import Result
from coalib.settings.Section import Section
from coalib.settings.Setting import Setting
from coalib.testing.LocalBearTestHelper import execute_bear
from queue import Queue


class PyPEP8Bear(LocalBear):
    """
    Integration of PycodestyleBear and PEP8Bear.
    """
    LANGUAGES = {'Python', 'Python 2', 'Python 3'}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_FIX = {'Formatting'}

    def run(self, filename, file,
            max_line_length: int = 79,
            indent_size: int = SpacingHelper.DEFAULT_TAB_WIDTH,):
        """
        Detects and fixes PEP8 incompliant code. This bear will not change
        functionality of the code in any way.

        :param max_line_length:
            Maximum number of characters for a line.
            When set to 0 allows infinite line length.
        :param indent_size:
            Number of spaces per indentation level.
        """
        if not max_line_length:
            max_line_length = sys.maxsize

        queue = Queue()
        section = Section('')
        section.append(Setting('max_line_length', max_line_length))

        with execute_bear(PycodestyleBear(section, queue),
                          filename, file,) as results:

            for result in results:
                start_line = result.affected_code[0].start.line
                end_line = result.affected_code[0].end.line
                # start_column = result.affected_code[0].start.column
                # end_column = result.affected_code[0].end.column
                rule = result.origin.split(' ')[1][1:-1]

                options = {'select': (rule,),
                           'max_line_length': max_line_length,
                           'indent_size': indent_size,
                           'line_range': [start_line, end_line + 1]}

                corrected = autopep8.fix_code(''.join(file),
                                              apply_config=False,
                                              options=options).splitlines(True)

                diffs = Diff.from_string_arrays(file, corrected).split_diff()

                logging.debug(corrected)

                for diff in diffs:
                    yield Result(self,
                                 result.message,
                                 affected_code=(diff.range(filename),),
                                 diffs={filename: diff})
