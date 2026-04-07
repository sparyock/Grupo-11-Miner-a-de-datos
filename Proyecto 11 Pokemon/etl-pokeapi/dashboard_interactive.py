#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import func, and_
import requests
from streamlit_lottie import st_lottie

from scripts.database import SessionLocal
from scripts.models import Pokemon, MetricasETL

st.set_page_config(
    page_title="Pokédex Interactivo",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="expanded"
)
import scripts.database as _db
st.write("HOST:", _db.cfg['host'])
st.markdown("""
<style>
    body { background-color: #0d0d1a; }
    .main { background-color: #0d0d1a; }
    .big-title {
        font-size: 3.5em;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #e94560, #f5a623, #e94560);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 200%;
    }
    .subtitle {
        text-align: center;
        color: #a8a8b3;
        font-size: 1.3em;
        margin-bottom: 20px;
    }
    .section-title {
        color: #f5a623;
        font-size: 1.8em;
        font-weight: bold;
        border-bottom: 2px solid #e94560;
        padding-bottom: 5px;
        margin: 20px 0;
    }
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d0d1a, #16213e);
        border-right: 2px solid #e94560;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #16213e;
        color: #a8a8b3;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e94560 !important;
        color: white !important;
    }
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 15px;
        padding: 15px;
        border-left: 5px solid #e94560;
        box-shadow: 0 4px 15px rgba(233, 69, 96, 0.3);
    }
</style>
""", unsafe_allow_html=True)

def cargar_lottie(url):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

lottie_pokeball = cargar_lottie("https://assets2.lottiefiles.com/packages/lf20_pKiaUR.json")

col_l, col_c, col_r = st.columns([1, 4, 1])
with col_l:
    if lottie_pokeball:
        st_lottie(lottie_pokeball, height=130, key="ball_left")
with col_c:
    st.markdown('<p class="big-title">🎛️ Pokédex Interactivo</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Control total sobre los datos de la Primera Generación</p>', unsafe_allow_html=True)
with col_r:
    if lottie_pokeball:
        st_lottie(lottie_pokeball, height=130, key="ball_right")

st.markdown("---")

@st.cache_data
def cargar_datos():
    db_local = SessionLocal()
    pokemons = db_local.query(Pokemon).all()
    data = []
    for p in pokemons:
        data.append({
            'ID': p.id,
            'Nombre': p.nombre.capitalize(),
            'Tipos': p.tipos,
            'Tipo Principal': p.tipos.split(',')[0].strip() if p.tipos else '',
            'HP': p.hp or 0,
            'Ataque': p.ataque or 0,
            'Defensa': p.defensa or 0,
            'Ataque Especial': p.ataque_especial or 0,
            'Defensa Especial': p.defensa_especial or 0,
            'Velocidad': p.velocidad or 0,
            'Total': (p.hp or 0) + (p.ataque or 0) + (p.defensa or 0) + (p.ataque_especial or 0) + (p.defensa_especial or 0) + (p.velocidad or 0),
            'Es Legendario': p.es_legendario,
            'Es Mítico': p.es_mitico,
            'Generacion': p.generacion,
            'Habitat': p.habitat or 'Desconocido',
            'Sprite': p.sprite_frente,
            'Sprite Shiny': p.sprite_shiny,
            'Tasa Captura': p.tasa_captura or 0,
            'Felicidad': p.felicidad_base or 0,
            'Peso': p.peso or 0,
            'Altura': p.altura or 0,
            'Descripcion': p.descripcion or '',
        })
    db_local.close()
    return pd.DataFrame(data)

df = cargar_datos()

# Sidebar con controles avanzados
st.sidebar.markdown("## 🎮 Control Total")
st.sidebar.markdown("---")

tipos_disponibles = sorted(df['Tipo Principal'].unique())
tipos_filtro = st.sidebar.multiselect("🔥 Tipos:", options=tipos_disponibles, default=[])

st.sidebar.markdown("### 📊 Rangos de Stats")
rango_hp = st.sidebar.slider("❤️ HP:", 0, 300, (0, 300))
rango_ataque = st.sidebar.slider("⚔️ Ataque:", 0, 200, (0, 200))
rango_defensa = st.sidebar.slider("🛡️ Defensa:", 0, 200, (0, 200))
rango_velocidad = st.sidebar.slider("⚡ Velocidad:", 0, 200, (0, 200))
rango_total = st.sidebar.slider("💪 Total:", 0, 800, (0, 800))

st.sidebar.markdown("### 🏷️ Categorías")
solo_legendarios = st.sidebar.checkbox("⭐ Solo Legendarios")
solo_miticos = st.sidebar.checkbox("✨ Solo Míticos")
mostrar_shiny = st.sidebar.checkbox("🌟 Sprites Shiny")

