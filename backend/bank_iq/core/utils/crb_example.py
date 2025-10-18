from types import SimpleNamespace

import requests

from backend.bank_iq.core.utils import pivot_export as pe


print("Пример работы с API Сервиса получения данных")
BASE_URL = 'http://www.cbr.ru/dataservice'  # источник данных

# необходимо получить все параметры для основного запроса /data
# для этого последовательно получаем данные справочников


print("**** Список публикаций ****")
response = requests.get(f"{BASE_URL}/publications")
pe.SaveJsonToFile(response, "publications.json") 
publicationObject = response.json(object_hook=lambda d: SimpleNamespace(**d))

for pbl in publicationObject:
    print(f"id:{pbl.id} title:{pbl.category_name} {' - NoActive' if pbl.NoActive else ''}")

publId = -1  # id публикации
while True:
    try:
        publId = int(input("Введите id публикации:"))
        selPublItem = next((e for e in publicationObject if e.id == publId), None)
        if selPublItem is not None and not selPublItem.NoActive:
            break
        else:
            print("Данного id не существует либо раздел не может быть выбран (NoActive)")
    except ValueError:
        print("ошибка! id должен быть числом...")

print(f"Для id публикации:{publId} нужно выбрать показатель из списка")
print("**** Список показателей  ****")

responseDS = requests.get(f"{BASE_URL}/datasets?publicationId={publId}")
pe.SaveJsonToFile(response, "datasets.json")  # сохраняем данные запроса в файл (для теста)
DSObject = responseDS.json(object_hook=lambda d: SimpleNamespace(**d))

for dsItem in DSObject:
    print(f"id:{dsItem.id}, title:{dsItem.name}")

dsId = -1  # id показателя
while True:
    try:
        dsId = int(input("Введите id показателя:"))
        selDSItem = next((e for e in DSObject if e.id == dsId), None)
        if selDSItem is None:
            print("Данного id не существует")
        else:
            currentTypeVal = selDSItem.type
            break
    except ValueError:
        print("ошибка! id должен быть числом...")

print("currentTypeVal", currentTypeVal)
melId = -1  # id разреза

if currentTypeVal == 1:
    print("**** Список разрезов  ****")
    responseME = requests.get(f"{BASE_URL}/measures?datasetId={dsId}")
    pe.SaveJsonToFile(response, "measures.json") 
    MEObject = responseME.json(object_hook=lambda d: SimpleNamespace(**d)).measure
    for meItem in MEObject:
        print(f"id:{meItem.id}, title:{meItem.name}")
    while True:
        try:
            melId = int(input("Введите id разреза:"))
            selMeItem = next((e for e in MEObject if e.id == melId), None)
            if selMeItem is None:
                print("Данного id не существует")
            else:
                break
        except ValueError:
            print("ошибка! id должен быть числом...")
else:
    print("У этого показателя нет разрезов")

yaersParams = {'measureId': melId, 'datasetId': dsId}
responseYears = requests.get(f"{BASE_URL}/years", params=yaersParams)
pe.SaveJsonToFile(response, "years.json") 
yy = responseYears.json(object_hook=lambda d: SimpleNamespace(**d))[0]
print(f"\r\nИнформация доступна с {yy.FromYear} по {yy.ToYear} год")

FromYear = -1
ToYear = -1
while True:
    try:
        FromYear = int(input("Введите год начала периода:"))
        ToYear = int(input("Введите год окончания периода:"))
        if FromYear >= yy.FromYear and ToYear <= yy.ToYear:
            break
        else:
            print(f"\r\nИнформация доступна с {yy.FromYear} по {yy.ToYear} год")
    except ValueError:
        print("ошибка! год должен быть числом...")

# Далее получаем массив данных
dataParams = {'y1': FromYear, 'y2': ToYear, 'publicationId': publId, 'datasetId': dsId, "measureId": melId}
responseData = requests.get(f"{BASE_URL}/data", params=dataParams)
pe.SaveJsonToFile(responseData, "data.json") 
pe.ExportDataToCSV(responseData.json(object_hook=lambda d: SimpleNamespace(**d)))

print("All done...")
