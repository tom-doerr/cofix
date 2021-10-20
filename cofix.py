#!/usr/bin/env python3

'''
This script automatically fixes bugs in programs.
It does this by taking the command to execute as an argument and
analyzing the traceback after executing the command.
Then the script uses OpenAI's Codex to fix the line that causes
the bug.
'''

import sys
import os
import subprocess
import json
import re
import pickle
import time
import random
from AUTH import *
import openai
import difflib

# The maximum number of times to try to fix a bug
MAX_FIX_TRIES = 10

FIX_PROMPT = (
        '# The above line throws the following exception:',
        '# Line that does not throw the error:'
        )

openai.organization = ORGANIZATION_ID
openai.api_key = SECRET_KEY

def assemble_prompt(lines_until_buggy_line, traceback, fix_prompt):
    prompt_lines = lines_until_buggy_line
    prompt_lines.append(fix_prompt[0])
    prompt_lines.append( '# "' + traceback.split('\n')[-2] + '"') 
    prompt_lines.append(fix_prompt[1])
    prompt = '\n'.join(prompt_lines)
    prompt += '\n'
    return prompt


def get_traceback(program):
    traceback = None

    # Run the program and capture its output
    with open(os.devnull, 'w') as devnull:
        try:
            # Get the stderr and the stdout of the program program.
            stderr = subprocess.check_output(program,  stderr=subprocess.STDOUT, shell=True).decode('utf-8')
        except subprocess.CalledProcessError as e:
            error_message_line = e.output.decode('utf-8').split('\n')[-2]
            traceback =  e.output.decode('utf-8')
            print("error_message_line:", error_message_line)
            print("traceback:", traceback)

    return traceback



def get_filename(traceback):
    # Get the line number from the traceback
    match = re.search(r'File \"(.*?)\", line ([0-9]+)', traceback)
    if not match:
        print('Could not find line number, exiting')
        sys.exit(1)

    filename = match.group(1)
    return filename


def get_source_code(filename):
    # Read the whole program code.
    with open(filename, 'r') as f:
        code = f.read()

    return code


def get_fixed_code(code, traceback, level):


    # Get all the line numbers in the traceback.
    line_numbers = []
    for line in traceback.split('\n'):
        match = re.search(r'File \"(.*?)\", line ([0-9]+)', line)
        if match:
            line_numbers.append(int(match.group(2)))


    line_number = line_numbers[level]



    lines_until_buggy_line  = code.split('\n')[:line_number]
    print("lines_until_buggy_line:", lines_until_buggy_line)
    prompt = assemble_prompt(lines_until_buggy_line, traceback, FIX_PROMPT)
    input_prompt = prompt
    print("input_prompt:", input_prompt)


    # Create prompt that surrounds the buggy line with text indicating that this is
    # the line that should be fixed.

    response = openai.Completion.create(engine='davinci-codex', prompt=input_prompt, temperature=0.5, max_tokens=64, stop='\n')
    fixed_line = response['choices'][0]['text']

    fixed_code = replace_faulty_line(code, fixed_line, line_number)

    # Visualize diff between original code and fixed_code with color.
    # The inserted words are colored green, the delted parts red.
    # The rest is black.
    d = difflib.Differ()
    diff = d.compare(lines_until_buggy_line, fixed_code.split('\n')[:len(lines_until_buggy_line)])
    colored_diff = []
    for line in diff:
        if line[0] == '+':
            colored_diff.append('\033[92m' + line + '\033[0m')
        elif line[0] == '-':
            colored_diff.append('\033[91m' + line + '\033[0m')
        else:
            colored_diff.append(line)

    print('\n'.join(colored_diff))

    return fixed_code

def replace_faulty_line(code, fixed_line, line_number):
    lines = code.split('\n')
    lines[line_number-1] = fixed_line
    return '\n'.join(lines)


def main(argv):
    if len(argv) != 2:
        print('Usage: %s <program>' % argv[0])
        sys.exit(1)

    program = argv[1]

    # Example response:
# response: {
  # "choices": [
    # {
      # "finish_reason": "length",
      # "index": 0,
      # "logprobs": null,
      # "text": "import pytz\n\ntimezones = ['America/New_York', 'America/Detroit', 'America/Kentucky/Louisville', 'America/Kentucky/Monticello', 'America/Indiana/Indianapolis', 'America/Indiana/Vincennes', 'America/Indiana/Win"
    # }
  # ],
  # "created": 1634710889,
  # "id": "cmpl-3uzGbX4bOreMWVHEWENPYXhgAA9W3",
  # "model": "davinci-codex:2021-08-03",
  # "object": "text_completion"
# }

    

    # Try to fix the bug
    for i in range(MAX_FIX_TRIES):

        traceback = get_traceback(program)


        # If the program didn't crash, exit
        if i == 0 and not traceback:
            print('No traceback, exiting')
            sys.exit(0)

        # If it didn't crash, exit
        elif i > 0 and not traceback:
            print('Successfully fixed bug')
            sys.exit(0)

        filename = get_filename(traceback)

        if i > 0:
            code = original_code
            traceback = original_traceback
        else:
            original_code = get_source_code(filename)
            code = original_code
            original_traceback = traceback

        print('Trying to fix bug (try %d of %d)' % (i+1, MAX_FIX_TRIES))

        # Get the correct code for the line
        fixed_code = get_fixed_code(code, traceback, i)
        print("fixed_code:", fixed_code)

        # Write the code to the file
        with open(filename, 'w') as f:
            f.write(fixed_code)

        input()


    print('Failed to fix bug')

if __name__ == '__main__':
    main(sys.argv)


