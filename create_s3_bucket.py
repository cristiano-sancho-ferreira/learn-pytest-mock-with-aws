import boto3
from botocore.exceptions import ClientError
import argparse
import os


def create_bucket(bucket_name, region=None):
    # Cria uma sessão com a AWS S3
    s3 = boto3.client('s3')

    # Verifica se o bucket já existe
    try:

        s3.head_bucket(Bucket=bucket_name)
        print(f"O bucket '{bucket_name}' já existe.")
    except ClientError as e:
        # Se o erro for 404, o bucket não existe e podemos criá-lo
        if e.response['Error']['Code'] == '404':
            print(f"O bucket '{bucket_name}' não existe. Criando o bucket...")
            if region is None:
                os.system(f'aws s3api create-bucket --bucket {bucket_name} --region us-east-1')
            else:
                os.system(f'aws s3api create-bucket --bucket {bucket_name} --region {region}')
            print(f"Bucket '{bucket_name}' criado com sucesso.")
        else:
            print(f"Erro ao verificar o bucket '{bucket_name}': {e}")

if __name__ == "__main__":
    # Configura o parser de argumentos
    parser = argparse.ArgumentParser(description='Criar um bucket S3 na AWS.')
    parser.add_argument('bucket_name', type=str, help='Nome do bucket S3 a ser criado')
    parser.add_argument('--region', type=str, help='Região do bucket S3 (padrão: us-east-1)', default='us-east-1')

    # Obtém os argumentos da linha de comando
    args = parser.parse_args()

    print(args)

    # Chama a função para criar o bucket
    create_bucket(args.bucket_name, args.region)
