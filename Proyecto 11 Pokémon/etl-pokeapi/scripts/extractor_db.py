#!/usr/bin/env python3
import os
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
import logging
from sqlalchemy.exc import IntegrityError

import sys
sys.path.insert(0, '.')
from scripts.database import SessionLocal
from scripts.models import Pokemon, MetricasETL

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/etl.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BASE_URL = os.getenv('POKEAPI_BASE_URL')

class PokeETL:
    def __init__(self):
        self.base_url = BASE_URL
        self.db = SessionLocal()
        self.tiempo_inicio = time.time()
        self.registros_extraidos = 0
        self.registros_guardados = 0
        self.registros_fallidos = 0

    def extraer_pokemon(self, identificador):
        try:
            url = f"{self.base_url}/pokemon/{identificador}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            self.registros_extraidos += 1
            logger.info(f"✅ Datos extraídos para {identificador}")
            return response.json()
        except Exception as e:
            logger.error(f"❌ Error extrayendo {identificador}: {str(e)}")
            self.registros_fallidos += 1
            return None

    def extraer_especie(self, nombre):
        try:
            url = f"{self.base_url}/pokemon-species/{nombre}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except:
            return None

    def procesar_pokemon(self, data):
        try:
            stats = {s['stat']['name']: s['base_stat'] for s in data['stats']}
            tipos = ', '.join([t['type']['name'] for t in data['types']])
            habilidades = ', '.join([a['ability']['name'] for a in data['abilities']])
            habilidades_ocultas = ', '.join([a['ability']['name'] for a in data['abilities'] if a['is_hidden']])

            especie_data = self.extraer_especie(data['name'])
            descripcion = ''
            es_legendario = False
            es_mitico = False
            tasa_captura = None
            felicidad_base = None
            habitat = ''
            generacion = ''

            if especie_data:
                for entry in especie_data.get('flavor_text_entries', []):
                    if entry['language']['name'] == 'es':
                        descripcion = entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
                        break
                if not descripcion:
                    for entry in especie_data.get('flavor_text_entries', []):
                        if entry['language']['name'] == 'en':
                            descripcion = entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
                            break

                es_legendario = especie_data.get('is_legendary', False)
                es_mitico = especie_data.get('is_mythical', False)
                tasa_captura = especie_data.get('capture_rate')
                felicidad_base = especie_data.get('base_happiness')
                habitat = especie_data.get('habitat', {}).get('name', '') if especie_data.get('habitat') else ''
                generacion = especie_data.get('generation', {}).get('name', '')

            return {
                'id': data['id'],
                'nombre': data['name'],
                'altura': data['height'],
                'peso': data['weight'],
                'experiencia_base': data['base_experience'],
                'tipos': tipos,
                'habilidades': habilidades,
                'habilidades_ocultas': habilidades_ocultas,
                'hp': stats.get('hp'),
                'ataque': stats.get('attack'),
                'defensa': stats.get('defense'),
                'ataque_especial': stats.get('special-attack'),
                'defensa_especial': stats.get('special-defense'),
                'velocidad': stats.get('speed'),
                'total_movimientos': len(data['moves']),
                'es_legendario': es_legendario,
                'es_mitico': es_mitico,
                'tasa_captura': tasa_captura,
                'felicidad_base': felicidad_base,
                'habitat': habitat,
                'generacion': generacion,
                'descripcion': descripcion,
                'sprite_frente': data.get('sprites', {}).get('front_default', ''),
                'sprite_shiny': data.get('sprites', {}).get('front_shiny', ''),
                'fecha_extraccion': datetime.now()
            }
        except Exception as e:
            logger.error(f"Error procesando datos: {str(e)}")
            return None

    def guardar_en_bd(self, datos):
        try:
            pokemon = self.db.query(Pokemon).filter_by(id=datos['id']).first()
            if not pokemon:
                pokemon = Pokemon(**datos)
                self.db.add(pokemon)
            else:
                for key, value in datos.items():
                    setattr(pokemon, key, value)
            self.db.commit()
            self.registros_guardados += 1
            logger.info(f"📊 Guardado: {datos['nombre']}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error guardando {datos['nombre']}: {str(e)}")
            self.registros_fallidos += 1
            return False

    def guardar_metricas(self, estado):
        try:
            tiempo = time.time() - self.tiempo_inicio
            metricas = MetricasETL(
                registros_extraidos=self.registros_extraidos,
                registros_guardados=self.registros_guardados,
                registros_fallidos=self.registros_fallidos,
                tiempo_ejecucion_segundos=tiempo,
                estado=estado,
                mensaje=f"Extraídos: {self.registros_extraidos}, Guardados: {self.registros_guardados}, Fallidos: {self.registros_fallidos}"
            )
            self.db.add(metricas)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error guardando métricas: {str(e)}")

    def ejecutar(self, cantidad=1000):
        logger.info(f"Iniciando ETL para {cantidad} Pokémon...")
        for i in range(1, cantidad + 1):
            raw = self.extraer_pokemon(i)
            if raw:
                procesado = self.procesar_pokemon(raw)
                if procesado:
                    self.guardar_en_bd(procesado)

        estado = "SUCCESS" if self.registros_fallidos == 0 else "PARTIAL"
        self.guardar_metricas(estado)

        print("\n" + "="*50)
        print("RESUMEN ETL POKÉMON")
        print("="*50)
        print(f"Extraídos: {self.registros_extraidos}")
        print(f"Guardados: {self.registros_guardados}")
        print(f"Fallidos:  {self.registros_fallidos}")
        print("="*50)

        self.db.close()

if __name__ == "__main__":
    etl = PokeETL()
    etl.ejecutar(1000)
