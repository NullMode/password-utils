#!/usr/bin/env python
""" This script takes input wordlists, manipulates them, then outputs new
    wordlists with changes.
    Best results are from wordlists containing multiple words that are spaced.
    Output is bested to be sorted and uniqued outside of this script.
"""

""" TODO
    -Optimize smart function so it requires minimal sorting
    -stdin
"""

import argparse
import re
import sys
import os

# Allow piping from python script
try:
    from signal import signal, SIGPIPE, SIG_DFL
    signal(SIGPIPE,SIG_DFL)
except:
    print "Error importing pipe related imports."

# Constants
ONE_FILE  = ""
ONE_FILE_CHECK = False
OVERWRITE = False
STDOUT    = False

# Core class
class Manipulate:
    global args
    global ONE_FILE
    global OVERWRITE
    global STDOUT
    global ONE_FILE_CHECK

    def __init__(self, input_file_name, file_name_append, option):
        self.input_file_name = input_file_name
        self.file_name_append = file_name_append
        self.option = option
        self.output_file_name = self.new_file_name(self.input_file_name, self.file_name_append)
        self.input_file = ''
        self.output_file = ''
        self.overwrite = OVERWRITE
        self.stdout = STDOUT
        self.one_file = ONE_FILE
        self.one_file_check = ONE_FILE_CHECK

    def run(self):
        if self.one_file:
            self.output_file_name = self.one_file
        self.open_files()
        self.logic()
        self.close_files()

    # Classes must override this to add logic
    def logic():
        pass

    def open_files(self):
        # If output file exists, error
        if os.path.isfile(self.output_file_name):
            if not self.overwrite:
                file_exists_error(self.output_file_name)

        self.input_file = open(self.input_file_name, 'r')

        # If outputting to one file
        if self.one_file:
            if not self.one_file_check:
                if os.path.isfile(self.output_file_name):
                    msg("Removing found output file")
                    os.remove(self.output_file_name)

                global ONE_FILE_CHECK
                ONE_FILE_CHECK = True

            if not self.stdout:
                print 'Creating "' + self.output_file_name + '" from "' + self.input_file_name + '"'
                self.output_file = open(self.output_file_name, 'a')

        # If outputting to individual files
        else:
            self.input_file = open(self.input_file_name, 'r')
            if not self.stdout:
                print 'Creating "' + self.output_file_name + '" from "' + self.input_file_name + '"'
                self.output_file = open(self.output_file_name, 'w')

    def output_string(self, string):
        if STDOUT:
            sys.stdout.write(string)
        else:
            self.output_file.write(string)

    def close_files(self):
        self.input_file.close()
        if not self.stdout:
            self.output_file.close()

    def new_file_name(self, input, append):
        split = input.split('.')
        extention = split[len(split) - 1]
        split.pop(len(split) - 1)
        return ''.join(split) + append + '.' + extention

# Mutations
class Capitalise(Manipulate):
    def logic(self):
        for i in self.input_file:
            o = i.split(' ')
            str = ''
            for s in o:
                s = s.replace('\n', '')
                if str is '':
                    str = s.capitalize()
                else:
                    str = str + ' ' + s.capitalize()
            self.output_string(str + '\n')

class RemoveThe(Manipulate):
    def logic(self):
        rgx = re.compile('the|The|THE')
        for i in self.input_file:
            self.output_string(rgx.sub('', i))

class ReverseSpacedWords(Manipulate):
    def logic(self):
        for i in self.input_file:
            r = i.rstrip().split(' ')
            r.reverse()
            first = True
            for m in r:
                if first:
                    first = False
                    str = m
                else:
                    str = str + ' ' + m
            self.output_string(str + '\n')

class StripNonAlpha(Manipulate):
    def logic(self):
        for i in self.input_file:
            self.output_string("".join(p for p in list(i) if 64<ord(p)<91 or 64<ord(p)<123 or ord(p)==32) + '\n')
class StripSpaces(Manipulate):
    def logic(self):
        for i in self.input_file:
            self.output_string(i.replace(' ', ''))

class StripSpecific(Manipulate):
    def logic(self):
        rgx = re.compile('[%s]' % self.option)
        for i in self.input_file:
            self.output_string(rgx.sub('', i))

class ToLowerCase(Manipulate):
    def logic(self):
        for i in self.input_file:
            self.output_string(i.lower())

