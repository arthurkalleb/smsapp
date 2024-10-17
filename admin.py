import streamlit as st
import json
from datetime import datetime, timedelta
from PIL import Image
import os

# Função para carregar dados de um arquivo JSON


def carregar_dados():
    try:
        with open('dados.json', 'r') as arquivo:
            dados = json.load(arquivo)
            # Filtra dados válidos que foram registrados há menos de 48 horas
            dados_validos = [
                paciente for paciente in dados
                if datetime.now() - datetime.fromisoformat(paciente['data_registro']) < timedelta(hours=48)
            ]
            return dados_validos
    except FileNotFoundError:
        return []
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return []


# Carregar os dados dos pacientes
pacientes = carregar_dados()

# Título da página
st.title("Gestão de Passagens de Pacientes")

if pacientes:
    for paciente in pacientes:
        st.write("Dados do Paciente:")
        st.write(f"**Nome do Paciente:** {paciente['nome_paciente']}")
        st.write(f"**Procedimento:** {paciente['procedimento']}")
        st.write(f"**Contato:** {paciente['contato']}")
        st.write(f"**Local da Consulta:** {paciente['local_consulta']}")
        st.write(f"**Hora da Consulta:** {paciente['hora_consulta']}")
        st.write(f"**Parada de Embarque:** {paciente['parada_embarque']}")

        # Exibir a imagem do documento
        if os.path.exists(paciente['imagem_path']):
            imagem = Image.open(paciente['imagem_path'])
            st.image(imagem, caption='Foto do Documento',
                     use_column_width=True)
        else:
            st.warning("Imagem não encontrada.")

else:
    st.write("Nenhum dado disponível ou dados expirados.")
