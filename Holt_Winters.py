# This is the 2nd draft of Bandwidth Prediction Algorithm.
# The below program is an implementation of Holt Winter's Forecasting technique. The algorithm is a triple exponential smoothing to predict number of points
# series is a variable which we used to store bandwidth values and contain 60 values which define the bandwidth of each minute in an hour
# Bandwidth_Prediction is the variable where predicted points are bring stored. We will be predicting 60 points in the future i.e., Bandwidth range for the next hour
# slen is the season length which is a requirement of a time series. In this implementation it will be chosen as 15 minutes i.e. 15 
# Values of aplha,beta and gamma are predicted using formula's given in report. 
# Value of alpha is 0.09, beta is 0.004 and gamma is 0.09

import MySQLdb as db
from datetime import datetime, timedelta

def initial_trend(series, slen):
    sum = 0.0
    for i in range(slen):
        sum += float(series[i+slen] - series[i]) / slen
    return sum / slen
    
def initial_seasonal_components(series, slen):
    seasonals = {}
    season_averages = []
    n_seasons = int(len(series)/slen)
    # compute season averages
    for j in range(n_seasons):
        season_averages.append(sum(series[slen*j:slen*j+slen])/float(slen))
    # compute initial values
    for i in range(slen):
        sum_of_vals_over_avg = 0.0
        for j in range(n_seasons):
            sum_of_vals_over_avg += series[slen*j+i]-season_averages[j]
        seasonals[i] = sum_of_vals_over_avg/n_seasons
    return seasonals

def triple_exponential_smoothing(series, slen, alpha, beta, gamma, n_preds):
    result = []
    seasonals = initial_seasonal_components(series, slen)
    for i in range(len(series)+n_preds):
        if i == 0: # initial values
            smooth = series[0]
            trend = initial_trend(series, slen)
            result.append(series[0])
            continue
        if i >= len(series): # we are forecasting
            m = i - len(series) + 1
            result.append((smooth + m*trend) + seasonals[i%slen])
        else:
            val = series[i]
            last_smooth, smooth = smooth, alpha*(val-seasonals[i%slen]) + (1-alpha)*(smooth+trend)
            trend = beta * (smooth-last_smooth) + (1-beta)*trend
            seasonals[i%slen] = gamma*(val-smooth) + (1-gamma)*seasonals[i%slen]
            result.append(smooth+trend+seasonals[i%slen])
    return result
    
predictor_db = MySQLdb.connect(host="192.168.1.7",user="ubuntu",passwd="123456",db="bandwidth",port=3306)
cur =predictor_db.cursor()
cur.execute("show tables;")
#cur.execute("select found_rows();")
try:
	answer=cur.fetchall()
except:
	print "unable to fetch"
tables = [x[0] for x in answer]#Tables contain all the tables that are present in database. We have to predict bandwidth for every table
number_tables = len(tables)
bandwidth_matrix = [[]]
for i in range(number_tables):
	query = "select bandwidthusage from %s order by bandwidthusage desc limit 60;" % tables[i]
	cur.execute(query)
    try:
        answers=cur.fetchall()
    except:
        print "unable to fetch"
	listi = [x[0] for x in answers]# Listi contains the bandwidth Value of our hour for the tenant
    bandwidth_matrix.append(listi)
predictor_db.close()

predicted_db = MySQLdb.connect(host="192.168.1.7",user="ubuntu",passwd="123456",port=3306)
cursor_db = predicted_db.cursor()
cursor_db.execute("SET sql_notes = 0;")
cursor_db.execute("create database if not exists predicted_bandwidth;")
cursor_db.execute("SET sql_notes =1;")
cursor_db.close()

predicted_db = MySQLdb.connect(host="192.168.1.7",user="ubuntu",passwd="123456",db="predicted_bandwidth",port=3306)
cursor_db = predicted_db.cursor()
for i in range(number_tables):
    bandwidth_matrix[i+1].reverse()
    series = bandwodth_matrix[i+1]
    Bandwidth_Prediction = triple_exponential_smoothing(series,15, 0.09, 0.004, 0.09, 60)
    cursor_db.execute("SET sql_notes = 0;")
    cursor_db.execute("create table if not exists {} (futuredatetime VARCHAR(50),predicted_bandwidthusage INTEGER);".format("tenant"+str(i)))
    cursor_db.execute("SET sql_notes = 1;")
    for j in range(60):
        curr_time = datetime.now()
        future_time = curr_time + timedelta(seconds = j+1)
        cursor_db.execute("insert into {} (futuredatetime,predicted_bandwidthusage) values ('{}',{});".format("tenant"+str(i),future_time.strftime('%Y/%m/%d %H:%M:%S'),Bandwidth_Prediction[j]))
        predicted_db.commit()
predicted_db.close()
