from time import strftime
import requests
from bs4 import BeautifulSoup
import os
import datetime
import csv
from airflow.models.variable import Variable
from airflow.models import XCom




def getUrl(ti):
    url= Variable.get("url_mercadolivre")
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    container = soup.find('div', class_='items-with-smart-groups')
    if not container:
        return []

    anchors = container.find_all("a", href=True)
    links = [link['href'] for link in anchors if link['href'].startswith('https://www.mercadolivre')]
    ti.xcom_push(key='links', value=links)
    return links


def extract(ti):
    links = ti.xcom_pull(key='links', task_ids='getURL')
    data = []
    for url in links:
         content = requests.get(url).text
         data.append(content)
    print(data)
    ti.xcom_push(key='data', value=data)
    return data
    
def transform(ti):
    print("transform")
    datas = ti.xcom_pull(key='data', task_ids='extract_html')
    products = []
    for data in datas:
        body = BeautifulSoup(data, 'html.parser')
        product_name = body.find('h1', class_='ui-pdp-title').get_text()
        prices: list = body.find_all('span', class_='andes-money-amount__fraction')

    
        old_price = prices[0].get_text()
        promotional_price = prices[1].get_text()
        
        installment_price = prices[2].get_text()
        
        timestamp = strftime('%Y-%m-%d %H:%M:%S')
    
        product_info = {'product_name': product_name,
                'old_price': old_price.strip(),
                'promotional_price': promotional_price,
                'installment_price': installment_price,
                'timestamp': timestamp
                }
        products.append(product_info)
    ti.xcom_push(key='products', value=products)
    return products

def load(ti):
    print("load")
    products = ti.xcom_pull(key='products', task_ids='transforma_product_info')
    date_actual = datetime.date.today()
    directory_name = "data"
    filename = os.path.join(directory_name, f"{date_actual}.csv")

    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

    file_exists = os.path.exists(filename)

    fieldnames = ['product_name', 'old_price', 'promotional_price', 'installment_price', 'timestamp']
    
    with open(filename, mode="a", newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')

        if not file_exists:
            writer.writeheader()

        for product in products:
            print(product)
            writer.writerow(product)

def clear_xcoms(**kwargs):
    XCom.clear(dag_id=kwargs['dag'].dag_id)
    print("XComs cleared for the DAG:", kwargs['dag'].dag_id)
