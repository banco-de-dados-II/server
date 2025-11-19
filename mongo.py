from pydantic import BaseModel, Field
from flask import g, request, session
from datetime import datetime
from time import time

def registrar(info={}):
    logs = g.mdb.get_collection('logs')

    info['url'] = request.path

    if request.method == 'GET':
        info['GET'] = request.args

    if request.method == 'POST':
        info['POST'] = request.form

    usuario = session.get('usuario')
    if usuario:
        info = info | {'usuario': usuario}

    data = datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')
    result = info | {'data': data}

    logs.insert_one(result)
