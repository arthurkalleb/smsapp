import streamlit as st
from datetime import time
import sqlite3


def create_table():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_paciente TEXT NOT NULL,
            procedimento TEXT NOT NULL,
            contato TEXT NOT NULL,
            local_consulta TEXT NOT NULL,
            hora_consulta TEXT NOT NULL,
            parada_embarque TEXT NOT NULL,
            passagem_concedida INTEGER DEFAULT 0,
            foto_documento BLOB
        )
    ''')
    conn.commit()
    conn.close()


# Chame a função para criar a tabela
create_table()

# Isso cria ou acessa o banco de dados no mesmo diretório do seu script
conn = sqlite3.connect('database.db')


# Função para obter conexão com o banco de dados SQLite

def get_db_connection(db_path='database.db'):
    conn = sqlite3.connect(db_path)
    return conn

# Função para salvar os dados do paciente no banco de dados


def save_paciente_to_db(paciente_info):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Criar tabela se não existir
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
            foto_documento BLOB
        )
    ''')

    # Inserir dados do paciente
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

# Função para obter paradas por bairro


def get_paradas(bairro):
    paradas = {
        'Alto da Esperança': ['PSF novo', 'PSF antigo', 'Em frente a branca'],
        'Alto da esperança': ['Sesp', 'E Angicana', 'Csu', 'Verdão'],
        'Centro': ['Praça do cemitério', 'Praça do fórum', 'Prefeitura', 'Rodoviária'],
        'Alto do Triângulo': ['Batalhão', 'Fábrica da castanha', 'Canindé Felipe', 'Retorno']
    }
    return paradas.get(bairro, [])


# Inicializar sessão para armazenar estado do formulário
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

# Título principal
st.title('Agendamento de Passagens')

# Seção de dados pessoais
st.header('Dados Pessoais')
nome_paciente = st.text_input(
    'Nome do Paciente', value=st.session_state['paciente_info']['nome_paciente'])
procedimento = st.selectbox('Procedimento', ['Exame', 'Consulta'], index=[
                            'Exame', 'Consulta'].index(st.session_state['paciente_info']['procedimento']))
contato = st.text_input(
    'Contato', value=st.session_state['paciente_info']['contato'])

# Seção do local da consulta
st.header('Local da Consulta')
local_consulta = st.text_input(
    'Local da Consulta', value=st.session_state['paciente_info']['local_consulta'])
hora_consulta = st.time_input(
    'Hora da Consulta', value=st.session_state['paciente_info']['hora_consulta'])

# Seção da parada de embarque
st.header('Parada de Embarque')
bairro_embarque = st.selectbox(
    'Bairro de Embarque',
    ['Alto da Esperança', 'Alto da esperança', 'Centro', 'Alto do Triângulo'],
    index=['Alto da Esperança', 'Alto da esperança', 'Centro', 'Alto do Triângulo'].index(
        st.session_state['paciente_info']['bairro_embarque'])
)
st.session_state['paciente_info']['bairro_embarque'] = bairro_embarque

paradas = get_paradas(bairro_embarque)
parada_embarque = st.selectbox(
    'Parada de Embarque',
    paradas,
    index=paradas.index(st.session_state['paciente_info']['parada_embarque']
                        ) if st.session_state['paciente_info']['parada_embarque'] in paradas else 0
)

# Seção de upload de documento
st.header('Confirmação')
st.session_state['paciente_info']['foto_documento'] = st.file_uploader(
    "Upload da Foto do Documento", type=["jpg", "jpeg", "png"])

# Botão de confirmação
if st.button('Confirmar Agendamento'):
    if not nome_paciente or not contato or not local_consulta or st.session_state['paciente_info']['foto_documento'] is None:
        st.error(
            "Todos os campos devem ser preenchidos e o upload do documento é obrigatório.")
    else:
        st.session_state['paciente_info']['nome_paciente'] = nome_paciente
        st.session_state['paciente_info']['procedimento'] = procedimento
        st.session_state['paciente_info']['contato'] = contato
        st.session_state['paciente_info']['local_consulta'] = local_consulta
        st.session_state['paciente_info']['hora_consulta'] = hora_consulta
        st.session_state['paciente_info']['parada_embarque'] = parada_embarque
        st.session_state['paciente_info']['foto_documento'] = st.session_state['paciente_info']['foto_documento'].read()

        # Salvar no banco de dados
        save_paciente_to_db(st.session_state['paciente_info'])
        st.success('Agendamento realizado com sucesso!')
