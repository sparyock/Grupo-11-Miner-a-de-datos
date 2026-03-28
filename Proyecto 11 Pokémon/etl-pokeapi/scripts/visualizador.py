import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

os.makedirs("reports", exist_ok=True)

df = pd.read_csv("data/pokemon.csv")

# Paleta de colores por tipo
TYPE_COLORS = {
    "fire": "#F08030", "water": "#6890F0", "grass": "#78C850",
    "electric": "#F8D030", "psychic": "#F85888", "ice": "#98D8D8",
    "dragon": "#7038F8", "dark": "#705848", "fairy": "#EE99AC",
    "normal": "#A8A878", "fighting": "#C03028", "flying": "#A890F0",
    "poison": "#A040A0", "ground": "#E0C068", "rock": "#B8A038",
    "bug": "#A8B820", "ghost": "#705898", "steel": "#B8B8D0",
}

# ─────────────────────────────────────────────
# 1. HISTOGRAMA DE HP (original mejorado)
# ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
ax.hist(df['hp'], bins=20, color="#6890F0", edgecolor="white", linewidth=0.8)
ax.axvline(df['hp'].mean(), color='red', linestyle='--', linewidth=1.5, label=f"Media: {df['hp'].mean():.1f}")
ax.axvline(df['hp'].median(), color='orange', linestyle='--', linewidth=1.5, label=f"Mediana: {df['hp'].median():.1f}")
ax.set_title("Distribución de HP en los 150 Pokémon", fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel("HP", fontsize=11)
ax.set_ylabel("Cantidad de Pokémon", fontsize=11)
ax.legend()
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
plt.savefig("reports/1_histograma_hp.png", dpi=150)
print("✅ Gráfica 1 guardada: histograma_hp.png")
plt.close()

# ─────────────────────────────────────────────
# 2. CONTEO DE TIPOS PRINCIPALES
# ─────────────────────────────────────────────
tipo_principal = df['tipos'].str.split(',').str[0].str.strip()
conteo = tipo_principal.value_counts()
colores = [TYPE_COLORS.get(t, "#AAAAAA") for t in conteo.index]

fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.bar(conteo.index, conteo.values, color=colores, edgecolor="white", linewidth=0.8)
ax.bar_label(bars, padding=3, fontsize=9, fontweight='bold')
ax.set_title("¿Cuántos Pokémon hay de cada tipo?", fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel("Tipo principal", fontsize=11)
ax.set_ylabel("Cantidad", fontsize=11)
plt.xticks(rotation=35, ha='right')
ax.spines[['top', 'right']].set_visible(False)
ax.set_ylim(0, conteo.max() + 5)
plt.tight_layout()
plt.savefig("reports/2_conteo_tipos.png", dpi=150)
print("✅ Gráfica 2 guardada: conteo_tipos.png")
plt.close()

# ─────────────────────────────────────────────
# 3. TOP 10 POKÉMON CON MAYOR ATAQUE
# ─────────────────────────────────────────────
top_ataque = df.nlargest(10, 'ataque')[['nombre', 'ataque', 'tipos']].reset_index(drop=True)
tipo_color = [TYPE_COLORS.get(r['tipos'].split(',')[0].strip(), "#AAAAAA") for _, r in top_ataque.iterrows()]

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(top_ataque['nombre'], top_ataque['ataque'], color=tipo_color, edgecolor="white")
ax.bar_label(bars, padding=4, fontsize=10, fontweight='bold')
ax.set_title("Top 10 Pokémon con Mayor Ataque", fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel("Ataque", fontsize=11)
ax.invert_yaxis()
ax.spines[['top', 'right']].set_visible(False)
ax.set_xlim(0, top_ataque['ataque'].max() + 20)
plt.tight_layout()
plt.savefig("reports/3_top10_ataque.png", dpi=150)
print("✅ Gráfica 3 guardada: top10_ataque.png")
plt.close()

# ─────────────────────────────────────────────
# 4. SCATTER: ATAQUE VS DEFENSA
# ─────────────────────────────────────────────
legendarios = df['es_legendario'] == True
normales = ~legendarios

fig, ax = plt.subplots(figsize=(9, 7))
ax.scatter(df.loc[normales, 'ataque'], df.loc[normales, 'defensa'],
           alpha=0.6, color="#6890F0", s=50, label="Normal")
ax.scatter(df.loc[legendarios, 'ataque'], df.loc[legendarios, 'defensa'],
           alpha=0.9, color="#F85888", s=120, marker="*", label="Legendario", zorder=5)

# Etiquetas para legendarios
for _, row in df[legendarios].iterrows():
    ax.annotate(row['nombre'], (row['ataque'], row['defensa']),
                textcoords="offset points", xytext=(6, 4), fontsize=8, color="#C03028")

ax.set_title("Ataque vs Defensa: ¿Quién es más equilibrado?", fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel("Ataque", fontsize=11)
ax.set_ylabel("Defensa", fontsize=11)
ax.legend(fontsize=10)
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
plt.savefig("reports/4_scatter_ataque_defensa.png", dpi=150)
print("✅ Gráfica 4 guardada: scatter_ataque_defensa.png")
plt.close()

# ─────────────────────────────────────────────
# 5. BOXPLOT: ESTADÍSTICAS LEGENDARIOS VS NORMALES
# ─────────────────────────────────────────────
stats = ['hp', 'ataque', 'defensa']
labels_esp = ['HP', 'Ataque', 'Defensa']

data_leg = [df[df['es_legendario'] == True][s].values for s in stats]
data_nor = [df[df['es_legendario'] == False][s].values for s in stats]

fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(stats))
width = 0.35

bp1 = ax.boxplot(data_nor, positions=x - width/2, widths=0.3,
                 patch_artist=True, boxprops=dict(facecolor="#6890F0", alpha=0.7),
                 medianprops=dict(color="white", linewidth=2))
bp2 = ax.boxplot(data_leg, positions=x + width/2, widths=0.3,
                 patch_artist=True, boxprops=dict(facecolor="#F85888", alpha=0.7),
                 medianprops=dict(color="white", linewidth=2))

ax.set_xticks(x)
ax.set_xticklabels(labels_esp, fontsize=11)
ax.set_title("Estadísticas: Legendarios vs Pokémon Normales", fontsize=14, fontweight='bold', pad=12)
ax.set_ylabel("Valor", fontsize=11)
normal_patch = mpatches.Patch(color="#6890F0", alpha=0.7, label="Normales")
legend_patch = mpatches.Patch(color="#F85888", alpha=0.7, label="Legendarios")
ax.legend(handles=[normal_patch, legend_patch], fontsize=10)
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
plt.savefig("reports/5_boxplot_legendarios.png", dpi=150)
print("✅ Gráfica 5 guardada: boxplot_legendarios.png")
plt.close()

# ─────────────────────────────────────────────
# 6. RADAR CHART: PERFIL DE 5 POKÉMON ICÓNICOS
# ─────────────────────────────────────────────
iconicos = ['charizard', 'blastoise', 'venusaur', 'pikachu', 'mewtwo']
colores_radar = ["#F08030", "#6890F0", "#78C850", "#F8D030", "#7038F8"]
categorias = ['hp', 'ataque', 'defensa']
N = len(categorias)
angulos = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angulos += angulos[:1]

fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
for nombre, color in zip(iconicos, colores_radar):
    row = df[df['nombre'] == nombre]
    if row.empty:
        continue
    valores = row[categorias].values.flatten().tolist()
    valores += valores[:1]
    ax.plot(angulos, valores, 'o-', linewidth=2, color=color, label=nombre.capitalize())
    ax.fill(angulos, valores, alpha=0.1, color=color)

ax.set_xticks(angulos[:-1])
ax.set_xticklabels(['HP', 'Ataque', 'Defensa'], fontsize=12)
ax.set_title("Perfil de Estadísticas: Pokémon Icónicos", fontsize=13, fontweight='bold', pad=20)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)
plt.tight_layout()
plt.savefig("reports/6_radar_iconicos.png", dpi=150)
print("✅ Gráfica 6 guardada: radar_iconicos.png")
plt.close()

# ─────────────────────────────────────────────
# 7. HEATMAP DE CORRELACIÓN
# ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(6, 5))
corr = df[['hp', 'ataque', 'defensa']].corr()
im = ax.imshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
plt.colorbar(im, ax=ax, shrink=0.8)
ticks = ['HP', 'Ataque', 'Defensa']
ax.set_xticks(range(3)); ax.set_xticklabels(ticks, fontsize=11)
ax.set_yticks(range(3)); ax.set_yticklabels(ticks, fontsize=11)
for i in range(3):
    for j in range(3):
        ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha='center', va='center',
                fontsize=13, fontweight='bold',
                color='white' if abs(corr.iloc[i, j]) > 0.5 else 'black')
ax.set_title("¿Qué estadísticas están relacionadas?", fontsize=13, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig("reports/7_heatmap_correlacion.png", dpi=150)
print("✅ Gráfica 7 guardada: heatmap_correlacion.png")
plt.close()

print("\n🎉 ¡Todas las gráficas generadas en la carpeta reports/!")