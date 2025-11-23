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
import pygal

def escape_str(s):
    if s is None or len(s) == 0:
        return None
    return str(escape(s))

def form_get(key):
    return escape_str(request.form.get(key, None))


def form_get_list(key):
    value = form_get(key)
    if value:
        return value.split(',')
    else:
        return []

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


def redirecionar(f, d={}, **kargs):
    d['redirecionar'] = f
    mongo.registrar(d)
    return redirect(url_for(f, **kargs))

def renderisar(rota, d={}, **kargs):
    d['renderisar'] = rota
    mongo.registrar(d)
    return render_template(f'{rota}.html', **kargs, rota=rota)

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
    return renderisar('index')

@app.get('/login/')
def login_get():
    return renderisar('login')

@app.get('/perfil/')
def perfil_get():
    u = usuario()
    if not u:
        return redirecionar(
            'login_get',
        )

    graficos = []

    tarefas = pygal.Pie()
    with g.db.cursor(buffered=True) as cur:
        for status in tarefa_status:
            cur.execute(
                'select count(*) from card where atribuido_id = %s and status = %s',
                (u.id, status)
            )
            tarefas.add(status, cur.fetchone()[0])
    graficos.append(tarefas)

    graficos = map(lambda o: o.render(disable_xml_declaration=True), graficos)

    return renderisar(
        'perfil',
        graficos=graficos
    )

def perfil(u, rest={}):
    session['usuario'] = u.to_json()
    return redirecionar('perfil_get', rest)

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

    return perfil(u, {'adicionar': not bool(pargs)})

@app.get('/tarefas/')
@app.get('/tarefas/<int:id>')
def tarefas_get(id=None):
    pagina = get_param_int('pagina', 0)
    max = get_param_int('max', 10)

    u = usuario()
    if not u:
        return redirecionar('login_get')

    if id:
        with g.db.cursor(dictionary=True, buffered=True) as cur:
            cur.execute('select * from card where id = %s', (id, ))
            tarefa = cur.fetchone()
            tarefa['tags'] = ','.join(mongo.tag_search(tarefa['tag'])['tags'])
            return renderisar('tarefa', tarefa=tarefa)

    with g.db.cursor(dictionary=True, buffered=True) as cur:
        tarefas = db.call_proc(cur, 'card_da_pessoa', u.id, pagina * max, max)

    for i in range(len(tarefas)):
        search = mongo.tag_search(tarefas[i]['tag'])
        tarefas[i]['tags'] = ','.join(search['tags'])

    return renderisar(
        'tarefas',
        tarefas=tarefas,
        lista_pagina=pagina,
        lista_max=max,
    )

@app.post('/tarefas/substituir')
def tarefas_substituir_post():
    id = form_get('id')
    titulo = form_get('titulo')
    tags = form_get_list('tags')
    fazendo = form_get('fazendo')
    conclusao = form_get('conclusao')
    limite = form_get('limite')
    status = form_get('status')

    modo: str
    with g.db.cursor(buffered=True) as cur:
        u = usuario()
        if not id:
            modo = 'criar'
            criacao = tempo()

            cur.execute('call create_card(@ret, %s, %s, %s, %s, %s, %s, %s)', (titulo, criacao, None, None, None, status, u.id))
            g.db.commit()
            cur.execute('select @ret')
            id = cur.fetchone()[0]
            print(f'id: {id}')
            tag_id = mongo.tag_update({'tarefa': id, 'pessoa': u.id}, ['criador'])
            cur.execute('insert into tarefas_has_pessoas (tarefa_id, pessoa_id, tag) value (%s, %s, %s)', (id, u.id, tag_id))
            g.db.commit()
        else:
            modo = 'substituir'
            tag_id = mongo.tag_update({'tarefa': id, 'pessoa': u.id}, tags)
            cur.execute('call update_card(%s, %s, %s, %s, %s, %s, %s)',
                        (int(id), titulo, tag_id, fazendo, conclusao, limite, status))
            g.db.commit()

    return redirecionar('tarefas_get', {'modo': modo}, id=id)


@app.get('/equipes')
@app.get('/equipes/<int:id>')
def equipes_get(id=None):
    pagina = get_param_int('pagina', 0)
    max = get_param_int('max', 10)

    u = usuario()
    if not u:
        return redirecionar('login_get')

    if id:
        with g.db.cursor(dictionary=True, buffered=True) as cur:
            cur.execute('select * from equipe_full where equipe_id = %s and pessoa_id = %s', (id, u.id))
            equipe = cur.fetchone()
            search = mongo.tag_search(equipe['equipe_tag'])
            equipe['tags'] = ','.join(search['tags'])
            return renderisar('equipe', equipe=equipe)

    equipes = db.call_proc(
        g.db.cursor(dictionary=True),
        'equipes_da_pessoa',
        u.id,
        pagina * max,
        max,
    )

    print(f'{equipes=}')

    for i in range(len(equipes)):
        search = mongo.tag_search(equipes[i]['tag'])
        equipes[i]['tags'] = ','.join(search['tags'])

    return renderisar(
        'equipes',
        equipes=equipes,
        lista_pagina=pagina,
        lista_max=max,
    )

