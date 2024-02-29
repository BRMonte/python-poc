import csv
from datetime import datetime
from collections import defaultdict
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

class Visita:
    def __init__(self, worker_code, date_time, origin, sku, ammount_of_boxes):
        self.worker_code = worker_code
        self.date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
        self.origin = origin
        self.sku = sku
        self.ammount_of_boxes = int(ammount_of_boxes)

def group_by_date(filename):
    grouped = defaultdict(lambda: defaultdict(int))

    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            date = row['date'].split()[0]
            worker = row['worker']
            quantity = int(row['quantity'])
            grouped[date][worker] += quantity

    return grouped

def format_output(grouped):
    output = {}
    for date, workers in sorted(grouped.items()):
        output[date] = {}
        for worker, quantity in workers.items():
            output[date][worker] = quantity
    return output

@app.get("/ranking/{date}")
def ranking(date):
    grouped_data = group_by_date('./visits_example.csv')
    data = format_output(grouped_data)

    if date not in data:
        return 'Record not found: date is invalid'

    max_value = max(data[date].values())
    keys_with_max_value = [key for key, value in data[date].items() if value == max_value]

    return keys_with_max_value

grouped_data = group_by_date('./visits_example.csv')
formated_data = format_output(grouped_data)

def get_skus_by_worker_and_time(worker_code, time_interval):
    start_date, end_date = time_interval
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    skus = []
    with open('./visits_example.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row_date = datetime.strptime(row['date'].split()[0], '%Y-%m-%d')
            if row['worker'] == worker_code and start_date <= row_date <= end_date:
                skus.append(int(row['sku']))
    return skus

worker_code = 'MPUQNTC'
time_interval = ('2023-09-04', '2023-09-08')
skus = get_skus_by_worker_and_time(worker_code, time_interval)
print(' - - START - - ')
print(skus)
print(' - - END - - ')

# @app.get("/serie_temporal/{worker_code}")
# async def serie_temporal(worker_code: str, inicio: str, fim: str):
#     inicio_obj = datetime.strptime(inicio, '%Y-%m')
#     fim_obj = datetime.strptime(fim, '%Y-%m')
#     serie_temporal = {k: v for k, v in dados_agrupados.items() if k[0] == worker_code and inicio_obj <= k[1] <= fim_obj}
#     return serie_temporal

# @app.put("/atualizar_caixas/{worker_code}/{ano_mes}")
# async def atualizar_caixas(worker_code: str, ano_mes: str, ammount_of_boxes: int):
    # chave = (worker_code, ano_mes)
    # if chave in dados_agrupados:
    #     dados_agrupados[chave] = ammount_of_boxes
    #     return {"message": "Atualizado com sucesso"}
    # else:
    #     return {"message": "Chave não encontrada"}

# Para executar a aplicação FastAPI, use o comando:
# uvicorn main:app --reload
