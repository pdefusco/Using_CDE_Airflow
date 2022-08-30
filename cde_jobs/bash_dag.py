# Airflow DAG
from datetime import datetime, timedelta
from dateutil import parser
import pendulum
from airflow import DAG
from cloudera.cdp.airflow.operators.cde_operator import CDEJobRunOperator
from cloudera.cdp.airflow.operators.cdw_operator import CDWOperator
from airflow.operators.bash import BashOperator

default_args = {
        'owner': 'pauldefusco',
        'retry_delay': timedelta(seconds=5),
        'depends_on_past': False,
        'start_date': pendulum.datetime(2020, 1, 1, tz="Europe/Amsterdam")
        }

bash_airflow_dag = DAG(
        'bash_dag',
        default_args=default_args,
        schedule_interval='@daily',
        catchup=False,
        is_paused_upon_creation=False
        )

spark_step = CDEJobRunOperator(
        task_id='sql_job_new',
        dag=bash_airflow_dag,
        job_name='sql_job'
        )

shell = BashOperator(
        task_id='bash',
        dag=bash_airflow_dag,
        bash_command='echo "Hello Airflow" '
        )

cdw_query = """
show databases;
"""

dw_step3 = CDWOperator(
    task_id='dataset-etl-cdw',
    dag=bash_airflow_dag,
    cli_conn_id='cdw_connection',
    hql=cdw_query,
    schema='default',
    use_proxy_user=False,
    query_isolation=True
)


also_run_this = BashOperator(
    task_id='also_run_this',
    dag=bash_airflow_dag,
    bash_command='echo "yesterday={{ yesterday_ds }} | today={{ ds }}| tomorrow={{ tomorrow_ds }}"',
)

spark_step >> shell >> dw_step3 >> also_run_this
