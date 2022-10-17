import json

from django.contrib.auth import logout, login, authenticate
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

from django.core.files.storage import default_storage

import influxdb
import os

import datetime
import time
from dateutil import parser
from datetime import datetime

INFLUX_HOST='localhost'
INFLUX_PORT=8086
INFLUX_USERNAME='admin'
INFLUX_PASSWORD='oLTj01mkPlaUjlJn'
INFLUX_DATABASE='robokop'

def open_influx():
    global client
    global INFLUX_HOST
    global INFLUX_PORT
    global INFLUX_USERNAME
    global INFLUX_PASSWORD
    global INFLUX_DATABASE
    s = os.getenv('INFLUX_HOST')
    if s:
        INFLUX_HOST = s
    s = os.getenv('INFLUX_PORT')
    if s:
        INFLUX_PORT = int(s)
    s = os.getenv('INFLUX_USERNAME')
    if s:
        INFLUX_USERNAME = s
    s = os.getenv('INFLUX_PASSWORD')
    if s:
        INFLUX_PASSWORD = s
    s = os.getenv('INFLUX_DATABASE')
    if s:
        INFLUX_DATABASE = s
    client = influxdb.InfluxDBClient(INFLUX_HOST,
                                     INFLUX_PORT,
                                     INFLUX_USERNAME,
                                     INFLUX_PASSWORD,
                                     INFLUX_DATABASE)

def createateArray(length, start, startValue):
    if startValue == 'OFF': startValue = 'ON'
    else: startValue == 'ON'

    dateArr = []
    i = 0
    while i < length:
        dateArr.append({'date': start + 600 * i, 'value' : startValue})
        i = i+1
    return dateArr

def arrayHandler(filterRes, dateArr):
    for item in filterRes:
        index = 0
        for el in dateArr:
            index += 1
            if el['date'] < time.mktime(parser.parse(item['time']).timetuple()):
                dateArr[index - 1]['value'] = item['action']
    return dateArr


def shifts(request, id, start, end):

    open_influx()
    
    res = list(client.query('SELECT * FROM shifts'))[0]

    print(res)

    #filter by id
    filterRes = [user for user in res if user['id'] == str(id)]
    #filter by date
    filterRes = [user for user in filterRes if time.mktime(parser.parse(user['time']).timetuple()) > start and time.mktime(parser.parse(user['time']).timetuple()) < end]
    filterRes = sorted(filterRes,  key=lambda x: 
                 datetime.strptime(x['time'][:-1], "%Y-%m-%dT%H:%M:%S").strftime("%b %d %Y %I:%M%p"))
    dateArr = createateArray(round((end - start)/600), start, filterRes[0]['action'])

    mutateDateArr = arrayHandler(filterRes, dateArr)
    
    if request.method == 'GET':
        return JsonResponse(mutateDateArr, safe=False)
