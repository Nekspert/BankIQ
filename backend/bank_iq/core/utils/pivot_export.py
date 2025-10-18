# PivotExport.py

import json
import csv

def SaveJsonToFile(response, filename):
    """Сохраняет JSON-ответ от requests в файл"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(response.json(), f, ensure_ascii=False, indent=4)
    print(f"JSON сохранён в {filename}")

def ExportDataToCSV(data):
    """Сохраняет данные в CSV (ожидается, что data — это список объектов)"""
    if not data or not hasattr(data, '__iter__'):
        print("Нет данных для экспорта.")
        return

    # Преобразуем объекты в словари
    dicts = [vars(d) for d in data if hasattr(d, '__dict__')]

    if not dicts:
        print("Пустые данные, экспорт пропущен.")
        return

    filename = "data.csv"
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=dicts[0].keys())
        writer.writeheader()
        writer.writerows(dicts)
    print(f"CSV сохранён в {filename}")
