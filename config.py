import datetime

import requests
from flask import Flask, request
import json


BOT_TOKEN="5253553025:AAHgYh1yp19l2YZfl02vEkCNk_YijSpcYDI"
URL="https://2a42-91-225-78-93.ngrok.io"

sbis_url = 'https://online.sbis.ru/service/?srv=1'
# url = requests.get("http://127.0.0.1:4041/inspect/http", 'html.parser')

states = {
    'reg':
        {'lastname': 'фамилия',
         'name': 'имя',
         'middlename': 'отчество',
         'position': 'должность',
         'departament': 'отдел',
         'phone': 'телефон'
         }
}

reg_attr = {
    'position':
        ["Исполнительный директор",
         "Директор по строительству",
         "Директор по финансам",
         "Главный инженер",
         "Руководитель проекта",
         "Начальник участка",
         "Прораб",
         "Мастер",
         "Офис-менеджер"
         "Сотрудник СДО",
         "Сотрудник ПТО",
         "Сотрудник ОМТС",
         "Сотрудник ПЭО",
         "Сотрудник ООТиТБ",
         "Сотрудник ОК"],
    'departament':
        ["ЖК Атмосфера",
         "ЖК Беседа",
         "ЖК Беседа ПАРКИНГ",
         "ЖК Волшебный сад",
         "ЖК Лето",
         "ЖК Лето",
         "ЖК Радужный",
         "ЖК МФЦ Сибгата Хакима",
         "ЖК Уникум",
         "ЖК Царево",
         "Офис"]
}

sbis_login = "amanatbot"
sbis_password = "sKamInutik2536eRu-116-dfwg3h6d3"

sbis_auth = {
   "jsonrpc": "2.0",
   "method": "СБИС.Аутентифицировать",
   "params": {
      "Параметр": {
          "Логин": sbis_login,
          "Пароль": sbis_password
      }
   },
   "id": 0
}

sbis_set_task = {
    "jsonrpc": "2.0",
    "method": "СБИС.ЗаписатьДокумент",
    "params": {
        "Документ": {
            "Дата": None,
            "Номер": None,
            "Идентификатор": None,
            "Тип": "СлужЗап",
            "Регламент": {
                "Название": None
            },
            "Ответственный": {
                "Фамилия": None,
                "Имя": None,
                "Отчество": None
            },
            "Автор": {
                "Фамилия": None,
                "Имя": None,
                "Отчество": None
            }
        }
    },
    "id": 0
}


sbis_auth_header = {
 "Content-Type": "application/json-rpc;charset=utf-8"
}

sbis_header = {
    "Content-Type": "application/json-rpc;charset=utf-8",
    "X-SBISSessionID": None
}
