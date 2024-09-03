import pytest
import pandas as pd

def setup():
    import src.generator_json_v33 as gen_json
    return_plan = gen_json.proc_planilhas("Mapeamento_TBXP0002_PDV.xlsx",
                                            "Mapping", 
                                            "C:\\Dados\\02. Treinamento\\Projeto SDLF\\learn-pytest-mock-with-aws\\app\\src\\excel")
    return return_plan


def test_proc_planilhas():
    import src.generator_json_v33 as gen_json
    return_plan = gen_json.proc_planilhas("Mapeamento_TBXP0002_PDV.xlsx",
                                            "Mapping", 
                                            "C:\\Dados\\02. Treinamento\\Projeto SDLF\\learn-pytest-mock-with-aws\\app\\src\\excel")

    assert type(return_plan) == type(dict())


def test_gera_json_light():
    import src.generator_json_v33 as gen_json
    dict_ret = setup()
    # Transforma o Dicionario de retorno em Dataframe
    df_dict_ret = pd.DataFrame(dict_ret)
    return_light = gen_json.gera_json_light(df_dict_ret,
                                            "", 
                                            "C:\\Dados\\02. Treinamento\\Projeto SDLF\\learn-pytest-mock-with-aws\\app\\src\\excel")

    assert return_light['statusCode'] == 200


def test_gera_json_heavy():
    import src.generator_json_v33 as gen_json
    dict_ret = setup()
    # Transforma o Dicionario de retorno em Dataframe
    df_dict_ret = pd.DataFrame(dict_ret)
    return_heavy = gen_json.gera_json_heavy(df_dict_ret,
                                            "C:\\Dados\\02. Treinamento\\Projeto SDLF\\learn-pytest-mock-with-aws\\app\\src\\excel")
    
    assert return_heavy['statusCode'] == 200