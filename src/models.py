from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

db = SQLAlchemy()


#Tabla para relacion Usuario-Planetas
planetas_favoritos = Table(
    "planetas_favoritos",
    db.metadata,
    Column("planeta", ForeignKey("planetas.nombre")),
    Column("usuario", ForeignKey("usuario.email"))
)

personajes_favoritos = Table(
    "personajes_favoritos",
    db.metadata,
    Column("personaje", ForeignKey("personajes.nombre")),
    Column("usuario", ForeignKey("usuario.email"))

)


class Usuario(db.Model):
    email: Mapped[str] = mapped_column(String(120), primary_key=True)
    password: Mapped[str] = mapped_column(String(20), nullable=False)
    fecha_suscripcion: Mapped[str] = mapped_column(String(20), nullable=False)
    nombre: Mapped[str] = mapped_column(String(20), nullable=False)
    apellido: Mapped[str] = mapped_column(String(20), nullable=False)
    
    #Relacion con PLANETAS
    planetas : Mapped[List["Planetas"]] = relationship(secondary="planetas_favoritos", back_populates="users")
    #Relación con Personajes
    personajes : Mapped[List["Personajes"]] = relationship(secondary="personajes_favoritos", back_populates="users")

class Planetas(db.Model):
    nombre: Mapped[str] = mapped_column(String(20), primary_key=True)
    galaxia:  Mapped[str] = mapped_column(String(20), nullable = False)
    numero_planetas : Mapped[int] = mapped_column(nullable=False)
    habitable : Mapped[bool] = mapped_column(nullable=False)

    #Relacion con USUARIO
    users: Mapped[List["Usuario"]] = relationship(secondary="planetas_favoritos", back_populates="planetas")
    #Relacion 1-N con PERSONAJES
    personajes : Mapped[List["Personajes"]] = relationship(back_populates="planeta")
class Personajes(db.Model):
    nombre: Mapped[str] = mapped_column(String(20), primary_key=True)
    edad: Mapped[int] = mapped_column(nullable=False)

    #Relacion con USUARIO
    users : Mapped[List["Usuario"]] = relationship(secondary="personajes_favoritos", back_populates="personajes")
    #Relacion 1-N con PLANETAS
    planeta_nombre: Mapped[str] = mapped_column(ForeignKey("planetas.nombre"))
    planeta : Mapped["Planetas"] = relationship(back_populates="personajes")
    #Relacion 1-N con NAVES
    naves: Mapped[List["Naves"]] = relationship(back_populates="personaje")

class Naves(db.Model):
    nombre: Mapped[str] = mapped_column(String(20), primary_key= True)
    capacidad : Mapped[int] = mapped_column(nullable=False)
    velocidad: Mapped[int] = mapped_column(nullable=False)

    #relacion 1-N con PERSONAJES
    capitan : Mapped[str] = mapped_column(ForeignKey("personajes.nombre"))
    personaje : Mapped["Personajes"] = relationship(back_populates="naves")