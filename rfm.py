"""Segmentación de clientes RFM con plan de acción -> tablero.html + clientes_rfm.csv"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from dashboard_kit import PALETTE, money, render_dashboard, table_html, tag

df = pd.read_csv("ventas.csv", parse_dates=["fecha"])
df["ingreso"] = df.cantidad * df.precio_unitario * (1 - df.descuento)
snap = df.fecha.max() + pd.Timedelta(days=1)  # fecha de corte del análisis

c = df.groupby("cliente_id").agg(
    ultima_compra=("fecha", "max"), frecuencia=("order_id", "nunique"), monto=("ingreso", "sum")
)
c["recencia_dias"] = (snap - c.ultima_compra).dt.days

# Puntajes: recencia en quintiles (5 = compró hace poco); frecuencia 1, 2 o 3+; monto en quintiles
c["R"] = pd.qcut(c.recencia_dias, 5, labels=[5, 4, 3, 2, 1]).astype(int)
c["F"] = c.frecuencia.clip(upper=3)
c["M"] = pd.qcut(c.monto.rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)


def segmento(r):
    if r.F == 3 and r.R >= 4:
        return "Campeones"
    if (r.F == 3 and r.R == 3) or (r.F == 2 and r.R >= 4):
        return "Leales"
    if r.F == 1 and r.R >= 4:
        return "Nuevos"
    if r.F == 3 and r.R <= 2:
        return "Valiosos dormidos"
    if r.F == 2 and r.R <= 2:
        return "En riesgo"
    if r.R == 3:
        return "Por activar"
    return "Dormidos"


c["segmento"] = c.apply(segmento, axis=1)

ORDEN = ["Campeones", "Leales", "Nuevos", "Por activar", "En riesgo", "Valiosos dormidos", "Dormidos"]
ACCION = {
    "Campeones": ("Cuidarlos", "Acceso anticipado a lanzamientos, programa de referidos y un detalle de agradecimiento. No dar descuentos: ya compran."),
    "Leales": ("Hacerlos crecer", "Sugerir productos complementarios y ofrecer un beneficio por llegar a su tercera compra."),
    "Nuevos": ("Lograr la 2.ª compra", "Mensaje de bienvenida y una oferta por segunda compra dentro de los 30 días siguientes."),
    "Por activar": ("Recordarles", "Recordatorio con los productos que vieron o compraron y una razón concreta para volver."),
    "En riesgo": ("Recuperarlos ya", "Mensaje personal tipo \"te extrañamos\" con una oferta limitada en el tiempo."),
    "Valiosos dormidos": ("Prioridad alta", "Contacto directo (WhatsApp o llamada) y oferta exclusiva. Son pocos y han comprado varias veces."),
    "Dormidos": ("Bajo costo", "Una campaña masiva de reactivación; si no responden, dejar de invertir en ellos."),
}
KIND = {"Campeones": "good", "Leales": "good", "Nuevos": "good", "Por activar": "warn", "En riesgo": "warn", "Valiosos dormidos": "bad", "Dormidos": "bad"}

c = c.reset_index()
c.sort_values("monto", ascending=False)[
    ["cliente_id", "ultima_compra", "recencia_dias", "frecuencia", "monto", "R", "F", "M", "segmento"]
].to_csv("clientes_rfm.csv", index=False)

tot_cli, tot_ing = len(c), c.monto.sum()
seg = c.groupby("segmento").agg(clientes=("cliente_id", "count"), ingresos=("monto", "sum"), gasto_prom=("monto", "mean"))
seg = seg.reindex(ORDEN)
seg["pct_cli"] = seg.clientes / tot_cli * 100
seg["pct_ing"] = seg.ingresos / tot_ing * 100

# Pareto: top 20% de clientes
ordenado = c.sort_values("monto", ascending=False).monto.values
acum = np.cumsum(ordenado) / ordenado.sum() * 100
top20 = acum[int(tot_cli * 0.2) - 1]

# --- Gráfico 1: % clientes vs % ingresos por segmento
fig1, ax = plt.subplots(figsize=(7.6, 4.0))
x = np.arange(len(seg))
w = 0.38
ax.bar(x - w / 2, seg.pct_cli, w, color=PALETTE["muted"], label="% de clientes")
ax.bar(x + w / 2, seg.pct_ing, w, color=PALETTE["primary"], label="% de ingresos")
ax.set_xticks(x, seg.index, rotation=30, ha="right")
ax.set_ylabel("%")
ax.set_title("Cuánto pesa cada segmento")
ax.legend(frameon=False)
ax.grid(axis="x", visible=False)

# --- Gráfico 2: mapa R x F
mapa = c.groupby(["R", "F"]).size().unstack(fill_value=0).reindex(index=[5, 4, 3, 2, 1], columns=[1, 2, 3], fill_value=0)
fig2, ax = plt.subplots(figsize=(7.6, 4.0))
im = ax.imshow(mapa.values, cmap="Blues", aspect="auto")
for i in range(mapa.shape[0]):
    for j in range(mapa.shape[1]):
        v = mapa.values[i, j]
        ax.text(j, i, f"{v:,}", ha="center", va="center", color="white" if v > mapa.values.max() * 0.55 else PALETTE["ink"], fontsize=11, fontweight="bold")
ax.set_xticks(range(3), ["1 compra", "2 compras", "3 o más"])
ax.set_yticks(range(5), ["Muy reciente (5)", "Reciente (4)", "Medio (3)", "Antiguo (2)", "Muy antiguo (1)"])
ax.set_xlabel("Frecuencia")
ax.set_title("Clientes por recencia y frecuencia")
ax.grid(False)
for s in ax.spines.values():
    s.set_visible(False)

# --- Gráfico 3: curva de concentración
fig3, ax = plt.subplots(figsize=(7.6, 3.8))
px = np.arange(1, tot_cli + 1) / tot_cli * 100
ax.plot(px, acum, color=PALETTE["primary"], lw=2.6)
ax.plot([0, 100], [0, 100], color=PALETTE["muted"], ls="--", lw=1)
ax.axvline(20, color=PALETTE["accent"], lw=1.4)
ax.scatter([20], [top20], color=PALETTE["accent"], zorder=3)
ax.annotate(f"El 20% de clientes\naporta {top20:.0f}% de ingresos", (20, top20), xytext=(33, top20 - 22), arrowprops=dict(arrowstyle="->", color=PALETTE["ink"]), fontsize=10)
ax.set_xlabel("% de clientes (de mayor a menor gasto)")
ax.set_ylabel("% acumulado de ingresos")
ax.set_title("Concentración de ingresos")

# --- Tabla del plan de acción
filas = []
for s in ORDEN:
    r = seg.loc[s]
    titulo, texto = ACCION[s]
    filas.append([f"<b>{s}</b>", f"{r.clientes:,.0f}", f"{r.pct_ing:.0f}%", money(r.gasto_prom), tag(titulo, KIND[s]), texto])
plan = table_html(["Segmento", "Clientes", "% ingresos", "Gasto promedio", "Prioridad", "Qué hacer"], filas)

en_riesgo = seg.loc[["En riesgo", "Valiosos dormidos"]]
render_dashboard(
    "tablero.html",
    "Segmentación de clientes (RFM) · Plan de acción",
    f"Tienda online · {tot_cli:,} clientes · Corte: {(snap - pd.Timedelta(days=1)):%d/%m/%Y} · Datos de ejemplo",
    kpis=[
        ("Clientes analizados", f"{tot_cli:,}"),
        ("Ingresos históricos", f"${tot_ing / 1e6:,.0f} M"),
        ("Top 20% de clientes", f"{top20:.0f}%", "de los ingresos"),
        ("Campeones", f"{seg.loc['Campeones', 'pct_cli']:.1f}%", f"de clientes · {seg.loc['Campeones', 'pct_ing']:.0f}% de ingresos"),
        ("Por recuperar", f"{en_riesgo.clientes.sum():,.0f}", f"clientes que han gastado ${en_riesgo.ingresos.sum() / 1e6:,.0f} M", "down"),
    ],
    sections=[
        {"title": "Quiénes compran y cuánto pesan", "note": "Cada cliente se clasifica por qué tan reciente compró, con qué frecuencia y cuánto gastó (RFM).", "figs": [fig1, fig2]},
        {"title": "Concentración de ingresos", "note": "Pocos clientes sostienen gran parte de las ventas: perderlos duele más que dejar de captar nuevos.", "figs": [fig3]},
        {"title": "Plan de acción por segmento", "note": "Una acción distinta para cada grupo. La lista de clientes por segmento está en clientes_rfm.csv.", "html": tabla if False else plan},
    ],
)
print(seg.round(1))
print("top20:", round(top20, 1))
