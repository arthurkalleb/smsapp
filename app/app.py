import streamlit as st
from datetime import time
import sqlite3
import os
import pandas as pd
from PIL import Image
import io

# Configuração básica da página
st.set_page_config(
    page_title="Agendamento de Passagens",
    page_icon="🚌",
    layout="centered"
)

# CSS para aumentar o tamanho da fonte
st.markdown("""
    <style>
    .stTextInput, .stSelectbox, .stTimeInput, .stFileUploader, button {
        font-size: 1.2em;
    }
    .stButton button {
        font-size: 1.2em;
        background-color: #4CAF50;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Função para obter conexão com o banco de dados SQLite


def get_db_connection(db_path='database.db'):
    db_path = os.path.join(os.path.dirname(__file__), db_path)
    conn = sqlite3.connect(db_path)
    return conn

# Função para salvar os dados do paciente no banco de dados


def save_paciente_to_db(paciente_info):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_paciente TEXT,
            procedimento TEXT,
            contato TEXT,
            local_consulta TEXT,
            hora_consulta TEXT,
            bairro_embarque TEXT,
            parada_embarque TEXT,
            foto_documento BLOB,
            passagem_concedida INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        INSERT INTO pacientes (
            nome_paciente, procedimento, contato, local_consulta, hora_consulta,
            bairro_embarque, parada_embarque, foto_documento
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        paciente_info['nome_paciente'], paciente_info['procedimento'], paciente_info['contato'],
        paciente_info['local_consulta'], str(paciente_info['hora_consulta']),
        paciente_info['bairro_embarque'], paciente_info['parada_embarque'], paciente_info['foto_documento']
    ))
    conn.commit()
    cursor.close()
    conn.close()

# Função para garantir que a tabela será criada caso ainda não exista


def ensure_table_exists():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_paciente TEXT,
            procedimento TEXT,
            contato TEXT,
            local_consulta TEXT,
            hora_consulta TEXT,
            bairro_embarque TEXT,
            parada_embarque TEXT,
            foto_documento BLOB,
            passagem_concedida INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()


# Certificar que a tabela existe ao inicializar o app
ensure_table_exists()

# Função para obter paradas por bairro


def get_paradas(bairro):
    paradas = {
        'Alto da Esperança': ['PSF novo', 'PSF antigo', 'Em frente a branca'],
        'Alto da esperança': ['Sesp', 'E Angicana', 'Csu', 'Verdão'],
        'Centro': ['Praça do cemitério', 'Praça do fórum', 'Prefeitura', 'Rodoviária'],
        'Alto do Triângulo': ['Batalhão', 'Fábrica da castanha', 'Canindé Felipe', 'Retorno']
    }
    return paradas.get(bairro, [])

# Função para atualizar o status de passagem concedida


def update_passagem_concedida(nome_paciente, concedida):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE pacientes
        SET passagem_concedida = ?
        WHERE nome_paciente = ?
    ''', (concedida, nome_paciente))
    conn.commit()
    cursor.close()
    conn.close()

# Função para excluir um paciente pelo nome


def delete_paciente(nome_paciente):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM pacientes
        WHERE nome_paciente = ?
    ''', (nome_paciente,))
    conn.commit()
    cursor.close()
    conn.close()

# Função para exibir a imagem do documento


def get_document_image(data):
    return Image.open(io.BytesIO(data))


# Configuração de abas
abas = ["Agendar Passagem", "Administração de Agendamentos"]
aba_selecionada = st.sidebar.selectbox("Selecione a aba", abas)

if aba_selecionada == "Agendar Passagem":
    st.title('Agendamento de Passagens para Consultas e Exames')

    # Inicializar dados padrão para o formulário
    if 'paciente_info' not in st.session_state:
        st.session_state['paciente_info'] = {
            'nome_paciente': '',
            'procedimento': 'Exame',
            'contato': '(84) ',
            'local_consulta': '',
            'hora_consulta': time(9, 0),
            'bairro_embarque': 'Alto da Esperança',
            'parada_embarque': 'PSF novo',
            'foto_documento': None
        }

    # Formulário de agendamento
    st.header('Dados Pessoais')
    nome_paciente = st.text_input(
        'Nome do Paciente', value=st.session_state['paciente_info']['nome_paciente'])
    procedimento = st.selectbox('Procedimento', ['Exame', 'Consulta'], index=[
                                'Exame', 'Consulta'].index(st.session_state['paciente_info']['procedimento']))
    contato = st.text_input(
        'Contato', value=st.session_state['paciente_info']['contato'])

    st.header('Local da Consulta')
    local_consulta = st.text_input(
        'Local da Consulta', value=st.session_state['paciente_info']['local_consulta'])
    hora_consulta = st.time_input(
        'Hora da Consulta', value=st.session_state['paciente_info']['hora_consulta'])

    st.header('Parada de Embarque')
    bairro_embarque = st.selectbox('Bairro de Embarque', ['Alto da Esperança', 'Alto da esperança', 'Centro', 'Alto do Triângulo'], index=[
                                   'Alto da Esperança', 'Alto da esperança', 'Centro', 'Alto do Triângulo'].index(st.session_state['paciente_info']['bairro_embarque']))
    paradas = get_paradas(bairro_embarque)
    parada_embarque = st.selectbox('Parada de Embarque', paradas, index=paradas.index(
        st.session_state['paciente_info']['parada_embarque']) if st.session_state['paciente_info']['parada_embarque'] in paradas else 0)

    st.header('Confirmação')
    foto_documento = st.file_uploader(
        "Upload da Foto do Documento", type=["jpg", "jpeg", "png"])

    if st.button('Confirmar Agendamento'):
        if not nome_paciente or not contato or not local_consulta or foto_documento is None:
            st.error(
                "Todos os campos devem ser preenchidos e o upload do documento é obrigatório.")
        else:
            # Atualizar estado com informações do formulário
            st.session_state['paciente_info'].update({
                'nome_paciente': nome_paciente,
                'procedimento': procedimento,
                'contato': contato,
                'local_consulta': local_consulta,
                'hora_consulta': hora_consulta,
                'bairro_embarque': bairro_embarque,
                'parada_embarque': parada_embarque,
                'foto_documento': foto_documento.read()
            })

            # Salvar no banco de dados
            save_paciente_to_db(st.session_state['paciente_info'])
            st.success('Agendamento realizado com sucesso!')

elif aba_selecionada == "Administração de Agendamentos":
    st.title('📋 Administração de Agendamentos')

    # Obter todos os pacientes
    conn = get_db_connection()
    pacientes = pd.read_sql_query("SELECT * FROM pacientes", conn)
    conn.close()

    if not pacientes.empty:
        st.subheader("Lista de Agendamentos")
        st.dataframe(pacientes[['nome_paciente', 'procedimento', 'contato', 'local_consulta',
                     'hora_consulta', 'bairro_embarque', 'parada_embarque', 'passagem_concedida']])

        st.subheader("Gerenciar Agendamentos")
        paciente_nome = st.selectbox(
            "Selecione o Paciente", pacientes['nome_paciente'].unique())

        # Exibir imagem do documento do paciente selecionado
        if st.button("Ver Documento"):
            foto_documento = pacientes.loc[pacientes['nome_paciente']
                                           == paciente_nome, 'foto_documento'].values[0]
            if foto_documento:
                st.image(get_document_image(foto_documento),
                         caption="Foto do Documento")
            else:
                st.warning("Documento não disponível.")

        if st.button("Marcar como Passagem Concedida"):
            update_passagem_concedida(paciente_nome, 1)
            st.success(f"Passagem concedida para {paciente_nome}")

        if st.button("Excluir Agendamento"):
            delete_paciente(paciente_nome)
            st.success(f"Agendamento de {
                       paciente_nome} foi excluído com sucesso.")
    else:
        st.write("Nenhum agendamento encontrado.")
