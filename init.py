from airflow import DAG 
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import time
import os
from dotenv import load_dotenv
import boto3
from scrape import transform

parent_dir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(parent_dir + '/.env')
filename = os.getenv('FILENAME')
path = parent_dir + '/' + filename

default_args = {
    'owner': 'admin',
    'retries': 2,
    'retry_daily': timedelta(minutes=5)
}

def upload():
    session = boto3.Session(aws_access_key_id=os.getenv('ACCESS_KEY'), aws_secret_access_key=os.getenv('SECRET_KEY'), region_name=os.getenv('REGION_NAME'))
    s3 = session.resource('s3')
    s3.meta.client.upload_file(Filename=path, Bucket=os.getenv('BUCKET'), Key=filename)  

with DAG (
    default_args = default_args,
    dag_id = 'fetch_ebay_data',
    description = 'DAG to fetch product details from ebay best deals page',
    start_date = datetime(2024, 4, 21),
    schedule='@weekly',
    catchup=False
) as dag:
    extract_transform = PythonOperator(task_id='extract_transform', python_callable=transform)
    load = PythonOperator(task_id='load', python_callable=upload)
    extract_transform >> load