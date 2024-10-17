import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import io

# Função para obter conexão com o banco de dados SQLite


def get_db_connection(db_path='database.db'):
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Retorna resultados como dicionários
        cursor = conn.cursor()
        # Verificar se a tabela "pacientes" existe
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='pacientes';")
        table_exists = cursor.fetchone()

        if table_exists is None:
            st.error(
                "Erro: A tabela 'pacientes' não foi encontrada no banco de dados.")
            return None

        return conn

    except sqlite3.Error as e:
        st.error(f"Erro ao conectar com o banco de dados: {e}")
        return None

# Função para carregar dados dos pacientes agendados


def load_pacientes():
    conn = get_db_connection()
    if conn is None:
        return []  # Retornar lista vazia se não houver conexão
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pacientes")
    pacientes = cursor.fetchall()
    conn.close()
    return pacientes

# Função para atualizar o status de uma passagem no banco de dados


def update_status_paciente(paciente_id, status):
    conn = get_db_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE pacientes SET passagem_concedida = ? WHERE id = ?", (
            status, paciente_id)
    )
    conn.commit()
    conn.close()


# Carregar os pacientes agendados
pacientes = load_pacientes()

# Verificar se há dados dos pacientes
if pacientes:
    # Título da página
    st.title("Gestão de Passagens de Pacientes")
    st.write("Gerencie as passagens e visualize as informações e documentos enviados.")

    # Criar um DataFrame a partir dos dados dos pacientes
    data = []
    for paciente in pacientes:
        # Verificar se 'passagem_concedida' existe nos dados do paciente
        status = 'Status desconhecido'
        if 'passagem_concedida' in paciente.keys():
            status = 'Em análise' if paciente['passagem_concedida'] == 0 else (
                'Concedida' if paciente['passagem_concedida'] == 1 else 'Não concedida')

        paciente_info = {
            'Nome do Paciente': paciente['nome_paciente'],
            'Procedimento': paciente['procedimento'],
            'Contato': paciente['contato'],
            'Local da Consulta': f"{paciente['local_consulta']} às {paciente['hora_consulta']}",
            'Bairro de Embarque': paciente['bairro_embarque'],
            'Parada de Embarque': paciente['parada_embarque'],
            'Status da Passagem': status,
            'ID': paciente['id']  # ID para referência
        }
        data.append(paciente_info)

    # Exibir os dados em uma tabela
    df = pd.DataFrame(data)
    st.dataframe(df.drop(columns='ID'), use_container_width=True)

    # Opção para baixar a tabela como CSV (sem a foto do documento)
    st.download_button(
        label="Baixar Tabela (CSV)",
        data=df.drop(columns='ID').to_csv(index=False),
        file_name='pacientes_agendados.csv',
        mime='text/csv'
    )

    # Atualizar o status das passagens
    for paciente in pacientes:
        with st.expander(f"Detalhes do Paciente: {paciente['nome_paciente']}"):
            # Exibir detalhes do paciente
            st.write(f"**Procedimento:** {paciente['procedimento']}")
            st.write(f"**Contato:** {paciente['contato']}")
            st.write(
                f"**Local da Consulta:** {paciente['local_consulta']} às {paciente['hora_consulta']}")
            st.write(f"**Bairro de Embarque:** {paciente['bairro_embarque']}")
            st.write(f"**Parada de Embarque:** {paciente['parada_embarque']}")

            # Exibir a imagem do documento
            if paciente['foto_documento']:
                image = Image.open(io.BytesIO(paciente['foto_documento']))
                st.image(image, caption="Foto do Documento",
                         use_column_width=True)

            # Verificar se 'passagem_concedida' existe
            status_atual = 'Status desconhecido'
            if 'passagem_concedida' in paciente.keys():
                status_atual = 'Em análise' if paciente['passagem_concedida'] == 0 else (
                    'Concedida' if paciente['passagem_concedida'] == 1 else 'Não concedida')

            # Seleção do status da passagem
            status = st.selectbox(
                'Status da Passagem',
                ['Em análise', 'Concedida', 'Não concedida'],
                index=['Em análise', 'Concedida', 'Não concedida'].index(
                    status_atual) if status_atual != 'Status desconhecido' else 0,
                key=f'status_{paciente["id"]}'
            )

            # Botão para atualizar o status
            if st.button(f'Atualizar Status', key=f'btn_{paciente["id"]}'):
                status_valor = 0 if status == 'Em análise' else (
                    1 if status == 'Concedida' else 2)
                update_status_paciente(paciente['id'], status_valor)
                st.success(f'Status do paciente {
                           paciente["nome_paciente"]} atualizado para {status}.')
else:
    st.warning(
        "Nenhum paciente encontrado ou erro de conexão com o banco de dados.")