class ToUpperCase(Manipulate):
    def logic(self):
        for i in self.input_file:
            self.output_string(i.upper())

# Core functions
def error(text):
    print '[!] ' + text
    exit(1)

def file_exists_error(filename):
    error('File "' + filename + '" exists, use option --overwrite to overwrite')

def msg(text):
    print '[*] ' + text

def process_args():
    global args

    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Input file to manipulate")
    parser.add_argument("-a", "--all", help="Run all modules to create output", action="store_true")
    parser.add_argument("-c", "--capitalise", help="Capitalise each word", action="store_true" )
    parser.add_argument("-l", "--lower-case", help="Change all to lower case", action="store_true")
    parser.add_argument("-o", "--overwrite", help="Select this option to force overwriting", action="store_true")
    parser.add_argument("-of", "--one-file", help="Output mutated list to this file only")
    parser.add_argument("-r", "--reverse", help="Reverse words that are spaced", action="store_true")
    parser.add_argument("-sm", "--smart", help="Does a combination of all the lists", action="store_true")
    parser.add_argument("-ss", "--strip-spaces", help="Remove spaces from list", action="store_true")
    parser.add_argument("-sp", "--strip-specific", help="List of chars to strip from the list", action="store_true")
    parser.add_argument("-so", "--stdout", help="Output to stdout rather than files.", action="store_true")
    parser.add_argument("-sy", "--strip-non-alpha", help="Strip all non-ascii characters (not space)", action="store_true")
    parser.add_argument("-t", "--the", help="Remove the word the (all instances)", action="store_true")
    parser.add_argument("-u", "--upper-case", help="Change all to upper case", action="store_true")

    args = parser.parse_args()

    # Check for errors
    if (args.overwrite or args.one_file) and args.stdout:
        error('You cannot mix "overwrite" or "one file" options with the "stdout" option.')

    if args.smart and args.one_file:
        error('You cannot use "smart" and "one file" at the same time as the smart function ' \
            + 'depends on files being created.')

    if args.smart and args.all:
            error('You can\'t run "smart" or "all" options at the same time.')

    # Set constants
    if args.overwrite:
        set_overwrite()

    if args.stdout:
        set_stdout()

    if args.one_file:
        set_output_one_file(args.one_file)

    # The smart options has it's own function
    if args.smart:
        smart()

    # Run all put the specific manipulcation
    elif args.all:
        StripSpaces(args.file, "-no-spaces", args.strip_spaces).run()
        Capitalise(args.file, "-capitalised-word", args.capitalise).run()
        ToLowerCase(args.file, "-lowercase", args.lower_case).run()
        ReverseSpacedWords(args.file, "-reversed", args.reverse).run()
        msg('Omitting strip specific manipulation.')
        StripNonAlpha(args.file, "-alpha-space-only", args.strip_non_alpha).run()
        RemoveThe(args.file, "-no-the", args.the).run()
        ToUpperCase(args.file, "-uppercase", args.upper_case).run()

    # If smart or all not selected run each option
    else:
        if args.strip_spaces:
            StripSpaces(args.file, "-no-spaces", args.strip_spaces).run()
        if args.capitalise:
            Capitalise(args.file, "-capitalised-word", args.capitalise).run()
        if args.lower_case:
            ToLowerCase(args.file, "-lowercase", args.lower_case).run()
        if args.reverse:
            ReverseSpacedWords(args.file, "-reversed", args.reverse).run()
        if args.strip_specific:
            StripSpecific(args.file, "-stripped", args.strip_specific).run()
        if args.strip_non_alpha:
            StripNonAlpha(args.file, "-alpha-space-only", args.strip_non_alpha).run()
        if args.the:
            RemoveThe(args.file, "-no-the", args.the).run()
        if args.upper_case:
            ToUpperCase(args.file, "-uppercase", args.upper_case).run()

def set_overwrite():
    global OVERWRITE
    OVERWRITE = True

def set_output_one_file(filename):
    global ONE_FILE
    ONE_FILE = filename
    msg('"One File" option selected. All output will be saved to ' + filename)

def set_stdout():
    global STDOUT
    STDOUT = True

