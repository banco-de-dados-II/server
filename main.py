import os
import json

from flask import render_template, request, redirect, url_for, send_file, g
from globals import *

import db

def usuario():
    return db.Pessoa(**json.loads(request.cookies['usuario']))

@app.context_processor
def injertar_usuario():
    return usuario().to_args()

@app.route('/')
def index():
    print(g.db, id(g.db))
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
    pessoas = db.Pessoa.procurar(nome=nome, email=email)

    if len(pessoas) == 0:
        u = db.Pessoa.adicionar(nome=nome, email=email)
    else:
        u = pessoas[0]

    return perfil(u)

@app.post('/pessoa-mudar')
def pessoa_mudar_post():
    u = usuario()
    u.mudar(
        nome=request.form['nome'],
        email=request.form['email'],
    )

    return perfil(u)
