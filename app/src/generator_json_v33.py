'''
cd C:\Dados\2.Script\Mapeamento\
python C:\Dados\2.Script\Mapeamento\generator_json_v33.py C:\Dados\2.Script\Mapeamento\Mapeamento_wave1

Instalar Anaconda
pip install xlrd==1.2.0 = Para instalar essa biblioteca tem que configura o pip config
execute "pip config list -v" para encontrar o pip.config na maquina

ai vc joga esse arquivo no global
que ai o anaconda com jupyter assume tbm
ai tu ja pode tentar rodar o pip

'''
#import boto3
import pandas as pd
import json
import logging
import xlrd
import fnmatch
import os
import sys
from time import time
from pandas import DataFrame
from typing import Dict
import re 

# 26-04-2022 - Incluido função replace para substituir traço (-) por underline (_) e tirar ponto do nome do campo. (Linha 707)
# 08-06-2022 - Incluido função replace para substituir smallint para bigint (Linha 138)

'''


SE NO JSON O "EntityType" estiver definido com o "link" e "SatelliteName" estiver vazio, não serão definidos atributos no campo "CDCColumns";
SE NO JSON O "EntityType" estiver definido com o "link" mas tiver a definição de satellite em "SatelliteName", o mesmo deverá respeitar os campos definidos em "CDCColumns";
Se o EntityType = link mas nao tem Satelite (SatelliteName), entao nao precisa alimentar CDC>
Se o TntityType - link e tem Satelite (SatelliteName), entao precisa alimentar o CDC
'''

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# List of file with exceptions to case RoleName

file_vault_exception = [

'flma509l' # MA - HubBusinessKey com problema, pois tem duas chave e coloca apenas uma

    ,'flme0002' # ME - HubBusinessKey com problema, pois tem duas chave e coloca apenas uma

    ,'flme361a' # ME - HubBusinessKey com problema, pois tem duas chave e coloca apenas uma

    ,'flme361b' # ME - HubBusinessKey com problema, pois tem duas chave e coloca apenas uma

    ,'flme362a' # ME - HubBusinessKey com problema, pois tem duas chave e coloca apenas uma

    ,'flme375a' # ME - HubBusinessKey com problema, pois tem duas chave e coloca apenas uma

    ,'flme380a' # ME - HubBusinessKey com problema, pois tem duas chave e coloca apenas uma

    ,'flme392a' # ME - HubBusinessKey com problema, pois tem duas chave e coloca apenas uma

    ,'flme393a' # ME - HubBusinessKey com problema, pois tem duas chave e coloca apenas uma

    ,'tbdr0071' # MVP

    ,'bnk803a' # NK - HubBusinessKey com problema, pois tem duas chave e coloca apenas uma

    ,'flnk800a' # NK - HubBusinessKey com problema, pois tem duas chave e coloca apenas uma

    ,'flpb720a' # PB - HubBusinessKey com problema, pois tem duas chave e coloca apenas uma

    ,'flpb721a' # PB - HubBusinessKey com problema, pois tem duas chave e coloca apenas uma

    ,'flqr0479' # QR - HubBusinessKey com problema, pois tem duas chave e coloca apenas uma

    ,'tbge0027' # Wave 1 - HubBusinessKey com problema, pois tem duas chave e coloca apenas uma

    ,'tbge0136' # Wave 1 - HubBusinessKey com problema, pois tem duas chave e coloca apenas uma (l_dmcl_bncr_age)

    ,'tbge7005' # Wave 1 - precisa separar os links em cada chave de cada RoleName

    ,'tbge0091' # Wave 2 - precisa separar os links em cada chave de cada RoleName

    ,'fltga0014' # Wave 3 - HubBusinessKey com problema, pois tem duas chave e coloca apenas uma

    ,'flge0355' # Wave 5 - HubBusinessKey com problema, pois tem duas chave e coloca apenas uma

    ,'flxb430a' # XB - HubBusinessKey com problema, pois tem duas chave e coloca apenas uma

    ,'flzp069a' # ZP - HubBusinessKey com problema, pois tem duas chave e coloca apenas uma

    ,'flzp676a' # ZP - HubBusinessKey com problema, pois tem duas chave e coloca apenas uma
    ]

# tbge0091 - Ajustado manualmente as chaves para os casos de Rolename (linha 55 a 59 do JSON)
"""
{
        "Name": "l_pdv_serv",               
        "HubName": "h_pdv",
        "RoleName": "hk_num_pdv_cntz",
        "BusinessKey": [
          "num_pdv_cntz"
        ]
      }
"""

# List of file with exceptions of the Pattern of datetime with "b d yyyy h:m:s" to dataframe Pandas
#file_pattern1 = ['tbge7004','tbge7007','tbge7009','tbge7010', 'tbtg0020','tbge7011','tbge0114','tbge0115','tbge0137', 'tbge0290']
file_pattern1 = ['tbtg0020']

# List of file with exceptions of the Pattern of datetime with "yyyyMMddHHmmssfff" and decimal with "([0-9]+\\.[0-9]+)"
# file_pattern2 = ['tbge0019']
file_pattern2 = []

# List of file with exceptions of the Pattern with decimal with "([0-9]+\\.[0-9]+)"
file_pattern3 = ['fltga0002']

