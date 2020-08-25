# -*- coding: utf-8 -*- 

import pandas as pd
from pytrends.request import TrendReq
from pytrends.exceptions import ResponseError
from datetime import date, datetime, timedelta
from unidecode import unidecode
import sys
from pathlib import Path
import shutil
import re
import time
import random

def print_usage():
    '''
    Função que printa a chamada correta em caso de o usuário passar o número errado
    de argumentos
    '''

    print ('Chamada Correta: python fetch_google_trends.py <df_path> <export_path>')

def get_data_inicial(apresentacao):
    '''
    Caso a apresentação tenha sido feita em menos de 6 meses retorna a data da apre
    sentação, caso contrário, retorna a data de 6 meses atrás
    '''
    
    seis_meses_atras = date.today() - timedelta(days=180)
    if apresentacao > seis_meses_atras:
        return apresentacao.strftime('%Y-%m-%d')
    else:
        return seis_meses_atras.strftime('%Y-%m-%d')

def formata_timeframe(passado_formatado):
    '''
    Formata o timeframe para o formato aceitável pelo pytrends
    '''

    return passado_formatado + ' ' + date.today().strftime('%Y-%m-%d')

def formata_apelido(apelido):
    '''
    Formata o apelido da proposição, limitando seu conteúdo 
    para o tamanho aceitado pelo pytrends
    '''

    return apelido[:85] if not pd.isna(apelido) else ''

def formata_nome_formal(nome_formal):
    '''
    Formata o nome da proposição para não incluir o ano de 
    criação
    '''

    # Separa nome e ano
    nome_separado = nome_formal.split("/", maxsplit=1)[0]

    # Formata para MPV ser MP
    nome_separado = re.sub('MPV', 'MP', nome_separado)

    return nome_separado

def formata_keywords(keywords):
    '''
    Formata as palavtas-chave da proposição, limitando 
    seu conteúdo para o tamanho aceitado pelo pytrends
    (100 caracteres)
    '''

    formated_keywords = ''
    if not pd.isna(keywords):
        keys = keywords.split(';')
        for i in range(len(keys)):
            if len(formated_keywords) + len(keys[i]) < 100:
                formated_keywords += keys[i]
            if len(formated_keywords) < 100:
                formated_keywords += ';'
    
        if formated_keywords[-1] == ';':
            return formated_keywords[:-1]
            
    return formated_keywords

def get_trends(termos, timeframe):
    '''
    Retorna os trends
    '''
    
    pytrend.build_payload(termos, cat=0, timeframe=timeframe, geo='BR', gprop='')
 
def get_popularidade(termo, timeframe):
    '''
    Retorna a popularidade de termos passados em um intervalo de tempo
    (timeframe)
    '''

    get_trends(termo, timeframe)

    return pytrend.interest_over_time()

def calcula_maximos(pop_df, termos_base):
    '''
    Calcula o máximo de pressão entre termos principais e relacionados
    '''

    termos = pop_df

    # Calcula o máximo da pressão baseada nos termos principais
    termos['max_pressao_principal'] = termos[termos_base].max(axis=1)
    cols_names = termos_base + ['date', 'max_pressao_principal', 'isPartial']

    # Calcula o máximo de pressão baseada nos termos relacioados
    cols_termos_relacionados = termos.columns[~termos.columns.isin(cols_names)]
    termos['max_pressao_rel'] = termos[cols_termos_relacionados].max(axis=1) if (len(cols_termos_relacionados) > 0) else 0

    # calcula o máximo de pressão entre termos principais e relacionados
    termos['maximo_geral'] = termos[['max_pressao_rel','max_pressao_principal']].max(axis=1)

    return termos

def agrupa_por_semana(pop_df):
    '''
    Agrupa por semana começando na segunda e calcula os máximos das colunas
    '''

    pop_df = pop_df.reset_index()
    pop_df = pop_df.groupby(['id_ext', pd.Grouper(key='date', freq='W-MON'), 'casa', 'interesse']).agg('max')
    pop_df = pop_df.reset_index()
    pop_df['date'] = pd.to_datetime(pop_df['date']) - pd.to_timedelta(7, unit = 'd')

    return pop_df

