from globals import *

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

class Pessoas(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    nome: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(nullable=True)

#class Datas(db.Model):
#    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
#    dia_de_criacao: Mapped[] = mapped_column(nullable=False)