# List of file with exceptions of the Pattern of datetime with "yyyy-b-d-h.m.s.f" to dataframe Pandas "2022-02-23-00.00.01.413394"
file_pattern4 = ['flma509l']


folder = os.getcwd() #'C:\\Dados\\2.Script\\Mapeamento\\'
bucket_artifact = 'redels3-sdlf-dev-us-east-1-822609617231-artifactory'


def exportar_mapeamento_consolidado():
    pasta = os.getcwd() #'C:\\Dados\\2.Script\\Mapeamento\\'
    print(pasta)
    start_letter = 'data_raw_mapeamento_'
    arquivos = os.listdir(pasta)
    arquivos_selecionados = [x for x in arquivos if x.startswith(start_letter)]
    df_full = pd.DataFrame()
    for arquivo in arquivos_selecionados:
        print(arquivo)
        df = pd.read_excel(pasta + '\\' + arquivo, index_col=0)
        df_full = pd.concat([df_full, df])    
    df_full        
    df_full.to_excel(f'{pasta}\\data_mapeamento_consolidado.xlsx')




def definir_datatype(Datatype):

    datatype = Datatype.lower().replace('[', '(').replace(']', ')').replace(';', '')

    #datatype = datatype.lower()

    # Tratamento de tipo de dados no formato numerico inteiro e decimal
    if datatype[0:7].lower() == 'decimal':    
        tipo = datatype[0:7].lower()
        value = datatype[7:].lower()
        value = re.sub(r"[\(\)]", "", value)
        value = float(re.sub(r"\,", ".", value))
        value = round(value, 2)
        
        print(f'{tipo}({str(value).replace(".",",")})')
        if int(str(value).split('.')[1]) == 0:
            Datatype = 'bigint'
        else:
            print(f"não é inteiro: {Datatype}")

    if datatype[0:6].lower() == 'number':    
        tipo = datatype[0:6].lower()
        value = datatype[6:].lower()
        value = re.sub(r"[\(\)]", "", value)
        value = float(re.sub(r"\,", ".", value))
        value = round(value, 2)
        
        print(f'{tipo}({str(value).replace(".",",")})')
        if int(str(value).split('.')[1]) == 0:
            Datatype = 'bigint'
        else:
            print(f"não é inteiro: {Datatype}")
            Datatype = datatype.replace('number', 'decimal').replace(' ', '').strip()

    if datatype[0:7].lower() == 'numeric':    
        tipo = datatype[0:7].lower()
        value = datatype[7:].lower()
        value = re.sub(r"[\(\)]", "", value)
        value = float(re.sub(r"\,", ".", value))
        value = round(value, 2)
        
        print(f'{tipo}({str(value).replace(".",",")})')
        if int(str(value).split('.')[1]) == 0:
            Datatype = 'bigint'
        else:
            print(f"não é inteiro: {Datatype}")
            Datatype = datatype.replace('numeric', 'decimal').replace(' ', '').strip()

    if datatype[0:8].lower() == 'integer':
        Datatype = 'bigint'

    if datatype[0:3].lower() == 'int':
        Datatype = 'bigint'

    if datatype[0:9].lower() == 'smallint':
        Datatype = 'bigint'

    # Tratamento de tipo de dados no formato de string
    if datatype.lower() == 'varchar':
        Datatype = 'varchar(250)'
        
    if datatype[0:8].lower() == 'varchar2':
        print(datatype)
        datatype = datatype.replace('varchar2', 'varchar').replace(' ', '').strip()
        Datatype = re.sub("\s", "", datatype)
        print(Datatype)
        
    if datatype[0:4].lower() == 'char':
        print(datatype)
        Datatype = datatype.replace('char', 'varchar').strip()
        print(Datatype)

    if datatype[0:6].lower() == 'string':
        print(datatype)
        Datatype = datatype.replace('string', 'varchar').strip()
        print(Datatype)

    # Tratamento de tipo de dados no formato de data
    if datatype[0:9].lower() == 'timestamp':
        Datatype = 'datetime' 

    return Datatype