st.sidebar.markdown("---")
st.sidebar.info(f"Total en BD: **{len(df)}** Pokémon")

# Aplicar filtros
df_f = df.copy()
if tipos_filtro:
    df_f = df_f[df_f['Tipo Principal'].isin(tipos_filtro)]
if solo_legendarios:
    df_f = df_f[df_f['Es Legendario'] == True]
if solo_miticos:
    df_f = df_f[df_f['Es Mítico'] == True]
df_f = df_f[
    (df_f['HP'] >= rango_hp[0]) & (df_f['HP'] <= rango_hp[1]) &
    (df_f['Ataque'] >= rango_ataque[0]) & (df_f['Ataque'] <= rango_ataque[1]) &
    (df_f['Defensa'] >= rango_defensa[0]) & (df_f['Defensa'] <= rango_defensa[1]) &
    (df_f['Velocidad'] >= rango_velocidad[0]) & (df_f['Velocidad'] <= rango_velocidad[1]) &
    (df_f['Total'] >= rango_total[0]) & (df_f['Total'] <= rango_total[1])
]

# Métricas principales
st.markdown('<p class="section-title">📊 Indicadores en Tiempo Real</p>', unsafe_allow_html=True)
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
with col1:
    st.metric("🎯 Total Pokémon", len(df_f))
with col2:
    st.metric("⭐ Legendarios", int(df_f['Es Legendario'].sum()))
with col3:
    st.metric("✨ Míticos", int(df_f['Es Mítico'].sum()))
with col4:
    if not df_f.empty:
        idx = df_f['HP'].idxmax()
        st.metric("❤️ Mayor HP", df_f.loc[idx, 'HP'], delta=df_f.loc[idx, 'Nombre'])
with col5:
    if not df_f.empty:
        idx = df_f['Ataque'].idxmax()
        st.metric("⚔️ Mayor Ataque", df_f.loc[idx, 'Ataque'], delta=df_f.loc[idx, 'Nombre'])
with col6:
    if not df_f.empty:
        idx = df_f['Velocidad'].idxmax()
        st.metric("⚡ Mayor Velocidad", df_f.loc[idx, 'Velocidad'], delta=df_f.loc[idx, 'Nombre'])
with col7:
    if not df_f.empty:
        idx = df_f['Total'].idxmax()
        st.metric("🏆 Mayor Total", df_f.loc[idx, 'Total'], delta=df_f.loc[idx, 'Nombre'])

st.markdown("---")

if df_f.empty:
    st.warning("⚠️ No hay Pokémon que coincidan con los filtros seleccionados. Ajusta los controles del panel.")
else:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Estadísticas",
        "🔥 Tipos",
        "🆚 Comparador",
        "⭐ Especiales",
        "🖼️ Pokédex Visual",
        "📋 Datos y Exportar"
    ])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            top10 = df_f.nlargest(10, 'Ataque')
            fig = px.bar(top10, x='Nombre', y='Ataque',
                        title='⚔️ Top 10 Mayor Ataque',
                        color='Ataque', color_continuous_scale='Reds',
                        template='plotly_dark')
            fig.update_xaxes(tickangle=45)
            fig.update_layout(paper_bgcolor='rgba(22,33,62,0.8)', font_color='#a8a8b3')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            top10v = df_f.nlargest(10, 'Velocidad')
            fig = px.bar(top10v, x='Nombre', y='Velocidad',
                        title='⚡ Top 10 Mayor Velocidad',
                        color='Velocidad', color_continuous_scale='Blues',
                        template='plotly_dark')
            fig.update_xaxes(tickangle=45)
            fig.update_layout(paper_bgcolor='rgba(22,33,62,0.8)', font_color='#a8a8b3')
            st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.scatter(df_f, x='Ataque', y='Defensa',
                           color='Tipo Principal', hover_data=['Nombre', 'HP'],
                           title='⚔️ Ataque vs Defensa',
                           template='plotly_dark', size='HP',
                           color_discrete_sequence=px.colors.qualitative.Bold)
            fig.update_layout(paper_bgcolor='rgba(22,33,62,0.8)', font_color='#a8a8b3')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            top10t = df_f.nlargest(10, 'Total')
            fig = px.bar(top10t, x='Nombre', y='Total',
                        title='🏆 Top 10 más Poderosos',
                        color='Total', color_continuous_scale='Viridis',
                        template='plotly_dark')
            fig.update_xaxes(tickangle=45)
            fig.update_layout(paper_bgcolor='rgba(22,33,62,0.8)', font_color='#a8a8b3')
            st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.scatter(df_f, x='HP', y='Velocidad',
                           color='Tipo Principal', hover_data=['Nombre'],
                           title='❤️ HP vs Velocidad',
                           template='plotly_dark',
                           color_discrete_sequence=px.colors.qualitative.Bold)
            fig.update_layout(paper_bgcolor='rgba(22,33,62,0.8)', font_color='#a8a8b3')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.box(df_f, y=['HP', 'Ataque', 'Defensa', 'Ataque Especial', 'Defensa Especial', 'Velocidad'],
                        title='📦 Distribución de Stats',
                        template='plotly_dark',
                        color_discrete_sequence=px.colors.qualitative.Bold)
            fig.update_layout(paper_bgcolor='rgba(22,33,62,0.8)', font_color='#a8a8b3')
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        tipos_exp = df_f['Tipos'].str.split(', ').explode().value_counts().reset_index()
        tipos_exp.columns = ['Tipo', 'Cantidad']

        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(tipos_exp, x='Tipo', y='Cantidad',
                        title='Distribución de Tipos',
                        color='Cantidad', color_continuous_scale='Viridis',
                        template='plotly_dark')
            fig.update_xaxes(tickangle=45)
            fig.update_layout(paper_bgcolor='rgba(22,33,62,0.8)', font_color='#a8a8b3')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.pie(tipos_exp, values='Cantidad', names='Tipo',
                        title='Proporción de Tipos',
                        template='plotly_dark', hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Bold)
            fig.update_layout(paper_bgcolor='rgba(22,33,62,0.8)', font_color='#a8a8b3')
            st.plotly_chart(fig, use_container_width=True)

        tipo_sel = st.selectbox("🔍 Radar por tipo:", sorted(df_f['Tipo Principal'].unique()))
        df_tipo = df_f[df_f['Tipo Principal'] == tipo_sel]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Pokémon", len(df_tipo))
        with col2:
            st.metric("❤️ HP Prom.", f"{df_tipo['HP'].mean():.1f}")
        with col3:
            st.metric("⚔️ Ataque Prom.", f"{df_tipo['Ataque'].mean():.1f}")
        with col4:
            st.metric("💪 Total Prom.", f"{df_tipo['Total'].mean():.1f}")

        prom = df_tipo[['HP', 'Ataque', 'Defensa', 'Ataque Especial', 'Defensa Especial', 'Velocidad']].mean()
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=prom.values, theta=prom.index, fill='toself',
            name=tipo_sel, line_color='#e94560', fillcolor='rgba(233,69,96,0.3)'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 150])),
            title=f'🕸️ Radar Promedio - Tipo {tipo_sel}',
            template='plotly_dark',
            paper_bgcolor='rgba(22,33,62,0.8)', font_color='#a8a8b3'
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.markdown("### 🆚 Comparador Interactivo")
        col1, col2 = st.columns(2)
        with col1:
            poke1 = st.selectbox("Pokémon 1:", df_f['Nombre'].tolist(), index=0)
        with col2:
            poke2 = st.selectbox("Pokémon 2:", df_f['Nombre'].tolist(), index=min(1, len(df_f)-1))

        p1 = df_f[df_f['Nombre'] == poke1].iloc[0]
        p2 = df_f[df_f['Nombre'] == poke2].iloc[0]

        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            sprite1 = p1['Sprite Shiny'] if mostrar_shiny and p1['Sprite Shiny'] else p1['Sprite']
            if sprite1:
                st.image(sprite1, width=130)
            st.markdown(f"### {p1['Nombre']}")
            st.caption(p1['Tipos'])
            st.metric("💪 Total", p1['Total'])
        with col3:
            sprite2 = p2['Sprite Shiny'] if mostrar_shiny and p2['Sprite Shiny'] else p2['Sprite']
            if sprite2:
                st.image(sprite2, width=130)
            st.markdown(f"### {p2['Nombre']}")
            st.caption(p2['Tipos'])
            st.metric("💪 Total", p2['Total'])
        with col2:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            st.markdown("## ⚡ VS ⚡")
            ganador_total = poke1 if p1['Total'] > p2['Total'] else poke2
            st.success(f"🏆 Ganador por Total: **{ganador_total}**")

        stats = ['HP', 'Ataque', 'Defensa', 'Ataque Especial', 'Defensa Especial', 'Velocidad']
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=[p1[s] for s in stats], theta=stats, fill='toself', name=poke1, line_color='#e94560', fillcolor='rgba(233,69,96,0.3)'))
        fig.add_trace(go.Scatterpolar(r=[p2[s] for s in stats], theta=stats, fill='toself', name=poke2, line_color='#f5a623', fillcolor='rgba(245,166,35,0.3)'))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 200])),
            title='🕸️ Comparación de Stats',
            template='plotly_dark',
            paper_bgcolor='rgba(22,33,62,0.8)', font_color='#a8a8b3'
        )
        st.plotly_chart(fig, use_container_width=True)

        comp_data = {'Stat': stats, poke1: [p1[s] for s in stats], poke2: [p2[s] for s in stats]}
        df_comp = pd.DataFrame(comp_data)
        df_comp['Ganador'] = df_comp.apply(lambda r: f"🥇 {poke1}" if r[poke1] > r[poke2] else (f"🥇 {poke2}" if r[poke2] > r[poke1] else '🤝 Empate'), axis=1)
        st.dataframe(df_comp, use_container_width=True)

    with tab4:
        legendarios = df_f[df_f['Es Legendario'] == True]
        miticos = df_f[df_f['Es Mítico'] == True]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### ⭐ Legendarios")
            if not legendarios.empty:
                for _, row in legendarios.iterrows():
                    cols = st.columns([1, 3])
                    with cols[0]:
                        sprite = row['Sprite Shiny'] if mostrar_shiny and row['Sprite Shiny'] else row['Sprite']
                        if sprite:
                            st.image(sprite, width=80)
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
                        sprite = row['Sprite Shiny'] if mostrar_shiny and row['Sprite Shiny'] else row['Sprite']
                        if sprite:
                            st.image(sprite, width=80)
                    with cols[1]:
                        st.markdown(f"**{row['Nombre']}**")
                        st.caption(f"Tipos: {row['Tipos']} | Total: {row['Total']}")
            else:
                st.info("No hay míticos con los filtros actuales")

        if not legendarios.empty or not miticos.empty:
            df_especiales = pd.concat([legendarios, miticos]).drop_duplicates()
            fig = px.bar(df_especiales, x='Nombre',
                        y=['HP', 'Ataque', 'Defensa', 'Velocidad'],
                        title='📊 Stats de Pokémon Especiales',
                        barmode='group', template='plotly_dark')
            fig.update_layout(paper_bgcolor='rgba(22,33,62,0.8)', font_color='#a8a8b3')
            st.plotly_chart(fig, use_container_width=True)

    with tab5:
        st.markdown("### 🖼️ Pokédex Visual - 150 Pokémon")
        col1, col2 = st.columns(2)
        with col1:
            buscar = st.text_input("🔍 Buscar Pokémon:", "")
        with col2:
            tipo_visual = st.selectbox("Filtrar por tipo:", ['Todos'] + tipos_disponibles)

        cols_vista = st.columns([1, 3])
        with cols_vista[0]:
            cols_por_fila = st.slider("Columnas:", 3, 6, 5)

        df_visual = df_f.copy()
        if buscar:
            df_visual = df_visual[df_visual['Nombre'].str.contains(buscar, case=False)]
        if tipo_visual != 'Todos':
            df_visual = df_visual[df_visual['Tipo Principal'] == tipo_visual]

        st.caption(f"Mostrando {len(df_visual)} Pokémon")

        pokemons_lista = df_visual.to_dict('records')
        for i in range(0, len(pokemons_lista), cols_por_fila):
            cols = st.columns(cols_por_fila)
            for j, poke in enumerate(pokemons_lista[i:i+cols_por_fila]):
                with cols[j]:
                    sprite = poke['Sprite Shiny'] if mostrar_shiny and poke['Sprite Shiny'] else poke['Sprite']
                    if sprite:
                        st.image(sprite, width=80)
                    st.markdown(f"**#{poke['ID']} {poke['Nombre']}**")
                    st.caption(poke['Tipos'])

    with tab6:
        st.markdown("### 📋 Datos Detallados")

        columnas_mostrar = st.multiselect(
            "Columnas a mostrar:",
            ['ID', 'Nombre', 'Tipos', 'HP', 'Ataque', 'Defensa', 'Ataque Especial', 'Defensa Especial', 'Velocidad', 'Total', 'Es Legendario', 'Es Mítico', 'Habitat', 'Generacion', 'Tasa Captura', 'Felicidad', 'Peso', 'Altura'],
            default=['ID', 'Nombre', 'Tipos', 'HP', 'Ataque', 'Defensa', 'Velocidad', 'Total']
        )

        ordenar_por = st.selectbox("Ordenar por:", ['ID', 'Total', 'HP', 'Ataque', 'Defensa', 'Velocidad'])
        orden_desc = st.checkbox("Orden descendente", value=True)

        df_tabla = df_f[columnas_mostrar].sort_values(ordenar_por, ascending=not orden_desc)
        st.dataframe(df_tabla, use_container_width=True, height=500)

        col1, col2 = st.columns(2)
        with col1:
            csv = df_f.drop(columns=['Sprite', 'Sprite Shiny', 'Descripcion']).to_csv(index=False)
            st.download_button(
                label="⬇️ Descargar CSV completo",
                data=csv,
                file_name="pokemon_data.csv",
                mime="text/csv"
            )
        with col2:
            csv_filtrado = df_tabla.to_csv(index=False)
            st.download_button(
                label="⬇️ Descargar selección actual",
                data=csv_filtrado,
                file_name="pokemon_filtrado.csv",
                mime="text/csv"
            )
