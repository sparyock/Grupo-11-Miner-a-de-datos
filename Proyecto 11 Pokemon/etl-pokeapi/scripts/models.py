#!/usr/bin/env python3
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy import Index
from scripts.database import Base

class Pokemon(Base):
    __tablename__ = "pokemon"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, index=True)
    altura = Column(Integer)
    peso = Column(Integer)
    experiencia_base = Column(Integer)
    tipos = Column(String(100))
    habilidades = Column(Text)
    habilidades_ocultas = Column(Text)
    hp = Column(Integer)
    ataque = Column(Integer)
    defensa = Column(Integer)
    ataque_especial = Column(Integer)
    defensa_especial = Column(Integer)
    velocidad = Column(Integer)
    total_movimientos = Column(Integer)
    es_legendario = Column(Boolean, default=False)
    es_mitico = Column(Boolean, default=False)
    tasa_captura = Column(Integer)
    felicidad_base = Column(Integer)
    habitat = Column(String(100))
    generacion = Column(String(100))
    descripcion = Column(Text)
    sprite_frente = Column(Text)
    sprite_shiny = Column(Text)
    fecha_extraccion = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_nombre', 'nombre'),
        Index('idx_tipos', 'tipos'),
    )

    def __repr__(self):
        return f"<Pokemon {self.nombre}>"

class MetricasETL(Base):
    __tablename__ = "metricas_etl"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha_ejecucion = Column(DateTime, default=datetime.utcnow)
    registros_extraidos = Column(Integer)
    registros_guardados = Column(Integer)
    registros_fallidos = Column(Integer, default=0)
    tiempo_ejecucion_segundos = Column(Float)
    estado = Column(String(50))
    mensaje = Column(String(500))

    def __repr__(self):
        return f"<MetricasETL {self.estado}>"
