#!/usr/bin/env python
# -*- encoding: utf-8 -*-

def open_file(location):
    """
    Abre o arquivo e retorna linhas em lista
    """

    # Lista com linhas do arquivo
    file = []

    # Abre o arquivo
    f = open(location)

    # Adiciona linhas a lista
    for line in f:
        file.append(line)

    # Fecha o arquivo
    f.close()

    return file


def split_mails(file, string):
    """
    Retorna lista com e-mails separados pela string indicada no argumento
    """

    # Lista com e-mails separados
    mails = []

    # Iterador para contar e-mails na lista
    mails_iterator = -1
    mails.append(mails_iterator)

    # Sempre que encontrar uma ocorrência de string uma nova lista será criada
    for line in file:
        index = line.find(string)
        if index != -1:
            mails_iterator += 1
            mails.append(mails_iterator)
            mails[mails_iterator] = []

        mails[mails_iterator].append(line)

    # Último item da lista é o total de e-mails
    del(mails[-1])

    return mails


def get_mail_values(mails, strings):
    """
    Retorna lista com valores indicados na lista de strings no argumento
    """

    # Lista com valores separados por e-mail
    values = []

    # Para cada e-mail, irá ser procurado nas linhas ocorrências de string
    mails_iterator = 0
    for mail in mails:
        values.append(mails_iterator)
        values[mails_iterator] = {}

        # Cria dicionário com valores vazios
        for string in strings:
            values[mails_iterator][string] = None

        for line in mail:
            for string in strings:
                # Se houver ocorrência de string irá mudar o valor dicionário
                index = line.find(string)
                if index != -1:
                    values[mails_iterator][string] = line

        mails_iterator += 1

    return values


def create_sqlite_db(db_location, find_values, values):
    """
    Cria base de dados SQLite3, requer instalação do módulo.
    TODO: esse banco não é incremental, é necessário apagá-lo para que essa função funcione
    """

    import sqlite3
    from datetime import datetime

    conn = sqlite3.connect(db_location)
    c    = conn.cursor()

    # Create table
    c.execute('''CREATE TABLE alerts (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        service TEXT,
        subject TEXT,
        date    TEXT,
        host    TEXT)''')

    # Insere um novo registro
    for list in values:
        # Valores para inserir na tabela
        data = []

        # Cada valor desta lista irá representar um campo na tabela
        for values in list.items():
            if values[1] != None:
                # TODO - Remove titulo do campo, ex.: 'Subject:'
                value = values[1].replace(values[0], '').replace(':', '').replace('\n', '').strip()
            else:
                value = ''
            data.append(value)

        # TODO - data[2] é a coluna da data, [5:16] é a parte da string que contem Dia/Mes/Ano
        data[2] = data[2][5:16]
        data[2] = datetime.strptime(data[2].strip(), "%d %b %Y")

        c.execute('INSERT INTO alerts (service, subject, date, host) VALUES (?,?,?,?)', data)

    # Save (commit) the changes
    conn.commit()

    # We can also close the cursor if we are done with it
    c.close()

    print 'Banco de dados criado com sucesso.'


# Localização do arquivo do mutt
file_location = 'nagios'

# Localização do arquivo do SQLite
db_location   = 'nagios.sqlite3'

# TODO - **Não alterar**, campos que o programa irá indexar
find_values   = ['Date:', 'Subject:', 'Host:', 'Service:']

# Abre arquivo do mutt
file   = open_file(file_location)

# Processa arquivo do mutt, dividindo e-mails
mails  = split_mails(file, 'From nagios@registro.br')

# Processa e-mails, dividindo campos
values = get_mail_values(mails, find_values)

# Cria base de dados e salva campos nela
create_sqlite_db(db_location, find_values, values)