def create_directory(export_path):
    path = Path(export_path)
    if path.exists():
        try:
            shutil.rmtree(export_path)
        except OSError as e:
            print("Erro ao esvaziar pasta destino: %s." % (e.strerror))
    
    path.mkdir(exist_ok=True)

def write_csv_popularidade(df_path, export_path):
    '''
    Para cada linha do csv calcula e escreve um csv com a popularidade da proposição
    '''

    tempo_entre_req = 60
    props_sem_popularidade = 0

    apelidos = pd.read_csv(df_path, encoding='utf-8', parse_dates=['apresentacao'])

    for index, row in apelidos.iterrows():

        # timeframe de até 6 meses da data de execução do script
        timeframe = formata_timeframe(get_data_inicial(row['apresentacao']))

        nome_formal = row['nome_formal']
        id_ext = str(row['id_ext'])
        casa = row['casa']
        id_leggo = row['id_leggo']
        interesse = row['interesse']

        # separa o nome da proposição do ano e trata MPVs
        nome_simples = formata_nome_formal(nome_formal) 
 
        # Cria conjunto de termos e adiciona aspas
        termos = [nome_simples]
        termos = ['"' + termo + '"' for termo in termos]

        # Inicializa o dataframe
        cols_names = [
                'id_leggo',
                'id_ext',
                'date',
                'casa',
                'interesse',
                nome_formal,
                'isPartial',
                'max_pressao_principal',
                'max_pressao_rel',
                'maximo_geral']

        pop_df = pd.DataFrame(columns = cols_names)

        # Tenta recupera a popularidade até 5 vezes
        for n in range(0, 5):
            try:
                print('Tentativa %s de coletar a popularidade da proposição %s da agenda %s' %(n+1, nome_formal, interesse))
                # Recupera as informações de popularidade a partir dos termos
                pop_df = get_popularidade(termos, timeframe)
                break
    
            except ResponseError as error:
                print(error.args)
                time.sleep((2 ** n) + random.random())

        # Recupera as informações de popularidade a partir dos termos
        pop_df = get_popularidade(termos, timeframe)

        # Caso da proposição sem popularidade
        if (pop_df.empty):
        
            print('Nome: %s TimeFrame: %s termos: %s sem informações do trends' %(nome_formal, timeframe, termos))
            props_sem_popularidade += 1

        else:
            print('Nome: %s TimeFrame: %s termos: %s com popularidade' %(nome_formal, timeframe, termos))

            pop_df = calcula_maximos(pop_df, termos)
            pop_df['id_leggo'] = id_leggo
            pop_df['id_ext'] = id_ext
            pop_df['casa'] = casa
            pop_df['interesse'] = interesse
            pop_df = agrupa_por_semana(pop_df)

        # Escreve resultado da consulta para uma proposição
        filename = export_path + 'pop_' + str(id_leggo) + '_' + str(interesse) + '.csv'
        pop_df.to_csv(filename, encoding='utf8', index=False)

        # Esperando para a próxima consulta do trends
        time.sleep(tempo_entre_req + random.random())

    if (props_sem_popularidade > 0):
        print('Não foi possível retornar a popularidade de %s / %s proposições' %(props_sem_popularidade, len(apelidos))) 

if __name__ == "__main__":
    # Argumentos que o programa deve receber:
    # -1º: Path para o arquivo onde estão os apelidos, nomes formais e datas de apresentações
    # -2º: Path para a pasta onde as tabelas de popularidades devem ser salvas

    if len(sys.argv) != 3:
        print_usage()
        exit(1)

    df_path = sys.argv[1]
    export_path = sys.argv[2]

    pytrend = TrendReq(timeout=(10,25))

    create_directory(export_path)

    write_csv_popularidade(df_path, export_path)

