import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime

#Database Setup
engine=create_engine("sqlite:///hawaii.sqlite")

#reflect database into a new model
Base=automap_base()
#reflect the tables
Base.prepare(engine,reflect=True)

#save references to the table
Station=Base.classes.stations
Measurement=Base.classes.measurments

#create session from python to the DB
session=Session(engine)

#Create an app
app=Flask(__name__)

#/api/v1.0/precipitation
#Query for dates and temperature observations from last year
#convert query results to a Dictionary using date as the key and tobs as value
#Return json representation of your dictionary
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Avalable Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def temperature():
    #find latest date in database and date year ago
    result=session.query(func.max(Measurement.date))
    date_tuple=result[0]
    max_date=date_tuple[0]
    year_ago_date = max_date - datetime.timedelta(365)
    #Query dates and temperature observations from last year
    results=session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago_date).all()
        
    #convert query results to a dictionary using date as the key and tabs as value
        
    date_temp=[]
    for daily_temp in results:
        Date=str(daily_temp[0])
        Temp=daily_temp[1]
        temp_dict={}
        temp_dict.update({Date:Temp})
        date_temp.append(temp_dict)
    #return json representation of your decitionary
    return jsonify(date_temp)

@app.route("/api/v1.0/stations")
def stations():
    results=session.query(Station.station)
    Stations=[]
    for result in results:
        Stations.append(result)
    return jsonify(Stations)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    
    if end=None:
    #calculate temperature min, max and average;
    #query for temperatures from previous years for given date range
    temp_data=session.query(Measurement.date,Measurement.tobs).\
    filter(Measurement.date >=start).all()
    
    #put queried data into a dataframe
    temp_df=pd.DataFrame(temp_data, columns=["Date","tobs"])
    
    #find average temperature
    average=temp_df["tobs"].mean()
    
    #find min temperature
    min_temp=temp_df["tobs"].min()
    
    #find max temperature
    max_temp=temp_df["tobs"].max()

    temp_list=[average,min_temp,max_temp]

    return jsonify(temp_list)

if __name__ == '__main__':
    app.run(debug=True)
