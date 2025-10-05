import streamlit as st
from model import gerar_solucao

st.set_page_config(page_title="Aurora 🌱", layout="centered")

st.title("Aurora 🌱")
st.subheader("Sua IA para soluções ambientais")

prompt = st.text_area("Descreva seu problema ambiental:")

if st.button("Gerar solução"):
    if prompt.strip():
        with st.spinner("Pensando..."):
            resposta = gerar_solucao(prompt)
            st.success("Solução proposta:")
            st.write(resposta)
    else:
        st.warning("Por favor, digite um problema ambiental.")
