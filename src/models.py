from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Column, Table, ForeignKey, Integer
from typing import List

db = SQLAlchemy()

# Usuarios
# personajes
# planetas
# favoritos

# relaciones


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    
    favorite: Mapped[List["Favorite"]] = relationship()


def serialize(self):
    return {
        "id": self.id,
        "email": self.email,
    }


class Character(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    gender: Mapped[str] = mapped_column(nullable=False)
    hair_color: Mapped[str] = mapped_column(nullable=False)
    eye_color: Mapped[str] = mapped_column(nullable=False)
    height: Mapped[str] = mapped_column(nullable=False)
    homeworld_id: Mapped[int] = mapped_column(ForeignKey("planet.id"), nullable=True)
    favorite: Mapped["Favorite"] = relationship(back_populates="character")

    homeworld: Mapped["Planet"] =relationship("Planet", back_populates="character")
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color,
            "height": self.height,
            "homeworld": self.homeworld

        }


class Planet(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    climate: Mapped[str] = mapped_column(nullable=False)
    population: Mapped[str] = mapped_column(nullable=False)
    character: Mapped[List["Character"]]= relationship("Character", back_populates="homeworld")
    favorite: Mapped["Favorite"] = relationship(back_populates="planet")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "population": self.population
        }


class Vehicle(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    cost_in_credits: Mapped[str] = mapped_column(nullable=False)
    manufacturer: Mapped[str] = mapped_column(nullable=False)
    vehicle_class: Mapped[str] = mapped_column(nullable=False)
    favorite: Mapped["Favorite"] = relationship(back_populates="vehicle")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "cost_in_credits": self.cost_in_credits,
            "manufacturer": self.manufacturer,
            "vehicle_class": self.vehicle_class
        }


homeworld: Mapped[int] = mapped_column(ForeignKey("planet.id"))


class Favorite(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    character_id: Mapped[int] = mapped_column(
        ForeignKey("character.id"), nullable=True)
    planet_id: Mapped[int] = mapped_column(
        ForeignKey("planet.id"), nullable=True)
    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicle.id"), nullable=True)

    
    character: Mapped["Character"] = relationship(back_populates="favorite")
    planet: Mapped["Planet"] = relationship(back_populates="favorite")
    vehicle: Mapped["Vehicle"] = relationship(back_populates="favorite")

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user,
            "character": self.character,
            "planet": self.planet,
            "vehicle": self.vehicle
        }
