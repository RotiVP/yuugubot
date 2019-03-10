#! /bin/python

# use -h for help
#
# example:
# add_entry where 'Где Шицелов?' teacher
#
# NOTE: not all contexts and intents are processed by the application

from sys import exit
import argparse
import os
from json import load, dump
from gensim.utils import simple_preprocess as convert

parser = argparse.ArgumentParser()
parser.add_argument('intent', type=str)
parser.add_argument('example', type=str)
parser.add_argument('context', type=str)
#parser.add_argument('-t', dest='is_template', action='store_const', const=True, default=False, help='entry is the template')
arg_ns = parser.parse_args()

dataf = 'dictionary.json'

data = []
if os.path.isfile(dataf) and os.path.getsize(dataf) > 0:
    with open('dictionary.json', 'r') as f:
        try:
            data = load(f)
        except JSONDecodeError:
            print('Invalid data file')
            sys.exit(1)

for entry in data:
    if 'example' not in entry:
        print('Invalid entry object')
        exit(1)
    if convert(entry['example']) == convert(arg_ns.example):
        print('Object already exists')
        exit(1)

data.append({'example': arg_ns.example, 'context': arg_ns.context, 'intent': arg_ns.intent})#, 'template': arg_ns.is_template})

with open('dictionary.json', 'w') as f:
    dump(data, f, indent=2)

print('Done')
exit(0)
