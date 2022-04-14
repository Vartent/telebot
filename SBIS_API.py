import datetime

import requests
import json
from config import sbis_auth, sbis_auth_header, sbis_header

#API documentation links
#https://sbis.ru/help/integration/api/sequence/auth?tb=tab2
#https://sbis.ru/help/integration/api/all_methods/format
#https://sbis.ru/help/integration/api/all_methods/auth_one

def get_certificate():
    d = json.dumps(sbis_auth).encode('utf8')
    try:
        r = requests.post(
            url='https://online.sbis.ru/auth/service/',
            headers=sbis_auth_header,
            data=d.decode('utf-8')
        )
        data = r.json()
        return data['result']
    except Exception as ex:
        print(ex)


def set_task(session_id, num, id, title, slave_name, slave_lastname, slave_middlename, date=datetime.datetime.today()):

    sbis_set_task = {
        "jsonrpc": "2.0",
        "method": "СБИС.ЗаписатьДокумент",
        "params": {
            "Документ": {
                "Дата": date,
                "Номер": num,
                "Идентификатор": id,
                "Тип": "СлужЗап",
                "Регламент": {
                    "Название": title
                },
                "Ответственный": {
                    "Фамилия": slave_lastname,
                    "Имя": slave_name,
                    "Отчество": slave_middlename
                },
                "Автор": {
                    "Фамилия": slave_lastname,
                    "Имя": slave_name,
                    "Отчество": slave_middlename
                }
            }
        },
        "id": 0
    }

    sbis_header['X-SBISSessionID'] = session_id

    d = json.dumps(sbis_set_task, indent=4, sort_keys=True, default=str).encode('utf8')
    try:
        r = requests.post(
            url='https://online.sbis.ru/auth/service/',
            headers=sbis_header,
            data=d.decode('utf-8')
        )
        data = r.json()
        print(data)
        return
    except Exception as ex:
        print(ex)

if __name__ == '__main__':
    print(set_task(session_id=get_certificate(),
                   num=1,
                   id=1,
                   title='test',
                   slave_name='Камиль',
                   slave_lastname='Усманов',
                   slave_middlename='Рафаилович'))