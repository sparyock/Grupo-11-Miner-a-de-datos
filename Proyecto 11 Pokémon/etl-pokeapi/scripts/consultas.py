#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from scripts.database import SessionLocal
from scripts.models import Pokemon, MetricasETL
from sqlalchemy import func
import pandas as pd

db = SessionLocal()

def pokemon_mas_fuertes():
    registros = db.query(Pokemon).order_by(Pokemon.ataque.desc()).limit(10).all()
    print("\n⚔️ TOP 10 POKÉMON POR ATAQUE:")
    for p in registros:
        print(f"  {p.nombre}: {p.ataque}")

def pokemon_mas_rapidos():
    registros = db.query(Pokemon).order_by(Pokemon.velocidad.desc()).limit(10).all()
    print("\n⚡ TOP 10 POKÉMON MÁS RÁPIDOS:")
    for p in registros:
        print(f"  {p.nombre}: {p.velocidad}")

def distribucion_tipos():
    registros = db.query(Pokemon.tipos, func.count(Pokemon.id).label('cantidad')).group_by(Pokemon.tipos).all()
    df = pd.DataFrame(registros, columns=['Tipos', 'Cantidad'])
    print("\n🔥 DISTRIBUCIÓN DE TIPOS:")
    print(df.to_string(index=False))

def legendarios():
    registros = db.query(Pokemon).filter(Pokemon.es_legendario == True).all()
    print("\n⭐ POKÉMON LEGENDARIOS:")
    for p in registros:
        print(f"  {p.nombre}")

def metricas_etl():
    metricas = db.query(MetricasETL).order_by(MetricasETL.fecha_ejecucion.desc()).limit(5).all()
    print("\n📈 ÚLTIMAS 5 EJECUCIONES DEL ETL:")
    for m in metricas:
        print(f"  - {m.fecha_ejecucion}: {m.estado} ({m.registros_guardados} registros en {m.tiempo_ejecucion_segundos:.2f}s)")

if __name__ == "__main__":
    try:
        print("\n" + "="*50)
        print("ANÁLISIS DE DATOS - POKÉMON")
        print("="*50)

        pokemon_mas_fuertes()
        pokemon_mas_rapidos()
        distribucion_tipos()
        legendarios()
        metricas_etl()

        print("\n" + "="*50 + "\n")

    finally:
        db.close()
