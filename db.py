from globals import *

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

class Pessoas(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(nullable=True)


#with app.app_context():
#    db.create_all()
