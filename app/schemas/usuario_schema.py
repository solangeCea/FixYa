from pydantic import BaseModel, EmailStr, field_validator
from datetime import date
import re

from app.enums.usuario_enum import TipoUsuario


class UsuarioCreate(BaseModel):

    rut: str
    nombre_completo: str
    fecha_nacimiento: date
    genero: str
    correo: EmailStr
    telefono: str
    contrasena: str
    comuna_id_comuna: int

    tipo_usuario: TipoUsuario

    @field_validator("rut", "nombre_completo")
    @classmethod
    def validar_obligatorio(cls, value: str):
        if not value or not value.strip():
            raise ValueError("Este campo es obligatorio")
        return value.strip()

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, value: str):
        if not re.fullmatch(r"\d{8,12}", value or ""):
            raise ValueError("El telefono debe contener solo numeros y tener entre 8 y 12 digitos")
        return value

    @field_validator("contrasena")
    @classmethod
    def validar_contrasena(cls, value: str):
        if len(value or "") < 8:
            raise ValueError("La contrasena debe tener al menos 8 caracteres")
        if not re.search(r"[A-Z]", value):
            raise ValueError("La contrasena debe incluir al menos una mayuscula")
        if not re.search(r"[a-z]", value):
            raise ValueError("La contrasena debe incluir al menos una minuscula")
        if not re.search(r"\d", value):
            raise ValueError("La contrasena debe incluir al menos un numero")
        return value

    @field_validator("fecha_nacimiento")
    @classmethod
    def validar_edad(cls, value: date):
        today = date.today()
        if value > today:
            raise ValueError("La fecha de nacimiento no puede ser futura")

        edad = today.year - value.year - (
            (today.month, today.day) < (value.month, value.day)
        )

        if edad < 18:
            raise ValueError("Debes tener al menos 18 anos")

        return value