def smart():
    # go through most of the options, some recursive to produce a larger,
    # more unique list

    global args

    seed = StripSpaces(args.file, "-no-spaces", args.strip_spaces)
    seed.run()
    Capitalise(seed.output_file_name, "-capitalised-word", args.capitalise).run()
    ToLowerCase(seed.output_file_name, "-lowercase", args.lower_case).run()
    ReverseSpacedWords(seed.output_file_name, "-reversed", args.reverse).run()
    StripNonAlpha(seed.output_file_name, "-alpha-space-only", args.strip_non_alpha).run()
    RemoveThe(seed.output_file_name, "-no-the", args.the).run()
    ToUpperCase(seed.output_file_name, "-uppercase", args.upper_case).run()

    seed = Capitalise(args.file, "-capitalised-word", args.capitalise)
    seed.run()
    StripSpaces(seed.output_file_name, "-no-spaces", args.strip_spaces).run()
    ToLowerCase(seed.output_file_name, "-lowercase", args.lower_case).run()
    ReverseSpacedWords(seed.output_file_name, "-reversed", args.reverse).run()
    StripNonAlpha(seed.output_file_name, "-alpha-space-only", args.strip_non_alpha).run()
    RemoveThe(seed.output_file_name, "-no-the", args.the).run()
    ToUpperCase(seed.output_file_name, "-uppercase", args.upper_case).run()

    seed = ToLowerCase(args.file, "-lowercase", args.lower_case)
    seed.run()
    StripSpaces(seed.output_file_name, "-no-spaces", args.strip_spaces).run()
    Capitalise(seed.output_file_name, "-capitalised-word", args.capitalise).run()
    ReverseSpacedWords(seed.output_file_name, "-reversed", args.reverse).run()
    StripNonAlpha(seed.output_file_name, "-alpha-space-only", args.strip_non_alpha).run()
    RemoveThe(seed.output_file_name, "-no-the", args.the).run()
    ToUpperCase(seed.output_file_name, "-uppercase", args.upper_case).run()

    seed = ReverseSpacedWords(args.file, "-reversed", args.reverse)
    seed.run()
    StripSpaces(seed.output_file_name, "-no-spaces", args.strip_spaces).run()
    Capitalise(seed.output_file_name, "-capitalised-word", args.capitalise).run()
    ToLowerCase(seed.output_file_name, "-lowercase", args.lower_case).run()
    StripNonAlpha(seed.output_file_name, "-alpha-space-only", args.strip_non_alpha).run()
    RemoveThe(seed.output_file_name, "-no-the", args.the).run()
    ToUpperCase(seed.output_file_name, "-uppercase", args.upper_case).run()

    seed = StripNonAlpha(args.file, "-alpha-space-only", args.strip_non_alpha)
    seed.run()
    StripSpaces(seed.output_file_name, "-no-spaces", args.strip_spaces).run()
    Capitalise(seed.output_file_name, "-capitalised-word", args.capitalise).run()
    ToLowerCase(seed.output_file_name, "-lowercase", args.lower_case).run()
    ReverseSpacedWords(seed.output_file_name, "-reversed", args.reverse).run()
    RemoveThe(seed.output_file_name, "-no-the", args.the).run()
    ToUpperCase(seed.output_file_name, "-uppercase", args.upper_case).run()

    seed = RemoveThe(args.file, "-no-the", args.the)
    seed.run()
    StripSpaces(seed.output_file_name, "-no-spaces", args.strip_spaces).run()
    Capitalise(seed.output_file_name, "-capitalised-word", args.capitalise).run()
    ToLowerCase(seed.output_file_name, "-lowercase", args.lower_case).run()
    ReverseSpacedWords(seed.output_file_name, "-reversed", args.reverse).run()
    StripNonAlpha(seed.output_file_name, "-alpha-space-only", args.strip_non_alpha).run()
    ToUpperCase(seed.output_file_name, "-uppercase", args.upper_case).run()

    seed = ToUpperCase(args.file, "-uppercase", args.upper_case)
    seed.run()
    StripSpaces(seed.output_file_name, "-no-spaces", args.strip_spaces).run()
    Capitalise(seed.output_file_name, "-capitalised-word", args.capitalise).run()
    ToLowerCase(seed.output_file_name, "-lowercase", args.lower_case).run()
    ReverseSpacedWords(seed.output_file_name, "-reversed", args.reverse).run()
    StripNonAlpha(seed.output_file_name, "-alpha-space-only", args.strip_non_alpha).run()
    RemoveThe(seed.output_file_name, "-no-the", args.the).run()

if __name__ == "__main__":
    process_args()