def gera_json_heavy(data_raw: DataFrame, path):
    try:

        # Gera o arquivo JSON
        df_vault = data_raw

        df_vault

        # construction of the list containing the json header
        header = df_vault[['Dataset', 'Table', 'Filename', 'Acronym', 'EntityType', 'HubName', 'LinkName', 'ExtractionType']]
        header = header.drop_duplicates()
        header_values = header.values.tolist()

        # json fields content list construction
        bodySchema = ['Table', 'Name', 'PrimaryKey', 'CDCColumns', 'RenameColumns', 'Links', 'ExcludeColumns']
        # construção de lista do conteudo dos campos do json BusinessKey
        body = df_vault[bodySchema]
        bodyBusinessKey = body[(body["PrimaryKey"] == 1)]
        bodyBusinessKey_values = bodyBusinessKey.values.tolist()
        # construção de lista do conteudo dos campos do json ExcludeColumns
        body = df_vault[bodySchema]
        bodyExcludeColumns = body[(body["ExcludeColumns"] == 1)]
        bodyExcludeColumns_values = bodyExcludeColumns.values.tolist()
        # construção de lista do conteudo dos campos do json CDCColumns
        body = df_vault[bodySchema]

        # Verificar se tem algum CDCColuns definido na tabela, caso não tenha colocar todos os campos com CDC ativo, Exceto os campos chave e de exclusão
        print('##############################teste#########################')

        bodyCDCColumns = pd.DataFrame()
        if body["CDCColumns"].sum() > 0:
            print('Valor maior que zero')
            bodyCDCColumns = body[((body["CDCColumns"] == 1) & (body["PrimaryKey"] == 0) & (body["ExcludeColumns"] == 0))]
        else:            
            print('Valor menor que zero')            
            print(body)
            body['CDCColumns'] = 1            
            print(body)

            #body["CDCColumns"]=1
            bodyCDCColumns = body[((body["CDCColumns"] == 1) & (body["PrimaryKey"] == 0) & (body["ExcludeColumns"] == 0))]

        print(body["CDCColumns"])
        print(body["CDCColumns"].sum())

        print('##############################teste#########################')

        ####################################################################################################################################
        ####################################################################################################################################
        ####################################################################################################################################
        ####################################################################################################################################

        bodyCDCColumns_values = bodyCDCColumns.values.tolist()
        # construção de lista do conteudo dos campos do json RenameColumns
        body = df_vault[bodySchema]
        bodyRenameColumns = body[((body["RenameColumns"] != "") & (body["ExcludeColumns"] == 0))]
        #body[(body["RenameColumns"] != "") & (body["ExcludeColumns"] == 0)]
        bodyRenameColumns_values = bodyRenameColumns.values.tolist()
        # construção de lista do conteudo dos campos do json LinksColumns
        body = df_vault[bodySchema]
        bodyLinksColumns = body[(body["Links"] != "")]
        bodyLinksColumns_values = bodyLinksColumns.values.tolist()

        print(bodyRenameColumns_values)

        # scroll through header list
        for df_vault in header_values:
            lista = []
            Dataset = df_vault[0].lower().strip()
            Table = df_vault[1].lower().strip().replace("tbdw_", "")
            SourceTable = df_vault[2].lower().strip().split("_")[-1]
            Acronym = df_vault[3].upper().strip()
            ExtractionType = df_vault[7].upper().strip()


            HubName = df_vault[5].lower().strip()
            print(f'HubName: {HubName}')
            # Define o tipo de EntityType
            if HubName == '':
                HubName = 'h_' + Table
            
            # Define o tipo de EntityType
            if df_vault[4].lower().strip() == 'link':
                EntityType = df_vault[4].lower().strip()
                prefixo_EntityName = 'l_'
            elif df_vault[4].lower().strip() == 'link with satellite':
                EntityType = df_vault[4].lower().strip()
                prefixo_EntityName = 'l_'
            else:
                EntityType = 'satellite'
                prefixo_EntityName = 's_'

            LinkName = df_vault[6].lower().strip()
            print(f'LinkName: {LinkName}')
            # Define o tipo de EntityType
            if LinkName == '':
                LinkName = prefixo_EntityName + Table

            # build json header            
            if EntityType.lower() == 'satellite':
                header_json = {
                    'Dataset': Dataset,
                    'SourceTable': SourceTable,
                    'Acronym': Acronym,
                    'EntityType': EntityType,
                    'EntityName': prefixo_EntityName + Table,
                    'HubName': HubName
                }           
            elif EntityType.lower() == 'link with satellite':
                header_json = {
                    'Dataset': Dataset,
                    'SourceTable': SourceTable,
                    'Acronym': Acronym,
                    'EntityType': EntityType[:4],
                    'EntityName': LinkName,
                    'SatelliteName': 's_' + Table
                }
            else:
            # build json header only link
                header_json = {
                    'Dataset': Dataset,
                    'SourceTable': SourceTable,
                    'Acronym': Acronym,
                    'EntityType': EntityType,
                    'EntityName': LinkName
                }

            ################################################################################################
            # BusinessKey - scrolls through the columns, placing inside the "Columns" key
            list_BusinessKey = []
            for y in bodyBusinessKey_values:
                # validates if the referenced column is from the table being used
                Name = ''
                if y[0] == df_vault[1]:
                    Name = y[4].lower().strip().split('\n')[0]
                    if Name == "":         
                        Name = y[1].lower().strip()
                    # store in a library list
                    list_BusinessKey.append(Name)
            # add the list of libraries inside the fields key
            header_json['BusinessKey'] = list_BusinessKey

            ################################################################################################
            # ExcludeColumns - scrolls through the columns, placing inside the "Columns" key
            list_ExcludeColumns = []
            for y in bodyExcludeColumns_values:
                # validates if the referenced column is from the table being used
                Name = ''
                if y[0] == df_vault[1]:    
                    Name = y[1].lower().strip()
                    # store in a library list
                    list_ExcludeColumns.append(Name)
            # add the list of libraries inside the fields key
            if list_ExcludeColumns != []:
                header_json['ExcludeColumns'] = list_ExcludeColumns

            ################################################################################################
            # CDCColumns - scrolls through the columns, placing inside the "Columns" key
            list_CDCColumns = []   
            # If the extract type is INCREMENTAL they will not have CDCColumns
            if ExtractionType == 'INCREMENTAL':                
                header_json['CDCColumns'] = []
            else:
                for y in bodyCDCColumns_values:
                    # validates if the referenced column is from the table being used
                    if y[0] == df_vault[1]:                    
                        Name = y[4].lower().strip().split('\n')[0]
                        if Name == "":         
                            Name = y[1].lower().strip()
                        # store in a library list
                        list_CDCColumns.append(Name)
                # add the list of libraries inside the fields key
                if EntityType == 'satellite':
                    header_json['CDCColumns'] = list_CDCColumns
                # SE NO JSON O "EntityType" estiver definido com o "link" mas tiver a definição de satellite em "SatelliteName", 
                # o mesmo deverá respeitar os campos definidos em "CDCColumns"
                elif EntityType == 'link with satellite':
                    header_json['CDCColumns'] = list_CDCColumns
                #- SE NO JSON O "EntityType" estiver definido somente "link" e "SatelliteName" estiver vazio, 
                # não serão definidos atributos no campo "CDCColumns"
                elif EntityType == 'link':
                    header_json['CDCColumns'] = []
                else:
                    header_json['CDCColumns'] = []

            ################################################################################################
            # RenameColumns - scrolls through the columns, placing inside the "Columns" key
            list_RenameColumnsOld = []
            list_RenameColumnsNew = []
            for y in bodyRenameColumns_values:
                # validates if the referenced column is from the table being used
                if y[0] == df_vault[1]: 
                    lista = []
                    NameOld = y[1].lower().strip()           
                    NameNew = y[4].lower().strip().split('\n')[0]
                    list_RenameColumnsOld.append(NameOld)
                    list_RenameColumnsNew.append(NameNew)
            # add the list of libraries inside the fields key
            #if EntityType == 'satellite':
            if not list_RenameColumnsOld:
                header_json['RenameColumns'] = []
            else:
                header_json['RenameColumns'] = [(dict(zip(list_RenameColumnsOld, list_RenameColumnsNew)))]

            ################################################################################################
            # LinksColumns - scrolls through the columns, placing inside the "Columns" key
            # RUles of Links
            # - RoleName: Criar nome que será utilizado como alias para caso que o 
            #             relacionamento usa a mesma tabela/coluna para colunas diferentes na interface.
            #             Exemplo: Cep_ini e Cep_fim que usa a tabela CEP e precisa de dois relacionamento (tbdr0071).
            # - HubBusinessKey:  


            list_LinksColumns = []
            list_LinksColumns2 = []
            RoleNameNum = 0
            HubBusinessKey = 0
            for y in bodyLinksColumns_values:
                # validates if the referenced column is from the table being used
                if y[0] == df_vault[1]:
                    LinksBusinessKey = ''                   
                    Name = y[4].lower().strip().split('\n')[0]
                    if Name == "":         
                        Name = y[1].lower().strip()
                    LinksBusinessKey = Name

                    for link0 in y[5].lower().strip().split('\n'):
                        
                        if len(link0.split(".")) == 2:
                            dictLinks = {
                            "Name": link0.split('.')[0].strip(),   
                            "HubName": link0.split('.')[1].strip(),
                            "BusinessKey": LinksBusinessKey
                            }
                        elif len(link0.split(".")) == 4:
                            HubBusinessKey = 1
                            dictLinks = {
                            "Name": link0.split('.')[0].strip(),   
                            "HubName": link0.split('.')[1].strip(),
                            "HubBusinessKey": link0.split('.')[3],
                            "BusinessKey": LinksBusinessKey
                            }
                        else:
                            RoleNameNum = 1
                            dictLinks = {
                            "Name": link0.split('.')[0].strip(),   
                            "HubName": link0.split('.')[1].strip(),
                            "RoleName": link0.split('.')[2],
                            "BusinessKey": LinksBusinessKey
                            }
                        list_LinksColumns2.append(dictLinks)

            
            if not list_LinksColumns2:
                header_json['Links'] = []
            else:
                link1 = pd.json_normalize(list_LinksColumns2)
                link2 = link1[['Name', 'HubName']]
                link2 = link2.drop_duplicates()
                for ind2 in link2.index:
                    LinksBusinessKey=[]
                    for ind1 in link1.index:
                        if (link2['Name'][ind2] == link1['Name'][ind1]) & (link2['HubName'][ind2] == link1['HubName'][ind1]):
                            LinksBusinessKey.append(link1['BusinessKey'][ind1])                             
                                
                            if RoleNameNum == 1:
                                if not pd.isnull(link1['RoleName'][ind1]):
                                    dictLinks2 = {
                                                "Name": link2['Name'][ind2],   
                                                "HubName": link2['HubName'][ind2],
                                                "RoleName": link1['RoleName'][ind1],
                                                "BusinessKey": LinksBusinessKey
                                                    }
                                else:                        
                                    dictLinks2 = {
                                                "Name": link2['Name'][ind2],   
                                                "HubName": link2['HubName'][ind2],
                                                "BusinessKey": LinksBusinessKey
                                                }
                            elif HubBusinessKey == 1:
                                if not pd.isnull(link1['HubBusinessKey'][ind1]):
                                    dictLinks2 = {
                                                "Name": link2['Name'][ind2],   
                                                "HubName": link2['HubName'][ind2],
                                                "BusinessKey": LinksBusinessKey,
                                                "HubBusinessKey": [link1['HubBusinessKey'][ind1]]
                                                    }
                                else:                        
                                    dictLinks2 = {
                                                "Name": link2['Name'][ind2],   
                                                "HubName": link2['HubName'][ind2],
                                                "BusinessKey": LinksBusinessKey
                                                }
                            else:                        
                                dictLinks2 = {
                                            "Name": link2['Name'][ind2],   
                                            "HubName": link2['HubName'][ind2],
                                            "BusinessKey": LinksBusinessKey
                                            }                    

                    # store in a library list
                    list_LinksColumns.append(dictLinks2)

                # add the list of libraries inside the fields key
                header_json['Links'] = list_LinksColumns

            print(f"vault-{Dataset}-{SourceTable}.json")
            lista.append(header_json)

            # Exclude some file generation with exceptions
            if SourceTable not in file_vault_exception:
                # generate json file with interface information
                with open(f"{path}\\vault-{Dataset}-{SourceTable}.json", "w", encoding="utf-8") as writeJsonfile:
                    json.dump(lista, writeJsonfile, indent=2,
                            default=str, ensure_ascii=False)

        print("Gerado arquivos JSON da Heavy Transformation!")
    except Exception as ex:
        logger.error(str(ex), exc_info=True)
        ##print(file)
        raise ex


