# Copyright (c) 2015 - present Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

import os
import logging
import util

MODULE_NAME = __name__
MODULE_DESCRIPTION = '''Run analysis of code built with a command like:
ant [options] [target]

Analysis examples:
infer -- ant compile'''

def gen_instance(*args):
    return AntCapture(*args)

# This creates an empty argparser for the module, which provides only
# description/usage information and no arguments.
create_argparser = util.base_argparser(MODULE_DESCRIPTION, MODULE_NAME)


class AntCapture:

    def __init__(self, args, cmd):
        self.args = args
        util.log_java_version()
        logging.info(util.run_cmd_ignore_fail(['ant', '-version']))
        # TODO: make the extraction of targets smarter
        self.build_cmd = ['ant', '-verbose'] + cmd[1:]

    def is_interesting(self, content):
        return self.is_quoted(content) or content.endswith('.java')

    def is_quoted(self, argument):
        quote = '\''
        return len(argument) > 2 and argument[0] == quote\
            and argument[-1] == quote

    def remove_quotes(self, argument):
        if self.is_quoted(argument):
            return argument[1:-1]
        else:
            return argument

    def get_javac_commands(self, verbose_output):
        javac_pattern = '[javac]'
        argument_start_pattern = 'Compilation arguments'
        javac_arguments = []
        javac_commands = []
        collect = False
        for line in verbose_output:
            if javac_pattern in line:
                if argument_start_pattern in line:
                    collect = True
                    if javac_arguments != []:
                        javac_commands.append(javac_arguments)
                        javac_arguments = []
                if collect:
                    pos = line.index(javac_pattern) + len(javac_pattern)
                    content = line[pos:].strip()
                    if self.is_interesting(content):
                        arg = self.remove_quotes(content)
                        javac_arguments.append(arg)
        if javac_arguments != []:
            javac_commands.append(javac_arguments)
        return javac_commands

    def capture(self):
        return map(util.javac_parse,self.get_javac_commands(util.get_build_output(self.build_cmd)))