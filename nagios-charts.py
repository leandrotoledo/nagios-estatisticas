#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sqlite3
from sys import stdout
from pygooglechart import *

# Localização do arquivo do SQLite
db_location   = 'nagios.sqlite3'

def execute_query(query):
    """
    Executa uma query e retorna uma lista de resultados
    """

    # Lista com resultados
    data = []

    # Abre conexão com banco de dados
    conn = sqlite3.connect(db_location)
    c    = conn.cursor()

    # Executa query
    c.execute(query)

    # Adiciona resultados a lista
    for row in c:
        data.append(row)

    # Fecha conexão com banco de dados
    c.close()

    # Retorna dados
    return data


def criar_grupos_de_dados(dados, grupo, limite):
    """
    Permite configurar um limite de dados mínimos para que um grupo seja independente.
    Caso o grupo não possua um valor mínimo, seu valor será somado ao nome do grupo passado por parâmetro
    """

    # Lista com novos grupos
    data = []

    # Identador do grupo passado por argumento
    i = 0

    # Para cada valor, analisar se está dentro do limite
    for value in dados:
        # Valores maiores que o limite continuam na lista
        if value[1] > limite:
            data.append(value)
        # Valores menores que o limite vão para o grupo passado por agumento
        else:
            i += value[1]

    # Adiciona o grupo a lista com novos grupos
    data.append([grupo, i])

    # Retorna dados
    return data


def grafico_todos_emails():
    """
    @ Gráfico de Barra
    QUERY: SELECT COUNT(*) FROM alerts;
    """
    stdout.write('[ GRÁFICO ] Todos os e-mails:')

    results = execute_query('SELECT COUNT(*) FROM alerts;')

    for row in results:
        #pass
        stdout.write('\t %d' % row[0])

    print

def grafico_emails_por_dia():
    """
    @ Gráfico de Linha
    QUERY: SELECT date, COUNT(*) FROM alerts GROUP BY date ORDER BY date;
    """
    stdout.write('[ GRÁFICO ] E-mails por dia:')

    results = execute_query('SELECT date, COUNT(*) FROM alerts GROUP BY date ORDER BY date;')

    datas        = []
    datas_values = []

    for row in results:
        # Formata label
        label = row[0][8:10]

        datas.append(label)
        datas_values.append(int(row[1]))

    chart = SimpleLineChart(800, 350, y_range=[0, max(datas_values)])

    chart.set_title('E-MAILS POR DIA')
    chart.add_data(datas_values)
    chart.set_colours(['A1AB84'])
    chart.fill_linear_stripes(Chart.CHART, 0, 'DDDDDD', 0.1, 'FFFFFF', 0.1)
    chart.set_grid(0, 25, 5, 5)
    left_axis    = range(0, max(datas_values) + 1, 25)
    left_axis[0] = ''
    chart.set_axis_labels(Axis.LEFT, left_axis)
    chart.set_axis_labels(Axis.BOTTOM, datas)

    chart.download('nagios-grafico_emails_por_dia.png')

    stdout.write('\t OK')
    print


def grafico_servicos():
    """
    @ Gráfico de Pizza
    QUERY: SELECT service, COUNT(*) FROM alerts GROUP BY service;
    """
    stdout.write('[ GRÁFICO ] Serviços:')

    results = execute_query('SELECT service, COUNT(*) FROM alerts GROUP BY service;')
    results = criar_grupos_de_dados(results, 'Outros', 10)

    servicos        = []
    servicos_values = []

    for row in results:
        if (row[0] != ''):
            # Formata label
            label = '''%s (%s)''' % (row[0], row[1])

            servicos.append(label)
            servicos_values.append(row[1])

    chart = PieChart2D(800, 350)

    chart.set_title('E-MAILS POR SERVIÇO')
    chart.add_data(servicos_values)
    chart.set_pie_labels(servicos)
    chart.set_colours(['A1AB84'])

    chart.download('nagios-grafico_servicos.png')

    stdout.write('\t\t OK')
    print


def grafico_servidores():
    """
    @ Gráfico de Barra
    QUERY: SELECT host, COUNT(*) FROM alerts GROUP BY host;
    """
    stdout.write('[ GRÁFICO ] Servidores:')

    results = execute_query('SELECT host, COUNT(*) FROM alerts GROUP BY host;')
    results = criar_grupos_de_dados(results, 'Outros', 25)
    results.sort()

    servidores        = []
    servidores_values = []

    for row in results:
        if (row[0] != ''):
            # Formata label
            label = '''%s (%s)''' % (row[0], row[1])

            servidores.append(label)
            servidores_values.append(row[1])

    chart = PieChart2D(800, 350)

    chart.set_title('E-MAILS POR SERVIDORES')
    chart.add_data(servidores_values)
    chart.set_legend(servidores)
    chart.set_colours(['FF0000', 'FF4500', 'FFFF00', 'A1AB84'])

    chart.download('nagios-grafico_servidores.png')

    stdout.write('\t\t OK')
    print


def grafico_tipos_de_alerta():
    """
    @ Gráfico de Linha de Área
    QUERY 1: SELECT COUNT(*) from alerts where subject LIKE '%PROBLEM%';
    QUERY 2: SELECT COUNT(*) from alerts where subject LIKE '%ACKNOWLEDGEMENT%';
    QUERY 3: SELECT COUNT(*) from alerts where subject LIKE '%RECOVERY%';
    QUERY 4: SELECT COUNT(*) from alerts where subject LIKE '%Host DOWN%';
    QUERY 5: SELECT COUNT(*) from alerts where subject LIKE '%Host UP%';
    """
    stdout.write('[ GRÁFICO ] Tipos de Alerta:')

    results = []

    problem = execute_query('''SELECT COUNT(*) from alerts where subject LIKE '%PROBLEM%';''')
    results.append(['PROBLEM', problem])

    acknowledgement = execute_query('''SELECT COUNT(*) from alerts where subject LIKE '%ACKNOWLEDGEMENT%';''')
    results.append(['ACKNOWLEDGEMENT', acknowledgement])

    recovery = execute_query('''SELECT COUNT(*) from alerts where subject LIKE '%RECOVERY%';''')
    results.append(['RECOVERY', recovery])

    hostdown = execute_query('''SELECT COUNT(*) from alerts where subject LIKE '%Host DOWN%';''')
    results.append(['Host DOWN', hostdown])

    hostup = execute_query('''SELECT COUNT(*) from alerts where subject LIKE '%Host UP%';''')
    results.append(['Host UP', hostup])

    tipos        = []
    tipos_values = []

    for row in results:
        if (row[0] != ''):
            # Formata label
            label = '''%s (%s)''' % (row[0], row[1][0][0])

            tipos.append(label)
            tipos_values.append(row[1][0][0])

    chart = PieChart2D(800, 350)

    chart.set_title('E-MAILS POR TIPOS DE ALERTA')
    chart.add_data(tipos_values)
    chart.set_legend(tipos)
    chart.set_colours(['FF0000', 'A1AB84'])

    chart.download('nagios-grafico_tipos_alerta.png')

    stdout.write('\t OK')
    print



# Gerar gráficos
grafico_todos_emails()
grafico_emails_por_dia()
grafico_servicos()
grafico_servidores()
grafico_tipos_de_alerta()
