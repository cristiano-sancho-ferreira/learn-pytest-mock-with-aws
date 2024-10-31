

@echo off
REM Obtém o Account ID usando AWS CLI e armazena na variável ACCOUNT_ID
FOR /F "usebackq" %%i IN (`aws sts get-caller-identity --query Account --output text --profile devops`) DO SET ACCOUNT_ID=%%i

REM Exibe o Account ID
echo O Account ID e: %ACCOUNT_ID%


cd ..
python create_s3_bucket.py devops-%ACCOUNT_ID%-terraform-state --region=us-east-1 --profile=devops


echo Alterando AWS_PROFILE para devops: %AWS_PROFILE%
set AWS_PROFILE=devops


echo Iniciando terraform init
cd sdlf-cicd-github

terraform init

echo Iniciando terraform apply
terraform apply -auto-approve -var-file="./_variables/dev.tfvars" 
