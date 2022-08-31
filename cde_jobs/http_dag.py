# Airflow DAG
from datetime import datetime, timedelta
from dateutil import parser
import pendulum
from airflow import DAG
from cloudera.cdp.airflow.operators.cde_operator import CDEJobRunOperator
from cloudera.cdp.airflow.operators.cdw_operator import CDWOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.models import Variable


default_args = {
        'owner': 'pauldefusco',
        'retry_delay': timedelta(seconds=5),
        'depends_on_past': False,
        'start_date': pendulum.datetime(2020, 1, 1, tz="Europe/Amsterdam")
        }

http_dag = DAG(
        'cde_http_dag',
        default_args=default_args,
        schedule_interval='@daily',
        catchup=False,
        is_paused_upon_creation=False
        )

spark_step = CDEJobRunOperator(
        task_id='sql_job_new',
        dag=http_dag,
        job_name='sql_job'
        )

shell = BashOperator(
        task_id='bash',
        dag=http_dag,
        bash_command='echo "Hello Airflow" '
        )

cdw_query = """
show databases;
"""

dw_step3 = CDWOperator(
    task_id='dataset-etl-cdw',
    dag=http_dag,
    cli_conn_id='cdw_connection',
    hql=cdw_query,
    schema='default',
    use_proxy_user=False,
    query_isolation=True
)


also_run_this = BashOperator(
    task_id='also_run_this',
    dag=http_dag,
    bash_command='echo "yesterday={{ yesterday_ds }} | today={{ ds }}| tomorrow={{ tomorrow_ds }}"',
)

#Custom Python Method
def _print_context(**context):
    print(context)

print_context = PythonOperator(
    task_id="print_context",
    python_callable=_print_context,
    dag=http_dag
)

foo = Variable.get("rapids_api_host")
foo_json = Variable.get("rapids_api_key", deserialize_json=True)

print(foo)
print(foo_json)

def handle_response(response):
    if response.status_code == 200:
        print("Received 2000 Ok")
        return True
    else:
        print("Error")
        return False

http_task = SimpleHttpOperator(
    task_id="chuck_norris_task",
    method="GET",
    http_conn_id="chuck_norris_connection",
    endpoint="/jokes/random",
    headers={"Content-Type":"application/json",
            "X-RapidAPI-Key": "f16c49e390msh7e364a479e33b3dp10fff7jsn6bc84b000b75",
            "X-RapidAPI-Host": "matchilling-chuck-norris-jokes-v1.p.rapidapi.com"},
    response_check=lambda response: handle_response(response),
    dag=http_dag
)

spark_step >> shell >> dw_step3 >> also_run_this >> print_context >> http_task
