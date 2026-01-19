import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
from fpdf import FPDF
import io

# --- MOTOR DE CÁLCULO LOGÍSTICO ---
def calcular_logistica(L, W, H, d, h_bob, peso_u, permite_tumbada):
    r = d / 2
    dist_v = d * (math.sqrt(3) / 2)
    num_filas = 1 + math.floor((L - d) / dist_v)
    coords_pie = []
    for f in range(num_filas):
        offset_x = r if (f % 2 == 0) else d
        y = r + (f * dist_v)
        n_en_fila = math.floor((W - (r if f % 2 != 0 else 0)) / d)
        for i in range(n_en_fila):
            x = offset_x + (i * d)
            if x + r <= L and y + r <= W:
                coords_pie.append((x, y))
    
    total_pie = len(coords_pie)
    total_tumbadas = 0
    if permite_tumbada and (H - h_bob) >= d:
        total_tumbadas = math.floor(W / d) * math.floor(L / h_bob)
    
    return total_pie, total_tumbadas, coords_pie

# --- DISEÑO DE LA INTERFAZ ---
st.set_page_config(page_title="Carga de Bobinas", layout="wide")
st.title("🚛 Optimizador de Camión y Bobinas")

col_inp, col_vis = st.columns([1, 2])

with col_inp:
    st.header("⚙️ Datos de Entrada")
    with st.expander("Dimensiones Camión", expanded=True):
        L = st.number_input("Largo Caja (mm)", value=13600)
        W = st.number_input("Ancho Caja (mm)", value=2450)
        H = st.number_input("Alto Caja (mm)", value=2700)
        p_max = st.number_input("Carga Máx (kg)", value=24000)
    
    with st.expander("Datos Bobinas", expanded=True):
        d = st.number_input("Diámetro (mm)", value=800)
        h = st.number_input("Altura (mm)", value=1200)
        peso = st.number_input("Peso (kg)", value=500)
        tumb = st.checkbox("¿Permitir tumbadas arriba?", value=False)

# --- CÁLCULO Y RESULTADOS ---
n_pie, n_tumb, coords = calcular_logistica(L, W, H, d, h, peso, tumb)
p_total = (n_pie + n_tumb) * peso

with col_vis:
    st.subheader("📍 Mapa de Carga (Base)")
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.add_patch(patches.Rectangle((0, 0), L, W, fill=False, lw=3, color='black'))
    for cx, cy in coords:
        ax.add_patch(patches.Circle((cx, cy), d/2, color="#007bff", alpha=0.6, ec="black"))
    plt.xlim(-100, L+100); plt.ylim(-100, W+100); plt.axis('off')
    st.pyplot(fig)

    res_col1, res_col2 = st.columns(2)
    res_col1.metric("Total Bobinas", f"{n_pie + n_tumb}")
    res_col2.metric("Peso Final", f"{p_total} kg", delta=f"{p_max - p_total} kg libre")

    if p_total > p_max: st.error("❌ ¡ALERTA! EXCESO DE PESO")
    
    # --- BOTÓN PDF ---
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, "PACKING LIST", ln=1, align='C')
    pdf.set_font("Arial", '', 12); pdf.ln(10)
    pdf.cell(0, 10, f"Camión: {L}x{W}x{H} | Total: {n_pie+n_tumb} bobinas", ln=1)
    buf = io.BytesIO(); fig.savefig(buf, format='png'); pdf.image(buf, x=10, y=50, w=190)
    st.download_button("📩 Descargar Packing List PDF", data=bytes(pdf.output()), file_name="Carga.pdf", mime="application/pdf")

