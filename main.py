import os
import json

from flask import render_template, request, redirect, url_for, send_file, g, session
from markupsafe import escape
from datetime import datetime
from time import time

from globals import *
import db
import db_gen

import mongo

def escape_str(s):
    if s is None or len(s) == 0:
        return None
    return str(escape(s))

def form_get(key):
    return escape_str(request.form.get(key, None))

def usuario():
    result = session.get('usuario')

    if not result:
        return None

    return db.Pessoa(**json.loads(result))

def tempo():
    return datetime.fromtimestamp(time()).strftime("%Y-%m-%d")

def get_param_int(name, default):
    result = request.args.get(name)

    if result:
        result = int(result)
    else:
        result = default

    return result


@app.context_processor
def injertar_usuario():
    u = usuario()

    if not u:
        return {}

    return u.to_args()

tarefa_status = ['a-fazer', 'em-andamento', 'concluido']

@app.context_processor
def injertar_tarefa_status():
    return {'tarefa_status': tarefa_status}

@app.get('/')
def index():
    mongo.registrar()
    return render_template('index.html', rota='index')

@app.get('/login/')
def login_get():
    mongo.registrar()
    return render_template('login.html', rota='login')

@app.get('/perfil/')
def perfil_get():

    u = usuario()
    if not u:
        mongo.registrar({'redirecionar': 'login_get'})
        return redirect(url_for('login_get'))

    mongo.registrar({'renderisar': 'perfil.html'})
    return render_template(
        'perfil.html',
        rota='perfil'
    )

def perfil(u):
    session['usuario'] = u.to_json()
    response = redirect(url_for("perfil_get"))
    return response

@app.post('/login')
def login_post():
    id = form_get('id')
    nome = form_get('nome')
    email = form_get('email')

    reg = {}

    if id:
        pargs = db.Pessoa.procurar('*', id=id).fetchone()
    else:
        procura = db.Pessoa.procurar('*', nome=nome, email=email)
        pargs = procura.fetchone()

    if pargs:
        u = db.Pessoa(*pargs)
    else:
        u = db.Pessoa.adicionar(nome=nome, email=email)

    mongo.registrar({'redirecionar': 'perfil_get', 'adicionar': bool(pargs)})
    return perfil(u)

@app.get('/tarefas/')
@app.get('/tarefas/<int:id>')
def tarefas_get(id=None):
    pagina = get_param_int('pagina', 0)
    max = get_param_int('max', 10)

    u = usuario()
    if not u:
        mongo.registrar({'redirecionar': 'login_get'})
        return redirect(url_for('login_get'))

    if id:
        mongo.registrar({'renderisar': 'tarefa.html'})

        with g.db.cursor(dictionary=True, buffered=True) as cur:
            cur.execute('select * from card where id = %s', (id, ))
            return render_template(
                'tarefa.html', tarefa=cur.fetchone(), rota='tarefa')

    with g.db.cursor(dictionary=True, buffered=True) as cur:
        tarefas = db.call_proc(cur, 'card_da_pessoa', u.id, pagina * max, max)

    mongo.registrar({'renderisar': 'tarefas.html'})
    return render_template(
        'tarefas.html',
        tarefas=tarefas,
        rota='tarefas',
        lista_pagina=pagina,
        lista_max=max,
    )

@app.post('/tarefas/substituir')
def tarefas_substituir_post():
    id = form_get('id')
    titulo = form_get('titulo')
    tag = form_get('tag')
    fazendo = form_get('fazendo') or 'NULL'
    conclusao = form_get('conclusao') or 'NULL'
    limite = form_get('limite') or 'NULL'
    status = form_get('status')

    reg = {}

    with g.db.cursor(buffered=True) as cur:
        if not id:
            reg['modo'] = 'criar'
            u = usuario()
            criacao = tempo()
            cur.execute('call create_card(%s, %s, %s, %s, %s, %s, %s, %s)',
                        (titulo, 'criador', criacao, None, None, None, status, u.id))
            g.db.commit()
            id = cur.lastrowid
        else:
            reg['modo'] = 'substituir'
            cur.execute('call update_card(%s, %s, %s, %s, %s, %s, %s)',
                        (int(id), titulo, tag, fazendo, conclusao, limite, status))
            g.db.commit()

    reg['redirecionar'] = 'terafas_get'
    mongo.registrar(reg)
    return redirect(url_for('tarefas_get', id=id))


@app.get('/equipes')
@app.get('/equipes/<int:id>')
def equipes_get(id=None):
    pagina = get_param_int('pagina', 0)
    max = get_param_int('max', 10)

    u = usuario()
    if not u:
        mongo.registrar({'redirecionar': 'login_get'})
        return redirect(url_for('login_get'))

    if id:
        mongo.registrar({'renderisar': 'equipe.html'})
        with g.db.cursor(dictionary=True, buffered=True) as cur:
            cur.execute('select id, nome, tag from equipes inner join equipes_has_pessoas on equipe_id = id where id = %s', (id,))
            return render_template('equipe.html', equipe=cur.fetchone(), rota='equipe')

    equipes = db.call_proc(
        g.db.cursor(dictionary=True),
        'equipes_da_pessoa',
        u.id,
        pagina * max,
        max,
    )

    mongo.registrar({'renderisar': 'equipes.html'})
    return render_template(
        'equipes.html',
        equipes=equipes,
        rota='equipes',
        lista_pagina=pagina,
        lista_max=max,
    )

