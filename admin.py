import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import io

# Função para obter conexão com o banco de dados SQLite


def get_db_connection(db_path='database.db'):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Retornar resultados como dicionários
    return conn

# Função para carregar dados dos pacientes agendados


def load_pacientes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pacientes")
    pacientes = cursor.fetchall()
    conn.close()
    return pacientes

# Função para atualizar o status de uma passagem no banco de dados


def update_status_paciente(paciente_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE pacientes SET passagem_concedida = ? WHERE id = ?", (status, paciente_id))
    conn.commit()
    conn.close()


# Carregar os pacientes agendados
pacientes = load_pacientes()

# Título da página
st.title("Gestão de Passagens de Pacientes")
st.write("Gerencie as passagens concedidas, em análise ou não concedidas de maneira simples e eficiente.")

# Criar um DataFrame a partir dos dados dos pacientes
data = []
for paciente in pacientes:
    paciente_info = {
        'Nome do Paciente': paciente['nome_paciente'],
        'Procedimento': paciente['procedimento'],
        'Contato': paciente['contato'],
        'Local da Consulta': f"{paciente['local_consulta']} às {paciente['hora_consulta']}",
        'Bairro de Embarque': paciente['bairro_embarque'],
        'Parada de Embarque': paciente['parada_embarque'],
        'Status da Passagem': 'Em análise' if paciente['passagem_concedida'] == 0 else ('Concedida' if paciente['passagem_concedida'] == 1 else 'Não concedida'),
        'Foto do Documento': paciente['foto_documento'],
        'ID': paciente['id']  # Adicionar ID para referência
    }
    data.append(paciente_info)

df = pd.DataFrame(data)

# Exibir os dados em uma tabela
st.dataframe(df.drop(columns='ID'), use_container_width=True)

# Atualizar o status das passagens
for paciente in pacientes:
    # Seleção do status da passagem
    status_atual = 'Em análise' if paciente['passagem_concedida'] == 0 else (
        'Concedida' if paciente['passagem_concedida'] == 1 else 'Não concedida')
    status = st.selectbox(
        f'Status da passagem - {paciente["nome_paciente"]}',
        ['Em análise', 'Concedida', 'Não concedida'],
        index=['Em análise', 'Concedida', 'Não concedida'].index(status_atual),
        key=f'status_{paciente["id"]}'
    )

    # Botão para atualizar o status
    if st.button(f'Atualizar Status - {paciente["nome_paciente"]}', key=f'btn_{paciente["id"]}'):
        status_valor = 0 if status == 'Em análise' else (
            1 if status == 'Concedida' else 2)
        update_status_paciente(paciente['id'], status_valor)
        st.success(f'Status do paciente {
                   paciente["nome_paciente"]} atualizado para {status}.')
