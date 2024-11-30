# Projeto de Data Engineering: Pipeline de Extração de Produtos em Oferta no Mercado Livre

## Visão Geral

Este projeto é uma pipeline de dados desenvolvida para realizar a extração automática de produtos em oferta no Mercado Livre a cada hora e enviar os dados extraídos para um bucket no Amazon S3 a cada dia. A pipeline é orquestrada utilizando **Apache Airflow** e implementada em **Python**, visando automação, escalabilidade e facilidade de monitoramento.

A extração é realizada por meio de web scraping no Mercado Livre. Os dados extraídos são armazenados em arquivos CSV e enviados para o **Amazon S3**, onde serão mantidos para análise e consumo posterior.

## Arquitetura

A arquitetura da pipeline é composta pelas seguintes etapas:
1. **getURL**: Coleta os links com os produtos na promoção.
2. **Extração (Extract)**: Coleta de dados do Mercado Livre, utilizando a biblioteca requests.
3. **Transformação (Transform)**: Utilzação do beautifulsoup para a extração dos dados desejados.
4. **Carregamento (Load)**: Armazenamento dos dados em um arquivo CSV com o formato 'ano-mes-dia.csv'
5. **Envio dos dados**: Uma dag executada diariamente para enviar os dados para o s3.
4. **Agendamento e Orquestração**: Utilização do Apache Airflow para orquestrar a execução da pipeline de forma automática, garantindo a extração a cada hora e o envio diário para o S3.

## Tecnologias Utilizadas

- **Apache Airflow**: Para orquestração e agendamento das tarefas.
- **Python**: Linguagem principal para implementar as lógicas de extração, transformação e carga dos dados.
- **AWS S3**: Para armazenamento dos arquivos CSV gerados.
- **Requests**: Para realizar as requisições HTTP à API do Mercado Livre.
- **beautifulsoup**: Permite o Parse do html, com isso podemos coletar as informações desejadas.

## Funcionalidades

### Extração dos Dados

A cada hora, a pipeline irá realizar o scrapy na página de promoções do [Mercado Livre](https://www.mercadolivre.com.br/ofertas) para obter os links dos produtos em oferta.  Após isso, a tarefa de extract irá colher o HTML e salvará ele em um lista.

- **Intervalo de Execução**: A cada 1 hora.
- **Formato de Dados**: list
  
### Transformação dos Dados
Após a colheta, a task de transform irá colher as informações: nome do produto, preço padrão, preço promocional, preço parcelado e o horário da coleta.

### Carregamento dos Dados

Ao final da pipeline, irá gerar um arquivo CSV que posteriormente será enviado para a S3.

### Envio dos dados


Uma vez por dia, enviará os dados para um bucket S3
- **Intervalo de Execução**: A cada 24 horas.
- **Destino**: Bucket do S3.

### Orquestração com Apache Airflow

O Apache Airflow é utilizado para agendar e monitorar as execuções das tarefas.

O Airflow garante que as tarefas sejam executadas na ordem correta e dentro dos intervalos definidos.

## Estrutura do Projeto

A estrutura do projeto é organizada da seguinte forma:

```
mercadolivre/
│
├── dags/
│   ├── main.py     # DAG do Airflow que orquestra a execução da pipeline
│   ├── modules
|       ├── etl.py  # arquivo que consiste em todas as funções utilizadas no processo de ETL.
│
├── requirements.txt                 # Dependências do projeto
├── config/
│   ├── airflow.cfg                  # Arquivo de configuração do Airflow
│
└── README.md                        # Documentação do projeto
```

## Instruções de Execução

### Pré-requisitos

1. **Instalação do docker**:
   Siga a documentação oficial do Docker para instalar o Docker em seu ambiente: [docker](https://docs.docker.com/engine/install/)

2. **Instalação das Dependências**:
   Instale as dependências do projeto via `pip`:

   ```bash
   python3 -m venv ./venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configuração do AWS S3**:
   Certifique-se de que as credenciais da AWS estão configuradas corretamente no ambiente (por exemplo, via variáveis de ambiente ou utilizando o AWS CLI).

### Executando a Pipeline

1. **Inicie o Airflow**:

   Para iniciar o airflow, iremos utilizar o docker compose. Para isso você pode executar o script com o comando:
   ```bash
   chmod +x scripts
   ./scripts
   ```

    Ou manualmente com os seguintes comandos
   ```bash
   docker compose up airflow-init
   docker compose up -d
   ```

2. **Verifique a DAG no Airflow**:

   Acesse a interface web do Airflow (`http://localhost:8080`) e execute a DAG `mercado_livre` manualmente ou aguarde a execução automatizada.

3. **Monitoramento**:

   O Airflow fornecerá logs detalhados sobre cada execução das tarefas. Acesse os logs para verificar se a extração, transformação e carga dos dados ocorreram corretamente.

## Docs
Esse projeto possui um docs feito através do mkdocs. Você consegue verificar usando o seguinte comando:

```Bash
cd docs
mkdocs build
mkdocs serve -a localhost:8005 # Change the port if necessary
```

## Contribuições

Contribuições são bem-vindas! Caso queira melhorar a pipeline ou adicionar novas funcionalidades, por favor, envie um pull request com suas alterações.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

---