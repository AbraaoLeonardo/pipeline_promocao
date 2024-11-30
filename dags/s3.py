from airflow import DAG
from airflow.operators.python import PythonOperator
import datetime

from modules.nuvem import check_and_create_bucket, upload_folder_to_s3

with DAG(
    dag_id="s3",
    schedule_interval="@daily",
    start_date=datetime.datetime(2024, 12, 1),
    catchup=False,
    tags=["ETL_mercadolivra","csv"],
    default_args={
        "owner": "Abraao Leonardo da Silva",
        "retries": 1,
        "retry_delay": datetime.timedelta(seconds=1)
    }
) as dag:

    check_and_create_bucket_task = PythonOperator(
        task_id="check_and_create_bucket",
        python_callable=check_and_create_bucket,
        dag=dag
    )

    upload_folder_to_s3_task = PythonOperator(
        task_id="upload_folder_to_s3",
        python_callable=upload_folder_to_s3,
        dag=dag
    )

    check_and_create_bucket_task >> upload_folder_to_s3_task