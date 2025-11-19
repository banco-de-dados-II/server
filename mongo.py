from pymongo import ReturnDocument
from pydantic import BaseModel, Field
from flask import g, request, session
from datetime import datetime
from time import time
from bson.objectid import ObjectId

import json

def registrar(info={}):
    logs = g.mdb.get_collection('logs')

    info['url'] = request.path

    if request.method == 'GET':
        info['GET'] = request.args

    if request.method == 'POST':
        info['POST'] = request.form

    usuario = session.get('usuario')
    if usuario:
        info['usuario'] =  json.loads(usuario)

    info['data'] = datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')

    logs.insert_one(info)

def tag_update(filter, l):
    tags = g.mdb.get_collection('tags')
    return str(tags.find_one_and_update(
        filter,
        {'$set': {'tags': l}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )['_id'])

def tag_search(id):
    tags = g.mdb.get_collection('tags')
    return tags.find_one({'_id': Objectid(id)})
