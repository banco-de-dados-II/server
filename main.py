import os
import json

from flask import render_template, request, redirect, url_for, send_file, g, session
from markupsafe import escape

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
def tarefas_get():
    u = usuario()
    if not u:
        return redirect(url_for('login_get'))

    with g.db.cursor(dictionary=True) as cur:
        tarefas = db.call_proc(
            cur,
            'card_da_pessoa',
            u.id,
        )

    return render_template(
        'tarefas.html',
        tarefas=tarefas,
    )

@app.get('/equipes')
@app.get('/equipes/<int:id>')
def equipes_get(id=None):
    u = usuario()
    if not u:
        return redirect(url_for('login_get'))

    if id:
        with g.db.cursor(dictionary=True) as cur:
            cur.execute('select id, nome, tag from equipes inner join equipes_has_pessoas on equipe_id = id where id = %s', (id,))
            return render_template('equipe.html', equipe=cur.fetchone())

    equipes = db.call_proc(
        g.db.cursor(dictionary=True),
        'equipes_da_pessoa',
        u.id,
    )

    return render_template(
        'equipes.html',
        equipes=equipes,
    )

@app.post('/equipes/mudar')
def equipes_post():
    u = usuario()
    id = form_get('id')
    nome = form_get('nome')
    tag = form_get('tag')

    with g.db.cursor() as cur:
        cur.execute('update equipes set nome = %s where id = %s', (nome, id))
        cur.execute('update equipes_has_pessoas set tag = %s where equipe_id = %s and pessoa_id = %s', (tag, id, u.id))
        g.db.commit()

    return redirect(url_for('equipes_get', id=id))

@app.post('/equipes/criar')
def equipes_criar_post():
    u = usuario()
    nome = form_get('nome')

    id: int
    with g.db.cursor() as cur:
        cur.execute('insert into equipes (nome) value (%s)', (nome,))
        g.db.commit()
        id = cur.lastrowid
        cur.execute('insert into equipes_has_pessoas (equipe_id, pessoa_id, tag) value (%s, %s, "criador")', (id, u.id))
        g.db.commit()

    return redirect(url_for('equipes_get', id=id))

@app.post('/equipes/sair')
def equipes_sair_post():
    u = usuario()
    if not u:
        return redirect(url_for('login_get'))
    id = form_get('id')

    with g.db.cursor() as cur:
        cur.execute('delete from equipes_has_pessoas where equipe_id = %s and pessoa_id = %s', (id, u.id))

    g.db.commit()

    return redirect(url_for('equipes_get'))

@app.post('/equipes/nova-pessoa')
def equipes_nova_pessoa():
    nome = form_get('nome')
    tag = form_get('tag')

    with g.db.cursor() as cur:
        cur.execute('select id from pessoas where nome = %s', (nome,))
        id = cur.fetchone()
        cur.execute('')

@app.get('/projetos/')
def projetos_get():
    u = usuario()
    if not u:
        return redirect(url_for('login_get'))

    projetos = db.call_proc(
        g.db.cursor(dictionary=True),
        'projetos_da_pessoa',
        u.id,
    )

    return render_template(
        'projetos.html',
        projetos=projetos,
    )

@app.post('/pessoa-mudar')
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
    db_gen.do(g.db, 100)
    return redirect(request.origin)
