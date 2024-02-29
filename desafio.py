import csv
from datetime import datetime
from collections import defaultdict
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
from typing import Dict

app = FastAPI()
data_base = []

class Visit:
    def __init__(self, worker_code, date_time, origin, sku, ammount_of_boxes):
        self.worker_code = worker_code
        self.date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
        self.origin = origin
        self.sku = sku
        self.ammount_of_boxes = int(ammount_of_boxes)

def read_csv(filename):
    with open(filename, newline='') as csvfile:
        return list(csv.DictReader(csvfile))

ROWS = read_csv('./visits_example.csv')

def populate_visit_table():
    for row in ROWS:
        visita = Visita(
            worker_code=row['worker'],
            date_time=row['date'],
            origin=row['origin'],
            sku=row['sku'],
            ammount_of_boxes=row['quantity']
        )
    data_base.append(visita)

def group_by_date(filename):
    grouped = defaultdict(lambda: defaultdict(int))

    for row in ROWS:
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
def get_best_worker_by_date(date: str = Path(..., description="The date for which you want to get the best worker")):
    grouped_data = group_by_date('./visits_example.csv')
    data = format_output(grouped_data)

    if date not in data:
        raise HTTPException(status_code=400, detail="Record not found: date is invalid or inexistent. Use YYYY-MM-DD format")

    max_value = max(data[date].values())
    keys_with_max_value = [key for key, value in data[date].items() if value == max_value]

    return keys_with_max_value

@app.get("/skus/{worker_code}/{start_date}/{end_date}")
def get_skus_by_worker_and_date(worker_code: str = Path(..., description="The worker code"),
                                 start_date: str = Path(..., description="The start date of the period (YYYY-MM-DD)"),
                                 end_date: str = Path(..., description="The end date of the period (YYYY-MM-DD)")) -> list:
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        skus = []

        for row in ROWS:
            row_date = datetime.strptime(row['date'].split()[0], '%Y-%m-%d')
            if row['worker'] == worker_code and start_date <= row_date <= end_date:
                skus.append(int(row['sku']))

        return skus
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date: use YYYY-MM-DD format")

@app.put("/update-boxes/{worker_code}/{year}/{month}/{sku}/{quantity}")
async def update_boxes(worker_code: str, year: str, month: str, sku: str, quantity: int) -> Dict[str, str]:
    try:
        target_date = datetime.strptime(f"{year}-{month}", "%Y-%m")
        updated = False

        for row in ROWS:
            row_date = datetime.strptime(row['date'].split()[0], "%Y-%m-%d")
            if row['worker'] == worker_code and row['sku'] == sku and row_date.year == target_date.year and row_date.month == target_date.month:
                row['quantity'] = str(int(row['quantity']) + quantity)
                updated = True

        if updated:
            return {"message": f"Updated {sku} boxes for {worker_code} in {month}-{year}"}
        else:
            raise HTTPException(status_code=404, detail=f"No records found for {worker_code} with {sku} boxes in {month}-{year}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
