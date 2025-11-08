import os
import json

from flask import render_template, request, redirect, url_for, send_file, g
from globals import *

import db

def usuario():
    result = request.cookies.get('usuario')
    if not result:
        return db.Pessoa()
    return db.Pessoa(**json.loads(result))

@app.context_processor
def injertar_usuario():
    return usuario().to_args()

@app.route('/')
def index():
    print(db.Pessoa.count())
    print(db.Pessoa.from_id(1))
    return render_template('index.html')

@app.get('/login/')
def login_get():
    return render_template('login.html')

@app.get('/perfil/')
def perfil_get():
    return render_template(
        'perfil.html',
        **usuario().to_args(),
    )

def perfil(u):
    response = redirect(url_for("perfil_get"))
    response.set_cookie('usuario', u.to_json())
    return response

@app.post('/login')
def login_post():
    nome = request.form['nome']
    email = request.form['email']
    procura = db.Pessoa.procurar('*', nome=nome, email=email)

    pargs = procura.fetchone()
    if pargs:
        u = db.Pessoa(*pargs)
    else:
        u = db.Pessoa.adicionar(nome=nome, email=email)

    return perfil(u)

@app.post('/pessoa-mudar')
def pessoa_mudar_post():
    u = usuario()
    u.mudar(
        nome=request.form['nome'],
        email=request.form['email'],
    )

    return perfil(u)