def gera_json_light(data_raw: DataFrame, nm_final_arq, path):
    try:
        # Gera o arquivo JSON
        x = data_raw
   

        # Lista com o Header do arquivo Json
        header = x[['Dataset', 'Table', 'Acronym', 'FileType', 'Filename', 'ExtractionType', 'Delimiter', 'Frequency', 'Description', 'ForceEngineGlue']]
        #               0           1            2            3            4               5              6            7            8               9
        header = header.drop_duplicates()
        header_values = header.values.tolist()

        # Lista com os Detalhes do arquivo Json
        body = x[['Table', 'Id', 'Name', 'Datatype', 'Description_1', 'PrimaryKey', 'PatternValue']]
        #               0         1      2         3            4                5       6
        body = body.drop_duplicates()
        body_values = body.values.tolist()

        x["Description"].fillna("Não definida", inplace=True)
        x["Description_1"].fillna("Não definida", inplace=True)
        x["Dataset"].fillna("Não definida", inplace = True) 
		
        # Gerando o Header do arquivo Json
        for x in header_values:
            lista = []
            Dataset = x[0].lower().strip()
            Table = x[4].lower().strip().split("_")[-1]
            Acronym = x[2].upper().strip()
            EntityType = x[3].lower().strip() 
            Filename = x[4].upper().strip()
            ExtractionType = x[5].lower().strip()
            if Table == 'tbge0020':
                SkipHeaderRows = '1'
            else:
                SkipHeaderRows = '1'
            Delimiter = x[6]
            Frequency = x[7].lower().strip()
            Description = x[8].capitalize().strip().replace('\n',' ').replace('\r','')            
            ForceEngineGlue = x[9]

            if ForceEngineGlue != 1:
                ForceEngineGlue = 'false'
            else:
                ForceEngineGlue = 'true'


            if Delimiter == '\\t':
                print(f"Delimitador é igual a {Delimiter}")
                Delimiter = '\t'

            # Header do Json
            header_json = {
                'Dataset': Dataset,
                'SourceTable': Table,
                'Acronym': Acronym,
                'EntityType': EntityType,
                'Filename': Filename,
                'ExtractionType': ExtractionType,
                'SkipHeaderRows': SkipHeaderRows,
                'Delimiter': Delimiter,
                'Frequency': Frequency,
                'Description': Description,
                'ForceEngineGlue': ForceEngineGlue
            }

            # Percorre as colunas gerando a Chave
            list_of_dic = []
            column_id = 0
            for y in body_values:
                column_id = column_id + 1
                # valida se a coluna referenciada pertence a tabela utilizada
                if y[0] == x[1]:
                    Id = y[1]
                    Name = y[2].lower().strip()
                    Datatype = y[3].lower().strip().replace('integer','int').replace('\s','')
                    Description = y[4].capitalize().strip().replace('\n',' ').replace('\r','')
                    PrimaryKey = y[5]
                    if Datatype in ['int', 'bigint']:
                        Pattern = '([0-9]+)'
                    elif ((Filename.lower().split("_")[-1] in file_pattern1) & (Datatype in ['datetime'])):
                        Pattern = 'b d yyyy h:m:s'
                    elif ((Filename.lower().split("_")[-1] in file_pattern2) & (Datatype in ['datetime'])):
                        Pattern = 'yyyyMMddHHmmssfff'
                    elif ((Filename.lower().split("_")[-1] in file_pattern4) & (Datatype in ['datetime'])):
                        Pattern = 'yyyy-b-d-h.m.s.f'
                    elif ((Filename.lower().split("_")[-1] in file_pattern2) & (Datatype[0:7] in ['decimal'])):
                        Pattern = '([0-9]+\\.[0-9]+)'
                    elif ((Filename.lower().split("_")[-1] in file_pattern3) & (Datatype[0:7] in ['decimal'])):
                        Pattern = '([0-9]+\\.[0-9]+)'
                    elif Datatype in ['date']:
                        Pattern = y[6]
                    else:
                        Pattern = y[6]
                    # Gerando o corpo do arquivo Json
                    body_json = {
                        'Id': str(column_id),
                        'Name': Name,
                        'Datatype': Datatype,
                        'Description': Description,
                        'PrimaryKey': PrimaryKey,
                        'Pattern': Pattern
                    }
                    if str(column_id) != Id:
                        raise Exception("The quantity of columns of the file " + Filename + " from DataFrame is different of the JSON Landing Zone definition")
                    # Gera Lista de Biblioteca
                    list_of_dic.append(body_json)
                # Adiciona a lista de bibliotecas a chave dos campos
            header_json['Columns'] = list_of_dic
            Filename = Filename.lower().split("_")[-1]

            print(
                'Arquivo ' + f"raw-{Dataset}-{Filename}{nm_final_arq}.json" + ' gerado')
            lista.append(header_json)

            print("Grava o arquivo Json com informações de interface")
            # Grava o arquivo Json com informações de interface
            with open(f"{path}\\raw-{Dataset}-{Filename}{nm_final_arq}.json", "w", encoding="utf-8") as writeJsonfile:
                json.dump(lista, writeJsonfile, indent=3, 
                          default=str, ensure_ascii=False)

    except Exception as ex:
        logger.error(str(ex), exc_info=True)
        print(file)
        raise ex


