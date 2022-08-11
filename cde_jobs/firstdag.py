# Airflow DAG
from datetime import datetime, timedelta
from dateutil import parser
import pendulum
from airflow import DAG
from cloudera.cdp.airflow.operators.cde_operator import CDEJobRunOperator
from airflow.operators.bash import BashOperator

default_args = {
        'owner': 'pauldefusco',
        'retry_delay': timedelta(seconds=5),
        'depends_on_past': False,
        'start_date': pendulum.datetime(2020, 1, 1, tz="Europe/Amsterdam")
        }

firstdag = DAG(
        'airflow-pipeline-demo',
        default_args=default_args,
        schedule_interval='@daily',
        catchup=False,
        is_paused_upon_creation=False
        )

spark_step = CDEJobRunOperator(
        task_id='sql_job_new',
        dag=firstdag,
        job_name='sql_job'
        )

shell = BashOperator(
        task_id='bash',
        dag=firstdag,
        bash_command='echo "Hello Airflow" '
        )

spark_step >> shell