@app.post('/equipes/substituir')
def equipes_post():
    u = usuario()
    id = form_get('id')
    nome = form_get('nome') or ''
    tags = form_get_list('tags')

    tag_id = mongo.tag_update({'equipe': id, 'pessoa': u.id}, tags)
    with g.db.cursor(buffered=True) as cur:
        cur.execute('update equipes set nome = %s where id = %s', (nome, id))
        cur.execute('update equipes_has_pessoas set tag = %s where equipe_id = %s and pessoa_id = %s', (tag_id, id, u.id))
        g.db.commit()

    return redirecionar('equipes_get', id=id)

@app.post('/equipes/criar')
def equipes_criar_post():
    u = usuario()
    nome = form_get('nome')

    id: int
    with g.db.cursor(buffered=True) as cur:
        cur.execute('insert into equipes (nome) value (%s)', (nome,))
        g.db.commit()
        id = cur.lastrowid
        tag = mongo.tag_update({'equipe': id, 'pessoa': u.id}, ['criador'])
        cur.execute('insert into equipes_has_pessoas (equipe_id, pessoa_id, tag) value (%s, %s, %s)', (id, u.id, tag))
        g.db.commit()

    return redirecionar('equipes_get', id=id)

@app.post('/equipes/sair')
def equipes_sair_post():
    u = usuario()
    if not u:
        return redirecionar('login_get')
    id = form_get('id')

    with g.db.cursor(buffered=True) as cur:
        cur.execute('delete from equipes_has_pessoas where equipe_id = %s and pessoa_id = %s', (id, u.id))

    g.db.commit()

    return redirecionar('equipes_get')

@app.post('/equipes/nova-pessoa')
def equipes_nova_pessoa():
    equipe_id = int(form_get('id'))
    nome = form_get('nome')
    tags = form_get_list('tags')

    with g.db.cursor(dictionary=True, buffered=True) as cur:
        pessoa_id = db.Pessoa.procurar('id', nome=nome).fetchone()[0]
        tag_id = mongo.tag_search({'equipe': equipe_id, 'pessoa': pessoa_id})

        cur.execute(
            'call equipe_adicionar_pessoa (%s, %s, %s)',
            equipe_id, pessoa_id, tag_id,
        )

        g.db.commit()

        return redirecionar('equipes_get', id=equipe_id)

@app.get('/projetos/')
@app.get('/projetos/<int:id>')
def projetos_get(id=None):
    pagina = get_param_int('pagina', 0)
    max = get_param_int('max', 10)

    u = usuario()
    if not u:
        return redirecionar('login_get')

    with g.db.cursor(dictionary=True, buffered=True) as cur:
        if id:
            cur.execute('select projetos.id, projetos.titulo, datas.criacao, datas.fazendo, datas.conclusao, datas.limite from projetos inner join datas on datas.id = projetos.data_id where projetos.id = %s', (id,))
            g.db.commit()

            return renderisar('projeto', projeto=cur.fetchone())

        projetos = db.call_proc(
            cur,
            'projetos_da_pessoa',
            u.id,
            pagina * max,
            max,
        )

        return renderisar(
            'projetos',
            projetos=projetos,
            lista_pagina=pagina,
            lista_max=max,
        )

@app.post('/projetos/substituir')
def projetos_mudar_post():
    id = form_get('id')
    titulo = form_get('titulo')
    fazendo = form_get('fazendo') or 'NULL'
    conclusao = form_get('conclusao') or 'NULL'
    limite = form_get('limite') or 'NULL'

    with g.db.cursor(buffered=True) as cur:
        if not id:
            u = usuario()
            args = (0, titulo, tempo(), u.id)
            cur.callproc('criar_projeto', args)
            g.db.commit()
            return redirecionar('projetos_get', id=args[0])

        cur.execute(
            'call update_projeto(%s, %s, %s, %s, %s, %s)',
            (int(id), titulo, tempo(), fazendo, conclusao, limite),
        )
        g.db.commit()

        return redirecionar('projetos_get', id=int(id))

@app.post('/perfil/substituir')
def pessoa_mudar_post():
    u = usuario()
    u.mudar(
        nome=form_get('nome'),
        email=form_get('email'),
    )

    return perfil(u)

@app.post('/reset')
def rest_post():
    if session.get('usuario'):
        session.pop('usuario')

    max = form_get('max')

    db_gen.do(g.db, g.mdb, int(max))
    return redirecionar('index')

@app.post('/dump')
def dump_post():
    print(g.mongo)
    print(g.mdb)
    print(g.mdb['logs'])
    for d in g.mdb['logs'].find():
        print(d)
    for d in g.mdb['tags'].find():
        print(d)

    return redirecionar('index')