def proc_planilhas(plan_in, sheet_in, path) -> Dict[str, DataFrame]:
    try:
        dataset = ''
        table = ''
        filename = ''
        acronym = ''
        filetype = ''
        extraction = ''
        delimiter = ''
        frequency = ''
        description = ''
        entitytype = ''
        val_id = ''
        name = ''
        datatype = ''
        primarykey = ''
        description_1 = ''
        nome_logico = ''
        renamecolumns = ''
        linkscolumns = ''
        cdcolumns = ''
        hubname = ''
        linkname = ''
        excludecolumns = ''
        forceengineglue = ''
        pattern_value = ''


        path_proc = path + '/' + plan_in
        #path_proc = 'C:/Users/740886/Documents/Rede/AWS_Desenv/Planilhas_modelagem/JSON/' + plan_in
        #print('Planilha a ser processada {} '.format(path_proc))
        inputWorkbook = xlrd.open_workbook(path_proc)
        linha_ok = False
        processa_aba = True
        array_plan = []

        # Lista todas as Abas da Planilha em Processamento
        sheet_names = inputWorkbook.sheet_names()
        #print('sheet_name = {}'.format(sheet_names))

        # Verifica se Aba a ser processada existe na Planilha
        if sheet_in not in sheet_names:
            processa_aba = False
            print('Aba {} Inexistente na Planilha {} '.format(sheet_in, plan_in))

        if not processa_aba:
            plan_dict = {}
            return plan_dict
        else:
            inputSheet = inputWorkbook.sheet_by_name(sheet_in)
            coluna_inicial = 0
            for row in range(inputSheet.nrows):
                for col in range(inputSheet.ncols):
                    # Encontra Coluna Final e linha inicial de Pesquisa
                    if (inputSheet.cell(row, col)).value == 'Aplicar CDC':
                        linha = row
                        coluna_final = col

            print('=================================================================================================================')
            print('Processando Planilha {} a partir da linha {} ,coluna Inicial {} e coluna Final {}'.format(plan_in, linha, coluna_inicial, coluna_final))
            print('=================================================================================================================')
            array_id = []
            array_name = []
            array_datatype = []
            array_description_1 = []
            array_nome_logico = []
            array_primarykey = []
            array_renamecolumns = []
            array_linkscolumns = []
            array_cdcolumns = []
            array_hubname = []
            array_linkname = []
            array_excludecolumns = []
            array_final = []
            array_pattern_value = []

            for row in range(inputSheet.nrows):
                val_id = ''
				# changed here
                excludecolumn = 0

                for col in range(inputSheet.ncols):
                    # Grava Atributos Unicos
                    v_col_name = str(inputSheet.cell(row, col).value)
                    # Retira Espaços a Direita
                    v_col_name = str.rstrip(v_col_name)
                    if v_col_name == 'dataset:':
                        dataset = inputSheet.cell(row, col+1).value
                    elif v_col_name == 'table:':
                        table = inputSheet.cell(row, col+1).value
                    elif v_col_name == 'filename:':
                        filename = inputSheet.cell(row, col+1).value
                    elif v_col_name == 'acronym:':
                        acronym = inputSheet.cell(row, col+1).value
                    elif v_col_name == 'type:':
                        filetype = inputSheet.cell(row, col+1).value
                    elif v_col_name == 'extraction:':
                        extraction = inputSheet.cell(row, col+1).value
                    elif v_col_name == 'delimiter:':
                        delimiter = inputSheet.cell(row, col+1).value
                    elif v_col_name == 'frequency :':
                        frequency = inputSheet.cell(row, col+1).value
                    elif v_col_name == 'description :':
                        description = inputSheet.cell(row, col+1).value
                    elif v_col_name == 'Entity Type:':
                        entitytype = inputSheet.cell(row, col+1).value
                        print(row, col)
                    elif v_col_name == 'Hub Name:':
                        hubname = inputSheet.cell(row, col+1).value
                    elif v_col_name == 'Link Name:':
                        linkname = inputSheet.cell(row, col+1).value
                    elif v_col_name == 'Force Engine Glue:':
                        forceengineglue = inputSheet.cell(row, col+1).value

                    # Grava Dicionario somente com as Linhas e Colunas que interessam
                    if (col <= coluna_final and row >= linha):
                        v_val = str(inputSheet.cell(row, col).value)
                        # Retira Espaços a Direita
                        v_val = str.rstrip(v_val)
                        v_val = v_val.replace('.0', '')
                        if (col == 0 and inputSheet.cell(row, col).value == ""):
                            linha_ok = False
                            print('Linha {} Coluna {} valor {}'.format(row,col,v_val))
                        elif (col == 0 and inputSheet.cell(row, col).value == "#"):
                            linha_ok = True
							# changed here
                            mapping_header_row = row
                            print('Linha {} Coluna {} valor {}'.format(row,col,v_val))
                        else:
							# changed here
                            column_name = str(inputSheet.cell(mapping_header_row, col).value)
                            print('Linha {} Coluna {} header {} valor {}'.format(row,col,column_name,v_val))
                            if col == 0:
                                val_id = v_val
                            elif column_name=='Campo': # col == 1:
                                name = v_val.replace("-","_").replace(".","")
                            elif column_name=='Descrição': # col == 4:
                                description_1 = v_val
                            elif column_name=='Nome Lógico': # col == 2:
                                nome_logico = v_val
                            elif column_name=='Tipo Dado': # col == 3:
                                datatype = definir_datatype(v_val.replace(';', ''))
                            elif (column_name=='Renomear para') | (column_name=='Renomear'): # col == 6:
                                renamecolumns = v_val
                            elif column_name=='Excluir': # col == 6:
                                if v_val.upper() == 'SIM':
                                    excludecolumn = 1
                                else:
                                    excludecolumn = 0
                            elif column_name=='Pattern': # col == 8:
                                pattern_value = v_val
                            elif column_name=='Business Key': # col == 9:
                                if v_val.upper() == 'SIM':
                                    primarykey = 1
                                else:
                                    primarykey = 0
                            elif (column_name =='Link.Hub Relacionado') | (column_name =='Hub Relacionado'): # col == 8:
                                linkscolumns = v_val
                            elif column_name=='Aplicar CDC': # col == 9:
                                print(f"Sancho extraction {extraction}")
                                if v_val.upper() == 'SIM':
                                    cdcolumns = 1
                                else:
                                    cdcolumns = 0

                            '''
                            print('Linha {} Coluna {} valor {}'.format(row,col,v_val))
                            if col == 0:
                                val_id = v_val
                            elif col == 1:
                                name = v_val
                            elif col == 3:
                                datatype = definir_datatype(v_val.replace(';', ''))
                            elif col == 4:
                                description_1 = v_val
                            elif col == 6:
                                renamecolumns = v_val
                            elif col == 7:
                                if v_val.upper() == 'SIM':
                                    primarykey = 1
                                else:
                                    primarykey = 0
                            elif col == 8:
                                linkscolumns = v_val
                            elif col == 9:
                                if v_val.upper() == 'SIM':
                                    cdcolumns = 1
                                else:
                                    cdcolumns = 0
                            '''
                # Gera os Arrays com os conteudos das linhas

                # Verifica se o valor é numerico
                if val_id.isdigit():
                    array_id.append(val_id)
                    array_name.append(name)
                    array_datatype.append(datatype)
                    if primarykey == 1:
                        array_description_1.append(description_1[0:240])
                        array_nome_logico.append(nome_logico[0:240])
                    else:
                        array_description_1.append(description_1[0:255])
                        array_nome_logico.append(nome_logico[0:255])
                    array_primarykey.append(primarykey)
                    array_renamecolumns.append(renamecolumns)
                    array_excludecolumns.append(excludecolumn)
                    array_linkscolumns.append(linkscolumns)
                    array_cdcolumns.append(cdcolumns)
                    array_pattern_value.append(pattern_value)
                    #print('val_id {} name {} datatype {} description_1 {} primarykey {}'.format(val_id,name,datatype,description_1,primarykey))

                print('valores => {} = {} = {} = {} = {} = {} = {} = {} = {}'.format(dataset,table,filename,acronym,filetype,extraction,delimiter,frequency,entitytype,hubname,linkname,forceengineglue))
                print(array_id)
                print('**********************')
                print(array_name)
                print('**********************')
                print(array_datatype)
                print('**********************')
                print(array_description_1)
                print('**********************')
                print(array_nome_logico)
                print('**********************')
                print(array_primarykey)
                print('**********************')
                print(array_renamecolumns)
                print('**********************')
                print(array_excludecolumns)
                print('**********************')
                print(array_linkscolumns)
                print('**********************')
                print(array_cdcolumns)
                print('**********************')
                print(array_pattern_value)

                print(' CRIANDO Dicionario 2')

            array_final = [str(x) for x in zip(array_id, array_name, array_datatype, array_description_1, array_nome_logico, array_primarykey, array_renamecolumns, array_linkscolumns, array_cdcolumns, array_pattern_value)]
            plan_dict = {'Dataset': dataset, 'Table': table, 'Acronym': acronym, 'FileType': filetype, 'Filename': filename, 'ExtractionType': extraction, 
                         'Delimiter': delimiter, 'Frequency': frequency, 'Description': description[0:255], 'EntityType': entitytype, 'HubName': hubname, 'LinkName': linkname, 'ForceEngineGlue': forceengineglue,
                         'Id': array_id, 'Name': array_name, 'Datatype': array_datatype, 'Description_1': array_description_1, 'Nome_logico': array_nome_logico, 'PrimaryKey': array_primarykey, 
                         'RenameColumns': array_renamecolumns, 'Links': array_linkscolumns, 'CDCColumns': array_cdcolumns, 'ExcludeColumns': array_excludecolumns, 'PatternValue': array_pattern_value}
            print(f'plan_dict: {plan_dict}')
            return plan_dict

    except Exception as ex:
        logger.error(str(ex), exc_info=True)
        #raise ex



