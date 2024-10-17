import streamlit as st
import json
import os
from datetime import datetime
from PIL import Image

# Função para salvar dados em um arquivo JSON


def salvar_dados(dados):
    try:
        # Verifica se o arquivo já existe
        if os.path.exists('dados.json'):
            with open('dados.json', 'r') as arquivo:
                todos_dados = json.load(arquivo)
        else:
            todos_dados = []

        todos_dados.append(dados)  # Adiciona novo paciente
        with open('dados.json', 'w') as arquivo:
            json.dump(todos_dados, arquivo)
    except Exception as e:
        st.error(f"Erro ao salvar os dados: {e}")


# Interface do usuário para cadastro de paciente
st.title("Agendamento de Pacientes")

# Campos do formulário
nome_paciente = st.text_input("Nome do Paciente")
procedimento = st.selectbox("Procedimento", ["Consulta", "Exame"])
contato = st.text_input("Contato")
local_consulta = st.text_input("Local da Consulta")
hora_consulta = st.time_input("Hora da Consulta")
parada_embarque = st.selectbox(
    "Parada de Embarque", ["Centro", "Alto da Esperança", "Alto do Triângulo"])
imagem = st.file_uploader("Enviar Foto do Documento",
                          type=["jpg", "jpeg", "png"])

# Botão para enviar os dados
if st.button("Solicitar Agendamento"):
    if imagem is not None:
        imagem_path = f"imagens/{imagem.name}"  # Define o caminho da imagem
        # Cria o diretório se não existir
        os.makedirs('imagens', exist_ok=True)
        with open(imagem_path, "wb") as f:
            f.write(imagem.getbuffer())  # Salva a imagem

        dados_paciente = {
            'nome_paciente': nome_paciente,
            'procedimento': procedimento,
            'contato': contato,
            'local_consulta': local_consulta,
            'hora_consulta': str(hora_consulta),
            'parada_embarque': parada_embarque,
            'imagem_path': imagem_path,  # Adiciona o caminho da imagem
            'data_registro': datetime.now().isoformat()  # Adiciona a data de registro
        }

        salvar_dados(dados_paciente)
        st.success("Agendamento solicitado com sucesso!")
    else:
        st.warning("Por favor, envie uma imagem do documento.")
