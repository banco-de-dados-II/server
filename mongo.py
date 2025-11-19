from pydantic import BaseModel, Field
from flask import g, request, session
from datetime import datetime
from time import time

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
