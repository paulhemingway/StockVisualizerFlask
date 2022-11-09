from flask import current_app as app
from flask import redirect, render_template, url_for, request, flash

from .forms import StockForm
from .charts import *



@app.route("/", methods=['GET', 'POST'])
@app.route("/stocks", methods=['GET', 'POST'])
def stocks():
    
    form = StockForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            #Get the form data to query the api
            symbol = request.form['symbol']
            chart_type = request.form['chart_type']
            time_series = request.form['time_series']
            start_date = convert_date(request.form['start_date'])
            end_date = convert_date(request.form['end_date'])

            if end_date <= start_date:
                #Generate error message as pass to the page
                err = "ERROR: End date cannot be earlier than Start date."
                chart = None
            else:
                #query the api using the form data
                err = None

                #THIS IS WHERE YOU WILL CALL THE METHODS FROM THE CHARTS.PY FILE AND IMPLEMENT YOUR CODE

                data = callAPI(symbol, time_series)
                chartLists = fillLists(data, start_date, end_date, time_series)
                chartLists = reverseLists(chartLists)

              
                #This chart variable is what is passed to the stock.html page to render the chart returned from the api
                chart = pygal.Line(x_label_rotation=65) if int(chart_type) == 2 else pygal.Bar(x_label_rotation=65)
                chart.title = 'Stock Data for ' + symbol + ": " + str(start_date)[0:10] + " to " +  str(end_date)[0:10]
                chart.x_labels = chartLists['chartDates']
                chart.add('Open', chartLists['chartOpen'])
                chart.add('High', chartLists['chartHigh'])
                chart.add('Low', chartLists['chartLow'])
                chart.add('Close', chartLists['chartClose'])
                if(len(chartLists['chartClose']) == 0):
                    print("No data was received for your inputs!")
                    return

                chart = chart.render_data_uri()
                # chart = createChart(symbol, start_date, end_date, chart_type, chartLists)

            return render_template("stock.html", form=form, template="form-template", err = err, chart = chart)
    
    return render_template("stock.html", form=form, template="form-template")
