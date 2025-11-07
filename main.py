import os

from flask import render_template, request, redirect, url_for, send_file, g
from globals import *

import db

@app.route('/')
def index():
    print(g.db, id(g.db))
    return render_template('index.html')

@app.get('/login/')
def login_get():
    return render_template('login.html')

@app.get('/perfil/')
def perfil_get():
    nome = request.args.get('nome', default='sem nome')
    email = request.args.get('email', default='sem email')
    return render_template('perfil.html', nome=nome, email=email)


@app.post('/login')
def login_post():
    nome = request.form['nome']
    email = request.form['email']

    pessoas = db.pessoa_procurar(nome)
    if len(pessoas) == 0:
        assert db.pessoa_adicionar(nome, email) > 0

    response = redirect(url_for("perfil_get", nome=nome, email=email))
    response.set_cookie('nome', nome)
    return response

@app.post('/pessoa-mudar')
def pessoa_mudar_post():
    nome = request.form['nome']
    email = request.form['email']

    db.pessoa_mudar(request.cookies['nome'], nome, email)

    response = redirect(url_for("perfil_get", nome=nome, email=email))
    response.set_cookie('nome', nome)
    return response
