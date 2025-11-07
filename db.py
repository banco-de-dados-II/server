from flask import g
from globals import *

def pessoa_procurar(nome):
    cur = g.db.cursor()
    cur.execute(
        'select * from pessoas where nome = %s',
        (nome,),
    )

    return cur.fetchall()

def pessoa_adicionar(nome, email):
    cur = g.db.cursor()
    cur.execute(
        'insert into pessoas (nome, email) value (%s, %s)',
        (nome, email),
    )

    g.db.commit()
    return cur.lastrowid

def pessoa_mudar(nome_antigo, nome, email):
    assert len(pessoa_procurar(nome_antigo)) > 0

    cur = g.db.cursor()
    cur.execute(
        'update pessoas set nome = %s, email = %s where nome = %s',
        (nome, email, nome_antigo),
    )

    g.db.commit()
    return cur.lastrowid
