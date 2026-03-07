#!/usr/bin/env python3
import os
import requests
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import logging

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

class PokeExtractor:
    def __init__(self):
        self.base_url = BASE_URL

    def extraer_pokemon(self, identificador):
        """Extrae datos de un Pokémon específico"""
        try:
            url = f"{self.base_url}/pokemon/{identificador}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            logger.info(f"✅ Datos extraídos para {identificador}")
            return response.json()
        except Exception as e:
            logger.error(f"❌ Error extrayendo {identificador}: {str(e)}")
            return None

    def extraer_especie(self, nombre):
        """Extrae datos de la especie del Pokémon (evoluciones, descripción, etc.)"""
        try:
            url = f"{self.base_url}/pokemon-species/{nombre}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ Error extrayendo especie de {nombre}: {str(e)}")
            return None

    def procesar_pokemon(self, data):
        """Procesa la respuesta JSON completa"""
        try:
            # Estadísticas
            stats = {s['stat']['name']: s['base_stat'] for s in data['stats']}

            # Tipos
            tipos = ', '.join([t['type']['name'] for t in data['types']])

            # Habilidades
            habilidades = ', '.join([a['ability']['name'] for a in data['abilities']])
            habilidades_ocultas = ', '.join([
                a['ability']['name'] for a in data['abilities'] if a['is_hidden']
            ])

            # Movimientos
            movimientos = ', '.join([m['move']['name'] for m in data['moves']])

            # Sprites (imágenes)
            sprites = data.get('sprites', {})

            # Especie
            especie_data = self.extraer_especie(data['name'])
            descripcion = ''
            es_legendario = False
            es_mitico = False
            tasa_captura = None
            felicidad_base = None
            habitat = ''
            generacion = ''
            cadena_evolucion_url = ''

            if especie_data:
                # Descripción en español o inglés
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
                cadena_evolucion_url = especie_data.get('evolution_chain', {}).get('url', '')

            return {
                # Identificación
                'id': data['id'],
                'nombre': data['name'],
                'es_default': data['is_default'],

                # Físico
                'altura': data['height'],
                'peso': data['weight'],

                # Combate
                'experiencia_base': data['base_experience'],
                'tipos': tipos,
                'habilidades': habilidades,
                'habilidades_ocultas': habilidades_ocultas,

                # Estadísticas
                'hp': stats.get('hp'),
                'ataque': stats.get('attack'),
                'defensa': stats.get('defense'),
                'ataque_especial': stats.get('special-attack'),
                'defensa_especial': stats.get('special-defense'),
                'velocidad': stats.get('speed'),

                # Movimientos
                'total_movimientos': len(data['moves']),
                'movimientos': movimientos,

                # Especie
                'descripcion': descripcion,
                'es_legendario': es_legendario,
                'es_mitico': es_mitico,
                'tasa_captura': tasa_captura,
                'felicidad_base': felicidad_base,
                'habitat': habitat,
                'generacion': generacion,
                'cadena_evolucion_url': cadena_evolucion_url,

                # Sprites
                'sprite_frente': sprites.get('front_default', ''),
                'sprite_shiny': sprites.get('front_shiny', ''),

                # Metadata
                'fecha_extraccion': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error procesando datos: {str(e)}")
            return None

    def ejecutar_extraccion(self, cantidad=150):
        """Extrae los primeros N Pokémon"""
        datos = []
        logger.info(f"Iniciando extracción de {cantidad} Pokémon...")

        for i in range(1, cantidad + 1):
            raw = self.extraer_pokemon(i)
            if raw:
                procesado = self.procesar_pokemon(raw)
                if procesado:
                    datos.append(procesado)

        return datos

if __name__ == "__main__":
    try:
        extractor = PokeExtractor()
        datos = extractor.ejecutar_extraccion(150)

        with open('data/pokemon_raw.json', 'w') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        logger.info("📁 Datos guardados en data/pokemon_raw.json")

        df = pd.DataFrame(datos)
        df.to_csv('data/pokemon.csv', index=False)
        logger.info("📁 Datos guardados en data/pokemon.csv")

        print("\n" + "="*50)
        print("RESUMEN DE EXTRACCIÓN")
        print("="*50)
        print(df[['id', 'nombre', 'tipos', 'hp', 'ataque', 'defensa', 'es_legendario', 'generacion']].to_string())
        print("="*50)

    except Exception as e:
        logger.error(f"Error en extracción: {str(e)}")