@app.post('/equipes/substituir')
def equipes_post():
    u = usuario()
    id = form_get('id')
    nome = form_get('nome')
    tag = form_get('tag')

    with g.db.cursor(buffered=True) as cur:
        cur.execute('update equipes set nome = %s where id = %s', (nome, id))
        cur.execute('update equipes_has_pessoas set tag = %s where equipe_id = %s and pessoa_id = %s', (tag, id, u.id))
        g.db.commit()

    mongo.registrar({'redirecionar': 'equipes_get'})
    return redirect(url_for('equipes_get', id=id))

@app.post('/equipes/criar')
def equipes_criar_post():
    u = usuario()
    nome = form_get('nome')

    id: int
    with g.db.cursor(buffered=True) as cur:
        cur.execute('insert into equipes (nome) value (%s)', (nome,))
        g.db.commit()
        id = cur.lastrowid
        cur.execute('insert into equipes_has_pessoas (equipe_id, pessoa_id, tag) value (%s, %s, "criador")', (id, u.id))
        g.db.commit()

    mongo.registrar({'redirecionar': 'equipes_get'})
    return redirect(url_for('equipes_get', id=id))

@app.post('/equipes/sair')
def equipes_sair_post():
    u = usuario()
    if not u:
        return redirect(url_for('login_get'))
    id = form_get('id')

    with g.db.cursor(buffered=True) as cur:
        cur.execute('delete from equipes_has_pessoas where equipe_id = %s and pessoa_id = %s', (id, u.id))

    g.db.commit()

    mongo.registrar({'redirecionar': 'equipes_get'})
    return redirect(url_for('equipes_get'))

@app.post('/equipes/nova-pessoa')
def equipes_nova_pessoa():
    equipe_id = int(form_get('id'))
    nome = form_get('nome')
    tag = form_get('tag')

    with g.db.cursor(dictionary=True, buffered=True) as cur:
        pessoa_id = db.Pessoa.procurar('id', nome=nome).fetchone()[0]

        print(equipe_id, pessoa_id, tag)

        cur.execute(
            'call equipe_adicionar_pessoa (%s, %s, %s)',
            equipe_id, pessoa_id, tag,
        )

        g.db.commit()

        mongo.registrar({'redirecionar': 'equipes_get'})
        return redirect(url_for('equipes_get', id=equipe_id))


@app.get('/projetos/')
@app.get('/projetos/<int:id>')
def projetos_get(id=None):
    pagina = get_param_int('pagina', 0)
    max = get_param_int('max', 10)

    u = usuario()
    if not u:
        return redirect(url_for('login_get'))

    with g.db.cursor(dictionary=True, buffered=True) as cur:
        if id:
            cur.execute('select projetos.id, projetos.titulo, datas.criacao, datas.fazendo, datas.conclusao, datas.limite from projetos inner join datas on datas.id = projetos.data_id where projetos.id = %s', (id,))
            g.db.commit()

            mongo.registrar({'renderisar': 'projeto.html'})
            return render_template('projeto.html', projeto=cur.fetchone(), rota='projeto')

        projetos = db.call_proc(
            cur,
            'projetos_da_pessoa',
            u.id,
            pagina * max,
            max,
        )

        mongo.registrar({'renderisar': 'projetos.html'})
        return render_template(
            'projetos.html',
            projetos=projetos,
            rota='projetos',
            lista_pagina=pagina,
            lista_max=max,
        )

@app.post('/projetos/substituir')
def projetos_mudar_post():
    id = form_get('id')
    titulo = form_get('titulo')
    fazendo = form_get('fazendo') or 'NULL'
    conclusao = form_get('conclusao') or 'NULL'
    limite = form_get('limite')

    with g.db.cursor(buffered=True) as cur:
        if not id:
            u = usuario()
            args = (0, titulo, tempo(), u.id)
            print(args)
            cur.callproc('criar_projeto', args)
            g.db.commit()
            print(args)
            return redirect(url_for('projetos_get', id=args[0]))

        cur.execute(
            'call update_projeto(%s, %s, %s, %s, %s, %s)',
            (int(id), titulo, tempo(), fazendo, conclusao, limite),
        )
        g.db.commit()

        mongo.registrar({'redirecionar': 'projetos_get'})
        return redirect(url_for('projetos_get', id=int(id)))

@app.post('/perfil/substituir')
def pessoa_mudar_post():
    u = usuario()
    u.mudar(
        nome=form_get('nome'),
        email=form_get('email'),
    )

    mongo.registrar({'redirecionar': 'perfil_get'})
    return perfil(u)

@app.post('/reset')
def rest_post():
    mongo.registrar({'redirecionar': request.origin})

    if session.get('usuario'):
        session.pop('usuario')

    max = form_get('max')

    db_gen.do(g.db, int(max))
    return redirect(request.origin)
