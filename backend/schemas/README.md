# Diretório de Schemas

Este diretório contém os arquivos de schema JSON utilizados pelos wrappers do sistema FORCA_V1 para validação de dados.

## Arquivos de Schema

- `schema_wrapper1.json` - Schema para validação do plano de treinamento gerado pelo Treinador Especialista
- `schema_wrapper2.json` - Schema para validação das adaptações do plano gerado pelo Sistema de Adaptação
- `schema_wrapper3.json` - Schema para validação dos dados preparados para o banco de dados pelo Distribuidor BD

## Estrutura Básica dos Schemas

Os schemas seguem o formato JSONSchema e definem a estrutura esperada para os objetos de dados manipulados por cada wrapper.

### Schema do Wrapper 1 (Treinador Especialista)

Define a estrutura do plano de treinamento principal, incluindo metadados, informações do usuário e estrutura do plano.

### Schema do Wrapper 2 (Sistema de Adaptação)

Define a estrutura do plano adaptado, incluindo o plano principal e todas as possíveis adaptações para diferentes estados do usuário.

### Schema do Wrapper 3 (Distribuidor BD)

Define a estrutura dos dados a serem enviados para o banco de dados, incluindo o mapeamento entre os campos do JSON e as tabelas do banco.