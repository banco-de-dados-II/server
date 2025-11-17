from dataclasses import dataclass
import json

from flask import g
from globals import *

def call_proc(cur, proc_name, *args):
    stmt = f'call {proc_name}'
    stmt += '('
    for i in range(len(args)):
        if i > 0:
            stmt += ','
        stmt += '%s'
    stmt += ')'
    cur.execute(stmt, args)
    return cur.fetchall()

class Tabela:
    def mudar(self, **kargs):
        for k, v in kargs.items():
            self[k] = v

        self.atualizar()
        return self

    def atualizar(self):
        with g.db.cursor() as cur:
            stmt = f'update {self.TABELA} set '
            stmt += ', '.join([f'{k} = %({k})s' for k in self.to_args().keys()])
            stmt += ' where id = %(id)s'

            cur.execute(stmt, self.to_args())

            g.db.commit()
            return self

    def to_args(self):
        return self.__dict__

    def to_json(self):
        return json.dumps(self.to_args())

    def __getitem__(self, index):
        return self.__dict__[index]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __delitem__(self, key):
        self.__dict__[key] = None

    @classmethod
    def from_json(klass, s):
        kargs = json.loads(s)
        return klass(*kargs)

    @classmethod
    def adicionar(klass, **kargs):
        with g.db.cursor() as cur:
            stmt = f'insert into {klass.TABELA}'
            stmt += '('+(', '.join([k for k in kargs.keys()]))+')'
            stmt += ' value '
            stmt += '('+(', '.join([f'%({k})s' for k in kargs.keys()]))+')'

            cur.execute(stmt, kargs)

            g.db.commit()
            return klass(id=cur.lastrowid, **kargs)

    @classmethod
    def procurar(klass, expr, **kargs):
        stmt = f'select {expr} from {klass.TABELA}'
        if len(kargs) != 0:
            stmt += ' where '
            stmt += ' and '.join([f'{k} = %({k})s' for k in kargs.keys()])

        cur = g.db.cursor()
        cur.execute(stmt, kargs)
        return cur


    @classmethod
    def from_id(klass, id):
        cur = klass.procurar('*', id=id)
        return klass(*cur.fetchone())

    @classmethod
    def count(klass):
        cur = klass.procurar('count(*)')
        return cur.fetchone()[0]

@dataclass
class Projeto(Tabela):
    TABELA = 'projetos'

    id: int
    titulo: str
    data_id: int

@dataclass
class Pessoa(Tabela):
    TABELA = 'pessoas'

    id: int
    nome: str
    email: str


@dataclass
class Tarefa(Tabela):
    TABELA = 'tarefas'

    id: int
    status: str
    titulo: str
    projeto_id: int
    criador_id: int
    data_id: int

@dataclass
class Equipe(Tabela):
    TABELA = 'equipes'

    id: int
    nome: int

@dataclass
class EquipePessoa(Tabela):
    TABELA = 'equipe_has_pessoas'

    equipe_id: int
    pessoa_id: int
    tag: str

@dataclass
class TarefaPessoa(Tabela):
    TABELA = 'tarefas_has_pessoas'

    tarefa_id: int
    pessoa_id: int

@dataclass
class ProjetoPessoa(Tabela):
    TABELA = 'projetos_has_pessoas'

    projeto_id: int
    pessoa_id: int
    tag: str

@dataclass
class ProjetoEquipe(Tabela):
    TABELA = 'projetos_has_equipe'

    projeto_id: int
    equipe_id: int
    tag: str
