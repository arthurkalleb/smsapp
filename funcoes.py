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
