'''
This web service extends the Alphavantage api by creating a visualization module, 
converting json query results retuned from the api into charts and other graphics. 

This is where you should add your code to function query the api
'''
import requests
from datetime import datetime
import pygal
from flask import render_template


timeSeriesTypes = ["INTRADAY", "DAILY_ADJUSTED", "WEEKLY", "MONTHLY"]
timeSeriesURL = ['Time Series (60min)', 'Time Series (Daily)', 'Weekly Time Series', 'Monthly Time Series']
apiKey = "33451WDSYYNTOXAH"

#Helper function for converting date
def convert_date(str_date):
    return datetime.strptime(str_date, '%Y-%m-%d').date() if len(str_date) == 10 else datetime.strptime(str_date, '%Y-%m-%d %H:%M:%S').date()

def callAPI(symbol, timeSeries):
    timeSeriesType = timeSeriesTypes[int(timeSeries)-1]

    interval = '&interval=60min' if timeSeriesType == "INTRADAY" else ''
    apiURL = "https://www.alphavantage.co/query?function=" + "TIME_SERIES_" + timeSeriesType + "&symbol=" + symbol + interval + "&outputsize=full&apikey=" + apiKey
    r = requests.get(apiURL)
    data = r.json()
    return data

def fillLists(data, start, end, timeSeries):
    chartLists = {
        'chartOpen': [],
        'chartHigh': [],
        'chartLow': [],
        'chartClose': [],
        'chartDates': [],
    }
    try:
        for entry in data[timeSeriesURL[int(timeSeries) - 1]]:
            entryDate = convert_date(entry)
            if(entryDate >= start and entryDate <= end):
                entryObject = data[timeSeriesURL[int(timeSeries) - 1]][entry]
                chartLists['chartOpen'].append(float(entryObject["1. open"]))
                chartLists['chartHigh'].append(float(entryObject["2. high"]))
                chartLists['chartLow'].append(float(entryObject["3. low"]))
                chartLists['chartClose'].append(float(entryObject["4. close"]))
                chartLists['chartDates'].append(entry)
    except KeyError:
        print("No data for the stock was found.")
        exit()
    return chartLists

def reverseLists(chartLists):
    chartLists['chartOpen'].reverse()
    chartLists['chartHigh'].reverse()
    chartLists['chartLow'].reverse()
    chartLists['chartClose'].reverse()
    chartLists['chartDates'].reverse()
    return chartLists

def createChart(symbol, start, end, chartType, chartLists):
    print("Creating chart")
    chart = pygal.Line(x_label_rotation=65) if int(chartType) == 2 else pygal.Bar(x_label_rotation=65)
    chart.title = 'Stock Data for ' + symbol + ": " + str(start)[0:10] + " to " +  str(end)[0:10]
    chart.x_labels = chartLists['chartDates']
    chart.add('Open', chartLists['chartOpen'])
    chart.add('High',  chartLists['chartHigh'])
    chart.add('Low',      chartLists['chartLow'])
    chart.add('Close',  chartLists['chartClose'])
    if(len(chartLists['chartClose']) == 0):
        print("No data was received for your inputs!")
        return
    return chart.render_data_uri()