#################################
'''
def selected_files(folder_files, files, layer1, layer2):
    selected_files_raw = [x for x in files if x.endswith('.json') & x.startswith(layer1)]
    print(selected_files_raw)

    for file in selected_files_raw:
        print(file)

        path_file = f'{folder_files}//{file}'
        path_file_s3 = f'governance/metadata/{layer2}_transformation/analytics/ingestion/{file.split("-")[1]}/{file}'
        result = upload_file_artifactory(path_file, bucket_artifact, path_file_s3)
        if result:
            print(result)
    return result


def upload_file_artifactory(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return f'Arquivos {object_name} copiado para S3'
'''
#########################################


def main() -> None:
    try:
        print(f"sys.argv {len(sys.argv)}: {sys.argv}")
        if len(sys.argv) != 2:
            raise Exception("Wrong number of arguments")

        start_time: float = time()

        file_pattern = 'Mapeamento_*.xls*'
        path = sys.argv[1]

        df_dict_ret_full = pd.DataFrame()
        # Vare o diretório listando todos as planilhas a serem processadas        

        caminhos = [os.path.join(path, nome) for nome in os.listdir(path)]
        arquivos = [arq.split('\\')[-1] for arq in caminhos if os.path.isfile(arq)]
        print(arquivos)
        
        for filenames in arquivos:
            filename = []
            filename.append(filenames.split('\\')[-1]) 
            planilhas = fnmatch.filter(filename, file_pattern)
            print(planilhas)

            if planilhas:
                for file in planilhas:
                    print(f'============= Inicio {file} ================')
                    # Gera arquivo da Aba Mapping
                    dict_ret = proc_planilhas(file, 'Mapping', path)
                    print('============= Dicionario retorno ================')
                    print(dict_ret)
                    # Transforma o Dicionario de retorno em Dataframe
                    df_dict_ret = pd.DataFrame(dict_ret)
                    print(df_dict_ret)
                    df_dict_ret = df_dict_ret.loc[df_dict_ret['Name'] != '']
                    print(
                        '============= Dataframe transformado retorno ================')
                    print(df_dict_ret)
                    df_dict_ret_full = pd.concat([df_dict_ret_full, df_dict_ret]) 

                    # Consolidar as informações das planilhas num unico arquivo
                    wave = path.split('\\')

                    print(df_dict_ret_full.dtypes)
                    print("##################################")
                    print(wave[-1].lower().replace('mapeamento_',''))
                    df_dict_ret_full['fase'] = wave[-1].lower().replace('mapeamento_','')
                    df_dict_ret_full.to_excel(f'data_raw_{wave[-1].lower()}.xlsx')

                    #df_dict_ret_full.to_csv(f'data_raw_{wave[-1].lower()}.csv', encoding='utf-8')



                    proc_json = gera_json_light(df_dict_ret, '', path)
                    gera_json_heavy(df_dict_ret, path)

                    # Gera arquivo da Aba Mapping_2 (Segundo arquivo da tabela, Caso Exista)
                    dict_ret_2 = proc_planilhas(file, 'Mapping_2', path)

                    # verifica se o Dicionario possui elementos, estará vazio se Aba não Existir na Planilha
                    if len(dict_ret_2) > 0:
                        # Transforma o Dicionario de retorno em Dataframe
                        df_dict_ret_2 = pd.DataFrame(dict_ret_2)
                        proc_json_2 = gera_json_light(df_dict_ret_2, '_2', path)
                        gera_json_heavy(df_dict_ret_2, path)
                    print(f'============= Finalizado {file} ================')

        # Subir JSON para AWS
        '''
        print(f'==================Subir JSON para AWS=====================')
        #uploadJSON = input(f'Deseja fazer upload dos JSON (S/N):')
        uploadJSON = 'N'
        if uploadJSON.upper()=='S':
            print("Upload Arquivos JSON")
            # listar arquivos da pasta
            folder_files = f'{path}'
            files = os.listdir(folder_files)
            print('Em execução...')

            result = selected_files(folder_files, files, 'raw', 'light')
            print(result)
        
            result = selected_files(folder_files, files, 'vault', 'heavy')
            print(result)

'''
        print(f"Time elapsed: {time() - start_time} seconds")

    except Exception as ex:
        logger.error(str(ex), exc_info=True)
        print(f'Erro: {file} - {ex}')
        
    
if __name__ == "__main__":
    main()
    #exportar_mapeamento_consolidado()
