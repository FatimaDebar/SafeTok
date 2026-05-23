"""
DASHBOARD SAFETOK — Streamlit
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─── CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="SafeTok Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# ─── STYLE DARK ───────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .metric-card {
        background: #1e2130;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        border: 1px solid #2d3250;
    }
    .danger { color: #ff4b4b; font-size: 2em; font-weight: bold; }
    .safe   { color: #00cc88; font-size: 2em; font-weight: bold; }
    .title  { color: #ffffff; font-size: 1.1em; }
</style>
""", unsafe_allow_html=True)

# ─── CHARGER DONNÉES ──────────────────────────────────────
@st.cache_data
def load_data():
    scored  = pd.read_csv("data/transcriptions_scored.csv")
    rapport = pd.read_csv("data/rapport_final.csv")
    return scored, rapport

scored, rapport = load_data()

# ─── HEADER ───────────────────────────────────────────────
st.title("🛡️ SafeTok — Dashboard de Modération")
st.markdown("**Système de détection automatique de contenus dangereux sur TikTok**")
st.divider()

# ─── MÉTRIQUES PRINCIPALES ────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

total     = len(scored)
dangerous = len(scored[scored['ai_decision'] == 'DANGEROUS'])
safe      = len(scored[scored['ai_decision'] == 'SAFE'])
accuracy  = round((scored['ai_decision'] == scored['label']).sum() / total * 100, 1)

with col1:
    st.metric("📹 Total Analysé", total)
with col2:
    st.metric("🔴 Contenus Dangereux", dangerous)
with col3:
    st.metric("🟢 Contenus Safe", safe)
with col4:
    st.metric("🎯 Accuracy", f"{accuracy}%")

st.divider()

# ─── GRAPHIQUES ───────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Distribution des décisions")
    fig1 = px.pie(
        values=[dangerous, safe],
        names=['DANGEROUS', 'SAFE'],
        color_discrete_map={'DANGEROUS': '#ff4b4b', 'SAFE': '#00cc88'},
        hole=0.4
    )
    fig1.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("📊 Distribution par catégorie")
    cat_counts = scored['ai_category'].value_counts().reset_index()
    cat_counts.columns = ['Catégorie', 'Count']
    fig2 = px.bar(
        cat_counts,
        x='Catégorie', y='Count',
        color='Catégorie',
        color_discrete_map={
            'Safe'   : '#00cc88',
            'Harmful': '#ff4b4b',
            'Suicide': '#ff8800',
            'Unknown': '#888888'
        }
    )
    fig2.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        showlegend=False
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ─── DISTRIBUTION DES SCORES ──────────────────────────────
st.subheader("📈 Distribution des scores de dangerosité")
fig3 = px.histogram(
    scored, x='ai_score',
    color='ai_decision',
    color_discrete_map={'DANGEROUS': '#ff4b4b', 'SAFE': '#00cc88'},
    nbins=20,
    barmode='overlay'
)
fig3.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color='white'
)
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# ─── TOP CONTENUS DANGEREUX ───────────────────────────────
st.subheader("🚨 Top contenus dangereux détectés")

for _, row in rapport.head(10).iterrows():
    with st.expander(f"{row['priority']} | Score: {row['ai_score']}/100 | {row['video'][:50]}"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**📹 Vidéo :** {row['video']}")
            st.write(f"**🏷️ Catégorie :** {row['ai_category']}")
            st.write(f"**📊 Score :** {row['ai_score']}/100")
        with col2:
            st.write(f"**💬 Raison :** {row['ai_reason']}")
            st.write(f"**✅ Label réel :** {row['label']}")
            st.write(f"**⚡ Priorité :** {row['priority']}")

st.divider()

# ─── CONFUSION MATRIX ─────────────────────────────────────
st.subheader("🎯 Matrice de confusion")

tp = len(scored[(scored['ai_decision']=='DANGEROUS') & (scored['label']=='DANGEROUS')])
tn = len(scored[(scored['ai_decision']=='SAFE')      & (scored['label']=='SAFE')])
fp = len(scored[(scored['ai_decision']=='DANGEROUS') & (scored['label']=='SAFE')])
fn = len(scored[(scored['ai_decision']=='SAFE')      & (scored['label']=='DANGEROUS')])

fig4 = go.Figure(data=go.Heatmap(
    z=[[tp, fp], [fn, tn]],
    x=['Prédit DANGEROUS', 'Prédit SAFE'],
    y=['Réel DANGEROUS', 'Réel SAFE'],
    colorscale='RdYlGn',
    text=[[f'TP: {tp}', f'FP: {fp}'], [f'FN: {fn}', f'TN: {tn}']],
    texttemplate="%{text}",
    textfont={"size": 18}
))
fig4.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    font_color='white',
    height=350
)
st.plotly_chart(fig4, use_container_width=True)

# ─── FOOTER ───────────────────────────────────────────────
st.divider()
st.markdown("**SafeTok** — Projet RJE | ENSIAS 2026 | Pipeline : Agent1 → Agent2 → Agent3 → Agent4")