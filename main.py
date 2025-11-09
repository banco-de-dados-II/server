import os
import json

from flask import render_template, request, redirect, url_for, send_file, g, session
from markupsafe import escape
from globals import *

import db

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

@app.get('/tarefas/')
def tarefas_get():
    u = usuario()
    if not u:
        return redirect(url_for('index'))

    with db.TarefaPessoa.procurar('tarefa_id', pessoa_id=u.id) as cur:
        tarefa_ids = cur.fetchall()

    if len(tarefa_ids) == 0:
        return render_template(
            'tarefas.html',
            tarefas=[],
        )

    stmt = f'select status, titulo from tarefas where id in ({','.join(str(tarefa_id[0]) for tarefa_id in tarefa_ids)})'
    cur = g.db.cursor(dictionary=True)
    cur.execute(stmt)
    tarefas = cur.fetchall()
    return render_template(
        'tarefas.html',
        tarefas=tarefas,
    )

@app.get('/perfil/')
def perfil_get():
    u = usuario()
    if not u:
        return redirect(url_for('index'))

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
