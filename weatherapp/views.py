from django.shortcuts import render
import pickle
import bs4
import requests
import time
import random
from datetime import datetime, date, timedelta
from django.http import HttpResponseNotFound

# Fill Null Data
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

def getCurrentCity():
    """     Uncomment This
    res = requests.get("https://ipinfo.io/")
    data = res.json()
    city = data['city']
    """
    city = "Ulhasnagar"
    return city

def getPrevDataOfCity(prev_date, city = None):
    if city is None:
        city = getCurrentCity()
    url = "https://www.timeanddate.com/weather/india/{}/historic?hd={}".format(city, prev_date)
    # print(url)
    res = requests.get(url)
    text = bs4.BeautifulSoup(res.text, "html.parser")
    
    location_html = text.select('body > div.main-content-div > header > div.bn-header__wrap.fixed > div > section.headline-banner__wrap > div > h1')
    location = str(location_html[0])[51:-34].split(", ")
    state = location[1]

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
    # Web Scraping
    for i, row in enumerate(rows):
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

    #For hours that aren't availible on the site
    final_data = fillAllNullValues(final_data)

    return city, state, final_data

def getPrevTime():
    now = datetime.now()

    curr_time = now.strftime("%H:%M:%S")
    if curr_time[0] == '0':
        prev_time = curr_time[1:2] + ".00"
    else:
        prev_time = curr_time[:2] + ".00"
    return str(prev_time)

def getPrevDate():
    yesterdat_date = date.today() - timedelta(1)
    temp = str(yesterdat_date)
    yesterdat_date = temp[:4] + temp[5:7] + temp[8:]
    return str(yesterdat_date)

def getDays():
    days = []
    day = date.today().strftime("%A")
    days.append(day)
    for i in range(1,7):
        dt = date.today() + timedelta(i)
        day = dt.strftime("%A")
        days.append(day)

    return days

def convertTimeFormat(time):
    if int(float(time)) <= 11:
        if int(float(time)) == 0:
            time = "12:00 AM"
        elif time[1] == '.':
            time = "0" + str(time[0]) + ":" + str(time[2:]) + " AM"
        elif time[2] == '.':
            time = str(time[:2]) + ":" + str(time[3:]) + " AM"
    else:
        if int(float(time)) == 12:
            time= "12:00 PM"
        else:
            time = int(float(time)) - 12
            if time <= 9:
                time = "0" + str(time) + ":00 PM"
            else:
                time = str(time) + ":00 PM"
    
    return time


def getIconName(time):
    time = int(float(time))
    if time >= 0 and time <= 8:
        return "fas fa-cloud"
    elif time >= 9 and time <= 17:
        return "fas fa-sun"
    elif time >= 18 and time <= 23:
        return "fas fa-wind"

def getTimePrior(time):
    if time == '0.00':
        time_prior = '23'
    elif time[1] == '.':
        time_prior = int(time[0:1]) - 1
    elif time[2] == '.':
        time_prior = int(time[0:2]) - 1
    time_prior = str(time_prior) + '.00'
    return time_prior

def getTimeNext(time):
    if time == '23.00':
        next_time = '0'
    elif time[1] == '.':
        next_time = int(time[0:1]) + 1
    elif time[2] == '.':
        next_time = int(time[0:2]) + 1
    next_time = str(next_time) + '.00'
    return next_time

def getPrevHourTempofCurrentCity(city = None):
    print(city)
    if city is None:
        city = getCurrentCity()
    url = 'https://www.timeanddate.com/weather/india/{}/historic'.format(city)
    res = requests.get(url)
    text = bs4.BeautifulSoup(res.text, "html.parser")
    curr_temp_prior = text.select_one('#wt-his > tbody > tr:nth-child(1) > td:nth-child(3)').text[:3]
    return curr_temp_prior

def importModel():
    f = open("weather_prediction_model/weather_model.ser", "rb")
    model = pickle.load(f)
    f.close()
    return model


def getRandomPositiveVariance():
    n = random.randint(-1,3)
    return (n)

def getRandomNegativeVariance():
    n = random.randint(-1,2)
    return (n)

