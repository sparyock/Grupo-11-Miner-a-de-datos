#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from streamlit_lottie import st_lottie

from scripts.database import SessionLocal
from scripts.models import Pokemon, MetricasETL

st.set_page_config(
    page_title="Dashboard Pokémon",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

def cargar_lottie(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_pokemon = cargar_lottie("https://assets9.lottiefiles.com/packages/lf20_ycmof7n0.json")

st.markdown("""
<style>
    .main { background-color: #1a1a2e; }
    .stMetric { background-color: #16213e; border-radius: 10px; padding: 10px; border-left: 4px solid #e94560; }
    .title-text { color: #e94560; font-size: 3em; font-weight: bold; text-align: center; }
    .subtitle-text { color: #a8a8b3; text-align: center; font-size: 1.2em; }
    .pokemon-card { background-color: #16213e; border-radius: 15px; padding: 15px; text-align: center; border: 2px solid #e94560; margin: 5px; }
    div[data-testid="stSidebar"] { background-color: #16213e; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="title-text">⚡ Pokédex Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Análisis completo de la Primera Generación</p>', unsafe_allow_html=True)

col_anim1, col_titulo, col_anim2 = st.columns([1, 3, 1])
with col_anim1:
    if lottie_pokemon:
        st_lottie(lottie_pokemon, height=150, key="pokemon1")
with col_anim2:
    if lottie_pokemon:
        st_lottie(lottie_pokemon, height=150, key="pokemon2")

st.markdown("---")

db = SessionLocal()

try:
    pokemons = db.query(Pokemon).all()

    data = []
    for p in pokemons:
        data.append({
            'ID': p.id,
            'Nombre': p.nombre.capitalize(),
            'Tipos': p.tipos,
            'HP': p.hp,
            'Ataque': p.ataque,
            'Defensa': p.defensa,
            'Ataque Especial': p.ataque_especial,
            'Defensa Especial': p.defensa_especial,
            'Velocidad': p.velocidad,
            'Total': (p.hp or 0) + (p.ataque or 0) + (p.defensa or 0) + (p.ataque_especial or 0) + (p.defensa_especial or 0) + (p.velocidad or 0),
            'Es Legendario': p.es_legendario,
            'Es Mítico': p.es_mitico,
            'Generacion': p.generacion,
            'Habitat': p.habitat,
            'Peso': p.peso,
            'Altura': p.altura,
            'Sprite': p.sprite_frente,
            'Sprite Shiny': p.sprite_shiny,
            'Descripcion': p.descripcion,
            'Felicidad': p.felicidad_base,
            'Tasa Captura': p.tasa_captura,
        })

    df = pd.DataFrame(data)

    # Sidebar
    st.sidebar.markdown("## 🎮 Filtros")
    tipos_disponibles = sorted(set(
        tipo.strip()
        for tipos in df['Tipos'].dropna()
        for tipo in tipos.split(',')
    ))
    tipos_filtro = st.sidebar.multiselect("🔥 Tipos:", options=tipos_disponibles, default=[])
    solo_legendarios = st.sidebar.checkbox("⭐ Solo Legendarios")
    solo_miticos = st.sidebar.checkbox("✨ Solo Míticos")
    rango_ataque = st.sidebar.slider("⚔️ Rango de Ataque:", 0, 200, (0, 200))

    df_filtrado = df.copy()
    if tipos_filtro:
        df_filtrado = df_filtrado[df_filtrado['Tipos'].apply(
            lambda x: any(t.strip() in x for t in tipos_filtro) if pd.notna(x) else False
        )]
    if solo_legendarios:
        df_filtrado = df_filtrado[df_filtrado['Es Legendario'] == True]
    if solo_miticos:
        df_filtrado = df_filtrado[df_filtrado['Es Mítico'] == True]
    df_filtrado = df_filtrado[
        (df_filtrado['Ataque'] >= rango_ataque[0]) &
        (df_filtrado['Ataque'] <= rango_ataque[1])
    ]

    # Métricas
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("🎯 Total Pokémon", len(df_filtrado))
    with col2:
        mejor_ataque = df_filtrado.loc[df_filtrado['Ataque'].idxmax()]
        st.metric("⚔️ Mayor Ataque", f"{mejor_ataque['Ataque']}", delta=mejor_ataque['Nombre'])
    with col3:
        mejor_vel = df_filtrado.loc[df_filtrado['Velocidad'].idxmax()]
        st.metric("⚡ Mayor Velocidad", f"{mejor_vel['Velocidad']}", delta=mejor_vel['Nombre'])
    with col4:
        mejor_hp = df_filtrado.loc[df_filtrado['HP'].idxmax()]
        st.metric("❤️ Mayor HP", f"{mejor_hp['HP']}", delta=mejor_hp['Nombre'])
    with col5:
        st.metric("⭐ Legendarios", int(df_filtrado['Es Legendario'].sum()))

    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Estadísticas", "🔥 Tipos", "⭐ Legendarios", "🖼️ Pokédex Visual", "📋 Datos"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            top10 = df_filtrado.nlargest(10, 'Ataque')
            fig = px.bar(top10, x='Nombre', y='Ataque',
                        title='⚔️ Top 10 Mayor Ataque',
                        color='Ataque', color_continuous_scale='Reds',
                        template='plotly_dark')
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            top10v = df_filtrado.nlargest(10, 'Velocidad')
            fig = px.bar(top10v, x='Nombre', y='Velocidad',
                        title='⚡ Top 10 Mayor Velocidad',
                        color='Velocidad', color_continuous_scale='Blues',
                        template='plotly_dark')
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.scatter(df_filtrado, x='Ataque', y='Defensa',
                           color='Tipos', hover_data=['Nombre', 'HP'],
                           title='⚔️ Ataque vs Defensa',
                           template='plotly_dark', size='HP')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            top10t = df_filtrado.nlargest(10, 'Total')
            fig = px.bar(top10t, x='Nombre', y='Total',
                        title='🏆 Top 10 Pokémon más Poderosos (Total Stats)',
                        color='Total', color_continuous_scale='Viridis',
                        template='plotly_dark')
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 🎯 Comparar Pokémon")
        col1, col2 = st.columns(2)
        with col1:
            poke1 = st.selectbox("Pokémon 1:", df_filtrado['Nombre'].tolist(), index=0)
        with col2:
            poke2 = st.selectbox("Pokémon 2:", df_filtrado['Nombre'].tolist(), index=1)

        categorias = ['HP', 'Ataque', 'Defensa', 'Ataque Especial', 'Defensa Especial', 'Velocidad']
        p1 = df_filtrado[df_filtrado['Nombre'] == poke1].iloc[0]
        p2 = df_filtrado[df_filtrado['Nombre'] == poke2].iloc[0]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=[p1[c] for c in categorias], theta=categorias, fill='toself', name=poke1))
        fig.add_trace(go.Scatterpolar(r=[p2[c] for c in categorias], theta=categorias, fill='toself', name=poke2))
        fig.update_layout(template='plotly_dark', title='Comparación de Stats')
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        tipos_exp = df_filtrado['Tipos'].str.split(', ').explode().value_counts().reset_index()
        tipos_exp.columns = ['Tipo', 'Cantidad']

        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(tipos_exp, x='Tipo', y='Cantidad',
                        title='Distribución de Tipos',
                        color='Cantidad', color_continuous_scale='Viridis',
                        template='plotly_dark')
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.pie(tipos_exp, values='Cantidad', names='Tipo',
                        title='Proporción de Tipos', template='plotly_dark',
                        hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

        stats_tipo = df_filtrado.copy()
        stats_tipo['Tipo Principal'] = stats_tipo['Tipos'].apply(lambda x: x.split(',')[0].strip() if pd.notna(x) else '')
        prom_tipo = stats_tipo.groupby('Tipo Principal')[['Ataque', 'Defensa', 'Velocidad', 'HP']].mean().reset_index()
        fig = px.bar(prom_tipo, x='Tipo Principal', y=['Ataque', 'Defensa', 'Velocidad', 'HP'],
                    title='Promedio de Stats por Tipo', barmode='group', template='plotly_dark')
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        legendarios = df_filtrado[df_filtrado['Es Legendario'] == True]
        miticos = df_filtrado[df_filtrado['Es Mítico'] == True]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### ⭐ Legendarios")
            if not legendarios.empty:
                for _, row in legendarios.iterrows():
                    cols = st.columns([1, 3])
                    with cols[0]:
                        if row['Sprite']:
                            st.image(row['Sprite'], width=80)
                    with cols[1]:
                        st.markdown(f"**{row['Nombre']}**")
                        st.caption(f"Tipos: {row['Tipos']} | Total: {row['Total']}")
            else:
                st.info("No hay legendarios con los filtros actuales")

        with col2:
            st.markdown("### ✨ Míticos")
            if not miticos.empty:
                for _, row in miticos.iterrows():
                    cols = st.columns([1, 3])
                    with cols[0]:
                        if row['Sprite']:
                            st.image(row['Sprite'], width=80)
                    with cols[1]:
                        st.markdown(f"**{row['Nombre']}**")
                        st.caption(f"Tipos: {row['Tipos']} | Total: {row['Total']}")
            else:
                st.info("No hay míticos con los filtros actuales")

    with tab4:
        st.markdown("### 🖼️ Pokédex Visual")
        buscar = st.text_input("🔍 Buscar Pokémon:", "")
        df_buscar = df_filtrado[df_filtrado['Nombre'].str.contains(buscar, case=False)] if buscar else df_filtrado

        cols_por_fila = 5
        pokemons_lista = df_buscar.head(150).to_dict('records')
        for i in range(0, len(pokemons_lista), cols_por_fila):
            cols = st.columns(cols_por_fila)
            for j, poke in enumerate(pokemons_lista[i:i+cols_por_fila]):
                with cols[j]:
                    if poke['Sprite']:
                        st.image(poke['Sprite'], width=80)
                    st.markdown(f"**#{poke['ID']} {poke['Nombre']}**")
                    st.caption(poke['Tipos'])

    with tab5:
        st.dataframe(df_filtrado.drop(columns=['Sprite', 'Sprite Shiny', 'Descripcion']),
                    use_container_width=True, height=500)
        csv = df_filtrado.to_csv(index=False)
        st.download_button(
            label="⬇️ Descargar CSV",
            data=csv,
            file_name="pokemon_data.csv",
            mime="text/csv"
        )

finally:
    db.close()