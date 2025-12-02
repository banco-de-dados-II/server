"""
para debug apenas

python -i mongo-repl.py
>>> dump_last(tags)
"""

import pymongo
import bson
from pprint import pprint as pp

def _dump(doc):
    return [d for d in doc.find()]

def dump_last(doc, n=3):
    for d in _dump(doc)[-n:]:
        pp(d)

mdb = pymongo.MongoClient('mongodb://root:root@localhost:27017')
bd2 = mdb['db2']
logs = bd2['logs']
tags = bd2['tags']