def predictTemparatures(city = None):
    prev_time = getPrevTime()                                                   # yesterday's time
    prev_date = getPrevDate()                                                   # yesterday's date  
    
    if city is None:
        city, state, prevData = getPrevDataOfCity(prev_date)                    #get yesterday's weather dataSet of current city
    else:
        city, state, prevData = getPrevDataOfCity(prev_date, city)              #get yesterday's weather dataSet of specified city

    if city is None:
        curr_temp_prior = int(getPrevHourTempofCurrentCity())                   #get temp at (today's time - 1hr) of current city
    else:
        curr_temp_prior = int(getPrevHourTempofCurrentCity(city))               #get temp at (today's time - 1hr) of specified city

    weatherModel = importModel()                                                #import Weather Pred Model
    
    prev_temp = prevData[prev_time]                                             #get temp at (yesterday's time)

    prev_time_prior = getTimePrior(prev_time)                                   #get (yesterday's time - 1hr) 

    prev_temp_prior = int(prevData[prev_time_prior])                            #get temp at (yesterday's time - 1hr) 

    '''
    1 - load the following into the Weather prediction model 
    temp at (yesterday's time), difference of {temp at (today's time - 1hr) and temp at (yesterday's time - 1hr)}

    2 - Make a predictedHourlyData dictionary and store every predicted time and its temp - from curr_time to '00.00'
    
    3- Loop 24 times to get 24 hrs of weather prediction
    '''
    days = getDays()
    today = days[0]
    tomorrow = days[1]
    predictedHourlyData = {}
    latestData = {}
    daily_data_first_set = {}
    current_day_dic = {}
    output_data = {}
    next_day = {}

    predictedDailyData = {
        days[0] : {},
        days[1] : {},
        days[2] : {},
        days[3] : {},
        days[4] : {},
        days[5] : {},
        days[6] : {},
    }

    # Initialisation
    curr_time = prev_time
    curr_temp = weatherModel.predict([[prev_temp, curr_temp_prior - prev_temp_prior]])[0]
    
    # Bug:1 - The day doesnot Changes when website is loaded at or after 11:00 PM
    if int(float(curr_time)) <= 23:
            latestData[curr_time] = {'time': convertTimeFormat(curr_time), 'day': today, 'temperature': int(curr_temp)}
    else:
        latestData[curr_time] = {'time': convertTimeFormat(curr_time), 'day': tomorrow, 'temperature': int(curr_temp)}
    
    next_time = getTimeNext(curr_time)
    prev_temp = prevData[next_time]
    next_time_prior = getTimePrior(next_time)
    next_temp_prior = prevData[next_time_prior]
    curr_temp_prior = latestData[next_time_prior]['temperature']
    next_temp = weatherModel.predict([[prev_temp, float(curr_temp_prior) - next_temp_prior]])[0]
    if int(float(next_time)) <= 23:
        current_day_dic[next_time] = int(next_temp)
        predictedHourlyData[next_time] = {'time': convertTimeFormat(next_time),'day': today, 'temperature': int(next_temp)}
    else:
        predictedHourlyData[next_time] = {'time': convertTimeFormat(next_time), 'day': tomorrow, 'temperature': int(next_temp)}
    
    # Iterations
    temp_var_factor = 1
    # day_ctr = 0
    # while day_ctr <= 6:
    hour_ctr = 0
    output_number_of_hours = 6
    day_change = False
    while hour_ctr != 46:
        if next_time == '23.00':
            day_change = True
        next_time = getTimeNext(next_time)
        prev_temp = prevData[next_time]
        next_time_prior = getTimePrior(next_time)
        next_temp_prior = prevData[next_time_prior]
        curr_temp_prior = predictedHourlyData[next_time_prior]['temperature']
        next_temp = weatherModel.predict([[prev_temp, float(curr_temp_prior) - next_temp_prior]])[0]
        if not day_change:
            # if hour_ctr <= output_number_of_hours:
            predictedHourlyData[next_time] = {'time': convertTimeFormat(next_time),'day': today, 'temperature': int(next_temp)}
            if hour_ctr <= output_number_of_hours:
                output_data[next_time] = {'time': convertTimeFormat(next_time),'day': today, 'temperature': int(next_temp)}
            current_day_dic[next_time] = int(next_temp)
        else:
            # if hour_ctr <= output_number_of_hours:
            predictedHourlyData[next_time] = {'time': convertTimeFormat(next_time), 'day': tomorrow, 'temperature': int(next_temp)}
            if hour_ctr <= output_number_of_hours:
                output_data[next_time] = {'time': convertTimeFormat(next_time), 'day': tomorrow, 'temperature': int(next_temp)}
            next_day[next_time] = int(next_temp)
        hour_ctr += 1

    day_ctr = 0
    while day_ctr <= 6:
        predictedDailyData[days[day_ctr]] = {'min_temperature': min(current_day_dic.values()) + getRandomNegativeVariance(),'max_temperature': max(current_day_dic.values()) + getRandomPositiveVariance()}
        day_ctr += 1

    return latestData, output_data, predictedDailyData, city, state

def home(request):
    try:
        if request.GET.get('city'):
            city = request.GET.get('city')
            latestData, predictedHourlyData, predictedDailyData, city, state = predictTemparatures(city)
            return render(request, 'home.html', {'latest_data': latestData, 'hourly_prediction': predictedHourlyData,'daily_prediction': predictedDailyData , 'city':city, 'state': state, 'city_msg' : city})
        else:
            latestData, predictedHourlyData, predictedDailyData, city, state = predictTemparatures()
            return render(request, 'home.html', {'latest_data': latestData, 'hourly_prediction': predictedHourlyData,'daily_prediction': predictedDailyData , 'city':city, 'state': state, 'city_msg' : "Enter City..."})
    except IndexError:
        return HttpResponseNotFound("<h1>Error 404: Check the City Name</h1>")
        
def stats(request):
    return render(request, 'stats.html',{'city_msg' : "Enter City..."})