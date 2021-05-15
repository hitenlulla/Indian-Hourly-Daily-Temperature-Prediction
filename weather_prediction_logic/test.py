import pickle
from typing import final
import bs4
import requests
import time
from datetime import datetime, date, timedelta

def fillStartNullValues(dic):
    val_arr = list(dic.values())
    ptr = 0
    while val_arr[ptr] == 0:
        ptr += 1

    preptr = ptr - 1
    dec_factor = -1
    while preptr > 0 and val_arr[preptr] == 0:
        val_arr[preptr] = val_arr[ptr] - dec_factor
        val_arr[preptr - 1] = val_arr[ptr] - dec_factor
        val_arr[preptr - 2] = val_arr[ptr] - dec_factor
        val_arr[preptr - 3] = val_arr[ptr] - dec_factor
        preptr -= 4
        dec_factor -= 1

    for i, a in enumerate(val_arr):
        key = str(i) + '.00'
        dic[key] = round(a)

    return dic

def fillEndNullValues(dic):
    val_arr = list(dic.values())
    N = len(val_arr)

    endptr = N - 1
    pre_endptr = endptr - 1
    while val_arr[pre_endptr] == 0: 
        pre_endptr -= 1

    xptr = pre_endptr + 1
    dec_factor = -1
    while xptr + 1 <= endptr:
        val_arr[xptr] = val_arr[pre_endptr] + dec_factor
        val_arr[xptr + 1] = val_arr[pre_endptr] + dec_factor
        dec_factor -= 1
        xptr += 2

    for i, a in enumerate(val_arr):
        key = str(i) + '.00'
        dic[key] = round(a)

    return dic

def checkNullSegments(dic):
    val_arr = list(dic.values())
    N = len(val_arr)
    start_ptr = 0

    while val_arr[start_ptr] != 0 and start_ptr < N - 1:
        start_ptr += 1

    if start_ptr == N:
        return False, -100, -100

    end_ptr = start_ptr

    while val_arr[end_ptr] == 0 and end_ptr < N - 1:
        end_ptr += 1

    if start_ptr == end_ptr:
        return False, -100, -100
    return True, start_ptr, end_ptr

def fillMidNullValues(dic, start_ptr, end_ptr):
    val_arr = list(dic.values())
    N = len(val_arr)
    dec_fac = 0.25
    while start_ptr < end_ptr:
        val_arr[start_ptr] = val_arr[end_ptr] - dec_fac
        start_ptr += 1
        dec_fac += 0.25
    for i, a in enumerate(val_arr):
        key = str(i) + '.00'
        dic[key] = round(a)

    return dic

def fillAllNullValues(dic):
    dic = fillStartNullValues(dic)
    dic = fillEndNullValues(dic)

    isNull, start_ptr, end_ptr = checkNullSegments(dic)

    while isNull:
        isNull, start_ptr, end_ptr = checkNullSegments(dic)
        dic = fillMidNullValues(dic, start_ptr, end_ptr)

    return dic

def getPrevData(city, prev_date):
    url = "https://www.timeanddate.com/weather/india/{}/historic?hd={}".format(city, prev_date)
    print(url)
    res = requests.get(url)
    text = bs4.BeautifulSoup(res.text, "html.parser")

    rows = text.select('#wt-his > tbody tr')
    final_data = {'0.00': 0,
            '1.00': 0, 
            '2.00': 0, 
            '3.00': 0, 
            '4.00': 0, 
            '5.00': 0, 
            '6.00': 0,
            '7.00':0,
            '8.00': 0, 
            '9.00': 0, 
            '10.00': 0, 
            '11.00': 0, 
            '12.00': 0, 
            '13.00': 0, 
            '14.00': 0, 
            '15.00': 0, 
            '16.00': 0, 
            '17.00': 0, 
            '18.00': 0, 
            '19.00': 0, 
            '20.00': 0, 
            '21.00': 0, 
            '22.00': 0, 
            '23.00': 0}

    dict = {}
    for i, row in enumerate(rows):
        # print(row)
        time = row.select('th')[0].text[:5]
        temp = int(row.select('td:nth-child(3)')[0].text[:2])
        if time[3:] == '30':
            time = time[:3] + '00'
        if time[0] == '0':
            time = time[1:]
        dict[time] = temp

    # For hours that were availible on the site
        for key, val in dict.items():
            final_data[key] = val

    # # For hours that don't have temperature
    # try:
    #     for key, val in final_data.items():
    #         if val == 0:
    #             prev_val = str(int(float(key)) - 1) + ".00"
    #             final_data[key] = final_data[prev_val]
    # except KeyError:
    #     print("hi")

    # final_data = fillAllNullValues(final_data)

    return (final_data)

print(getPrevData('amritsar', 20210512))
print(getPrevData('chennai', 20210512))
print(getPrevData('thane', 20210512))
print(getPrevData('bengaluru', 20210512))
print(getPrevData('mumbai', 20210512))
print(getPrevData('ahmadabad', 20210512))
print(getPrevData('jaipur', 20210512))
print(getPrevData('hyderabad', 20210512))
print(getPrevData('dharamshala', 20210512))
print(getPrevData('lucknow', 20210512))
print(getPrevData('agra', 20210512))