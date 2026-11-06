"""Étape 8 - Interface Streamlit : streamlit run app.py"""
import streamlit as st
from etape6_generation import repondre

st.set_page_config(page_title="Assistant Altéa", page_icon="📄")
st.title("📄 Assistant documentaire Altéa Services")

service = st.sidebar.selectbox("Service", ["Tous", "RH", "IT", "General"])
k = st.sidebar.slider("Nombre d'extraits (k)", 1, 10, 3)
question = st.text_input("Posez votre question :")

if st.button("Envoyer") and question.strip():
    with st.spinner("Recherche et rédaction..."):
        rep, chunks = repondre(question, k=k, service=None if service == "Tous" else service)
    st.subheader("Réponse")
    st.write(rep)
    st.subheader("Sources")
    for c in chunks:
        with st.expander(f"{c['source']} - page {c['page']} (score {c['score']})"):
            st.write(c["texte"])
