from flask import render_template, request, redirect, url_for
from globals import *

from db import Pessoas

@app.route('/')
def index():
    print(db, id(db))
    return render_template('index.html')

@app.get('/login/')
def login_get():
    return render_template('login.html')

@app.get('/tarefas/')
def tarefas_get():
    nome = request.args.get('nome', default='sem nome')
    return render_template('tarefas.html', nome=nome)


@app.post('/login')
def login_post():
    nome = request.form['nome']
    email = request.form['email']
    pessoa = Pessoas(nome=nome, email=email)
    print(pessoa)
    db.session.add(pessoa)
    db.session.commit()

    print(nome, email)
    return redirect(url_for("tarefas_get", nome=nome))

#@app.post('/login/')
#def login():
#    return None
