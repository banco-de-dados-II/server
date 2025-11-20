import os
import json

from flask import render_template, request, redirect, url_for, send_file, g, session
from markupsafe import escape
from datetime import datetime
from time import time

from globals import *
import db
import db_gen

def escape_str(s):
    if s is None:
        return s
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


# ---------------------------
# ROTAS COM title + rota
# ---------------------------

@app.route('/')
def index():
    return render_template(
        'index.html',
        rota='home',
        title='Home'
    )


@app.get('/login/')
def login_get():
    return render_template(
        'login.html',
        rota='login',
        title='Login'
    )


@app.get('/perfil/')
def perfil_get():
    u = usuario()
    if not u:
        return redirect(url_for('login_get'))

    return render_template(
        'perfil.html',
        rota='perfil',
        title='Perfil'
    )


def perfil(u):
    session['usuario'] = u.to_json()
    return redirect(url_for("perfil_get"))


@app.post('/login')
def login_post():
    id = form_get('id')
    nome = form_get('nome')
    email = form_get('email')

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


@app.get('/tarefas/')
@app.get('/tarefas/<int:id>')
def tarefas_get(id=None):
    u = usuario()
    if not u:
        return redirect(url_for('login_get'))

    if id:
        with g.db.cursor(dictionary=True, buffered=True) as cur:
            cur.execute('select * from card where id = %s', (id,))
            return render_template(
                'tarefa.html',
                tarefa=cur.fetchone(),
                rota='tarefas',      # CONSISTENTE
                title='Tarefa'
            )

    with g.db.cursor(dictionary=True, buffered=True) as cur:
        tarefas = db.call_proc(cur, 'card_da_pessoa', u.id)

    return render_template(
        'tarefas.html',
        tarefas=tarefas,
        rota='tarefas',
        title='Tarefas'
    )


@app.post('/tarefas/substituir')
def tarefas_substituir_post():
    id = form_get('id')
    titulo = form_get('titulo')
    tag = form_get('tag')
    fazendo = form_get('fazendo')
    conclusao = form_get('conclusao')
    limite = form_get('limite')
    status = form_get('status')

    with g.db.cursor(buffered=True) as cur:
        if not id:
            u = usuario()
            criacao = tempo()
            cur.execute(
                'call create_card(%s, %s, %s, %s, %s, %s, %s, %s)',
                (titulo, 'criador', criacao, None, None, None, status, u.id)
            )
            g.db.commit()
            id = cur.lastrowid
        else:
            cur.execute(
                'call update_card(%s, %s, %s, %s, %s, %s, %s)',
                (int(id), titulo, tag, fazendo, conclusao, limite, status)
            )
            g.db.commit()

    return redirect(url_for('tarefas_get', id=id))


# -------------------------------
# EQUIPES
# -------------------------------

@app.get('/equipes')
@app.get('/equipes/<int:id>')
def equipes_get(id=None):
    u = usuario()
    if not u:
        return redirect(url_for('login_get'))

    if id:
        with g.db.cursor(dictionary=True, buffered=True) as cur:
            cur.execute(
                'select id, nome, tag from equipes '
                'inner join equipes_has_pessoas on equipe_id = id '
                'where id = %s',
                (id,)
            )
            return render_template(
                'equipe.html',
                equipe=cur.fetchone(),
                rota='equipes',
                title='Equipe'
            )

    equipes = db.call_proc(
        g.db.cursor(dictionary=True),
        'equipes_da_pessoa',
        u.id,
    )

    return render_template(
        'equipes.html',
        equipes=equipes,
        rota='equipes',
        title='Equipes'
    )


@app.post('/equipes/substituir')
def equipes_post():
    u = usuario()
    id = form_get('id')
    nome = form_get('nome')
    tag = form_get('tag')

    with g.db.cursor(buffered=True) as cur:
        cur.execute('update equipes set nome = %s where id = %s', (nome, id))
        cur.execute(
            'update equipes_has_pessoas set tag = %s where equipe_id = %s and pessoa_id = %s',
            (tag, id, u.id)
        )
        g.db.commit()

    return redirect(url_for('equipes_get', id=id))


@app.post('/equipes/criar')
def equipes_criar_post():
    u = usuario()
    nome = form_get('nome')

    with g.db.cursor(buffered=True) as cur:
        cur.execute('insert into equipes (nome) value (%s)', (nome,))
        g.db.commit()
        id = cur.lastrowid
        cur.execute(
            'insert into equipes_has_pessoas (equipe_id, pessoa_id, tag) '
            'value (%s, %s, "criador")',
            (id, u.id)
        )
        g.db.commit()

    return redirect(url_for('equipes_get', id=id))


@app.post('/equipes/sair')
def equipes_sair_post():
    u = usuario()
    if not u:
        return redirect(url_for('login_get'))
    id = form_get('id')

    with g.db.cursor(buffered=True) as cur:
        cur.execute(
            'delete from equipes_has_pessoas where equipe_id = %s and pessoa_id = %s',
            (id, u.id)
        )

    g.db.commit()

    return redirect(url_for('equipes_get'))


@app.post('/equipes/nova-pessoa')
def equipes_nova_pessoa():
    equipe_id = int(form_get('id'))
    nome = form_get('nome')
    tag = form_get('tag')

    with g.db.cursor(dictionary=True, buffered=True) as cur:
        pessoa_id = db.Pessoa.procurar('id', nome=nome).fetchone()[0]

        cur.execute(
            'call equipe_adicionar_pessoa (%s, %s, %s)',
            (equipe_id, pessoa_id, tag)
        )

        g.db.commit()
        return redirect(url_for('equipes_get', id=equipe_id))


# -------------------------------
# PROJETOS
# -------------------------------

@app.get('/projetos/')
@app.get('/projetos/<int:id>')
def projetos_get(id=None):
    u = usuario()
    if not u:
        return redirect(url_for('login_get'))

    with g.db.cursor(dictionary=True, buffered=True) as cur:
        if id:
            cur.execute(
                'select projetos.id, projetos.titulo, datas.criacao, datas.fazendo, datas.conclusao, datas.limite '
                'from projetos inner join datas on datas.id = projetos.data_id '
                'where projetos.id = %s',
                (id,)
            )
            g.db.commit()

            return render_template(
                'projeto.html',
                projeto=cur.fetchone(),
                rota='projetos',
                title='Projeto'
            )

        projetos = db.call_proc(cur, 'projetos_da_pessoa', u.id)

        return render_template(
            'projetos.html',
            projetos=projetos,
            rota='projetos',
            title='Projetos'
        )


@app.post('/projetos/substituir')
def projetos_mudar_post():
    id = form_get('id')
    titulo = form_get('titulo')
    fazendo = form_get('fazendo')
    conclusao = form_get('conclusao')
    limite = form_get('limite')

    with g.db.cursor(buffered=True) as cur:
        if not id:
            u = usuario()
            args = (0, titulo, tempo(), u.id)
            cur.callproc('criar_projeto', args)
            g.db.commit()
            return redirect(url_for('projetos_get', id=args[0]))

        cur.execute(
            'call update_projeto(%s, %s, %s, %s, %s, %s)',
            (int(id), titulo, tempo(), fazendo, conclusao, limite)
        )
        g.db.commit()

        return redirect(url_for('projetos_get', id=int(id)))


# -------------------------------
# RESET
# -------------------------------

@app.post('/reset')
def rest_post():
    if session.get('usuario'):
        session.pop('usuario')
    db_gen.do(g.db, 100)
    return redirect(request.origin)
