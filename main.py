import os
import json

from flask import render_template, request, redirect, url_for, send_file, g, session
from markupsafe import escape
from globals import *

import db
import db_gen

def escape_str(s):
    return str(escape(s))

def usuario():
    result = session.get('usuario')

    if not result:
        return None

    return db.Pessoa(**json.loads(result))

@app.context_processor
def injertar_usuario():
    u = usuario()

    if not u:
        return {}

    return u.to_args()

@app.route('/')
def index():
    return render_template('index.html')

@app.get('/login/')
def login_get():
    return render_template('login.html')

@app.get('/perfil/')
def perfil_get():
    u = usuario()
    if not u:
        return redirect(url_for('login_get'))

    return render_template(
        'perfil.html',
        **u.to_args(),
    )

def perfil(u):
    session['usuario'] = u.to_json()
    response = redirect(url_for("perfil_get"))
    return response

@app.post('/login')
def login_post():
    id = escape_str(request.form.get('id'))
    nome = escape_str(request.form.get('nome'))
    email = escape_str(request.form.get('email'))

    if id:
        pargs = db.Pessoa.procurar('*', id=id).fetchone()
    else:
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
        nome=escape_str(request.form['nome']),
        email=escape_str(request.form['email']),
    )

    return perfil(u)

@app.post('/reset')
def rest_post():
    session.pop('usuario')
    db_gen.do(g.db)
    return redirect(request.origin)

@app.get('/tarefas/')
def tarefas_get():
    u = usuario()
    if not u:
        return redirect(url_for('login_get'))

    tarefas = db.call_proc(
        g.db.cursor(dictionary=True),
        'card_da_pessoa',
        u.id,
    )

    print(tarefas)

    return render_template(
        'tarefas.html',
        tarefas=tarefas,
    )

@app.get('/equipes/')
def equipes_get():
    u = usuario()
    if not u:
        return redirect(url_for('login_get'))

    equipes = db.call_proc(
        g.db.cursor(dictionary=True),
        'equipes_da_pessoa',
        u.id,
    )

    print(equipes)

    return render_template(
        'equipes.html',
        equipes=equipes,
    )
