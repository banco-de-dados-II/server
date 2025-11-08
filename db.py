import json


from flask import g
from globals import *

class Tabela:
    tabela = '????'

    def mudar(self, **kargs):
        for k, v in kargs.items():
            self.__dict__[k] = v

        with g.db.cursor() as cur:
            stmt = f'update {self.tabela} set '
            stmt += ', '.join([f'{k} = %({k})s' for k in self.to_args().keys()])
            stmt += ' where id = %(id)s'

            cur.execute(stmt, self.to_args())

            g.db.commit()
            return self

    def to_args(self):
        return self.__dict__

    def to_json(self):
        return json.dumps({'id': self.id} | self.to_args())

    @classmethod
    def from_json(klass, s):
        kargs = json.loads(s)
        return klass(*kargs)

    @classmethod
    def adicionar(klass, **kargs):
        with g.db.cursor() as cur:
            stmt = f'insert into {klass.tabela}'
            stmt += '('+(', '.join([k for k in kargs.keys()]))+')'
            stmt += ' value '
            stmt += '('+(', '.join([f'%({k})s' for k in kargs.keys()]))+')'

            cur.execute(stmt, kargs)

            g.db.commit()
            return klass(id=cur.lastrowid, **kargs)

    @classmethod
    def procurar(klass, expr, **kargs):
        assert len(kargs) > 0

        stmt = f'select {expr} from {klass.tabela} where '
        stmt += ' and '.join([f'{k} = %({k})s' for k in kargs.keys()])

        cur = g.db.cursor()
        cur.execute(stmt, kargs)
        return cur


    @classmethod
    def from_id(klass, id):
        stmt = f'select * from {klass.tabela} where id = %d'

        with g.db.cursor() as cur:
            cur.execute(stmt, id)
            klass(*cur.fetchone())


class Pessoa(Tabela):
    tabela = 'pessoas'

    def __init__(self, id, nome, email):
        self.id = id
        self.nome = nome
        self.email = email
