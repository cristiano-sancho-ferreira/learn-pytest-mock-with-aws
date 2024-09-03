

# Learn Pytest Mock with AWS
Este repositório é um guia prático para aprender a usar o Pytest junto com o Mock em ambientes AWS. Se você deseja escrever testes automatizados robustos e confiáveis para suas aplicações que utilizam serviços AWS, este é o lugar certo para começar.

## O que você encontrará aqui
* Tutoriais passo a passo sobre como usar Pytest para escrever testes unitários e de integração.
* Exemplos práticos de como aplicar mocks para simular chamadas a serviços AWS, como S3, DynamoDB, Lambda, e mais.
* Boas práticas para organizar e estruturar seus testes para garantir que sejam fáceis de manter e entender.
* Exercícios e desafios para ajudar a consolidar seu conhecimento.

## Pré-requisitos
Conhecimento básico em Python.
Familiaridade com os serviços AWS que deseja testar.
Instalação do Pytest e boto3.

## Comece agora
Siga os tutoriais, explore os exemplos e comece a testar suas aplicações AWS com confiança!


## Conteudo util e comandos
### Criar ambiente
python -m venv env_pytest

### iniciar ambiente (win32)
env_pytest\Scripts\activate

### Instala libs
pip install -r app/requirements.txt

### Executa pytest na pasta app
cd app
python -m pytest -v --cov

### Resultado do comando acima
============================================= test session starts ==============================================
platform win32 -- Python 3.12.5, pytest-8.3.2, pluggy-1.5.0 -- C:\Dados\02. Treinamento\Projeto SDLF\sdlf-datalake-sancho\pytest-lambda\env\Scripts\python.exe
e-sancho\pytest-lambda\env\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Dados\02. Treinamento\Projeto SDLF\sdlf-datalake-sancho\pytest-lambda\app
plugins: cov-5.0.0
rootdir: C:\Dados\02. Treinamento\Projeto SDLF\sdlf-datalake-sancho\pytest-lambda\app
plugins: cov-5.0.0
plugins: cov-5.0.0
collected 2 items

tests/test_app.py::test_my_function_return_double PASSED                                                  [ 50%]
tests/test_app.py::test_my_function_raise_when_x_is_not_int PASSED                                        [100%]

---------- coverage: platform win32, python 3.12.5-final-0 -----------
Name                Stmts   Miss  Cover
---------------------------------------
src\double.py           5      0   100%
tests\test_app.py      11      0   100%
---------------------------------------
TOTAL                  16      0   100%


============================================== 2 passed in 0.12s ===============================================

## links:
https://docs.pytest.org/en/stable/
