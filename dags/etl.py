from modules.etl import extract, load, getUrl, transform, clear_xcoms
from airflow import DAG
from airflow.operators.python import PythonOperator

import pendulum
import datetime

utc_now = pendulum.now('UTC')
start_date = utc_now.in_timezone('America/Sao_Paulo')
end_date = start_date.add(days=10)

default_args = {
    "owner": "Abraao Leonardo da Silva",
    "start_date": start_date,
    "end_date": end_date,
    "retries": 1,
    "retry_delay": datetime.timedelta(seconds=1)
}

with DAG(
    dag_id="mercado_livre",
    schedule_interval="@daily",
    default_args=default_args,
    tags=["ETL_mercadolivra","csv"]
) as dag:
    
    getURL_task = PythonOperator(
        task_id="getURL",
        python_callable=getUrl,
        dag=dag
    )

    extract_task = PythonOperator(
        task_id="extract_html",
        python_callable=extract,
        dag=dag
    )
    transform_task = PythonOperator(
        task_id="transforma_product_info",
        python_callable=transform,
        dag=dag
    )

    load_task = PythonOperator(
        task_id="carrega_os_dados_em_um_arquivo_CSV",
        python_callable=load,
        dag=dag
    )

    clear_operation_task = PythonOperator(
        task_id="clear_operation",
        provide_context=True,
        python_callable=clear_xcoms,
        do_xcom_push=False,
        trigger_rule="all_done",
        dag=dag
    )

    getURL_task >> extract_task >> transform_task >> load_task >> clear_operation_task