
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


def get_session_and_tables():
    engine = create_engine("sqlite:///Resources/hawaii.sqlite")
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    Measurement = Base.classes.measurement
    Station = Base.classes.station
    session = Session(engine)
    return (session, Measurement, Station)

app = Flask(__name__)

@app.route("/")
def homepage():
    # thread gets created to service the request
    """List of all returnable API routes."""
    return(
        f"(Note: Dates range from 2010-01-01 to 2017-08-23). <br><br>"
        f"Available Routes: <br>"

        f"/api/v1.0/precipitation<br/>"
        f"Returns dates and temperature from the last year. <br><br>"

        f"/api/v1.0/stations<br/>"
        f"Returns a json list of stations. <br><br>"

        f"/api/v1.0/tobs<br/>"
        f"Returns list of Temperature Observations(tobs) for previous year. <br><br>"

        f"/api/v1.0/yyyy-mm-dd/<br/>"
        f"Returns an Average, Max, and Min temperatures for a given start date.<br><br>"

        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd/<br/>"
        f"Returns an Average, Max, and Min temperatures for a given date range."

        
    )


# Note - here we are getting the db variables
# within the same thread that's servicing the request
# So we don't throw some programming error on Windows machines
@app.route("/api/v1.0/precipitation")
def precipitation():
    # connection to the db, session, tables
    session, Measurement, Station = get_session_and_tables()
    """Return Dates and Temp from the last year."""
    precip_analysis = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= "2016-08-23").\
        filter(Measurement.date <= "2017-08-23").all()

    # creates JSONified list
    precipitation_list = [precip_analysis]

    return jsonify(precipitation_list)

@app.route("/api/v1.0/stations")
def stations():
    # connection to the db, session, tables
    session, Measurement, Station = get_session_and_tables()
    """Return a list of stations"""
    active_station = session.query(Measurement.station, Station.name, func.count(Measurement.tobs)).\
    filter(Measurement.station == Station.station).group_by(Measurement.station).order_by(func.count(Measurement.tobs).desc()).all()
    # results = session.query(Station.name, Station.station, Station.elevation).all()
     
    # creates JSONified list of dictionaries
    station_list = []
    for result in active_station:
        row = {}
        row['name'] = result[0]
        row['station'] = result[1]
        row['elevation'] = result[2]
        station_list.append(row)
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def temp_obs():
    # connection to the db, session, tables
    session, Measurement, Station = get_session_and_tables()
    """Return a list of tobs for the previous year"""
    results = session.query(Station.name, Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= "2016-08-24", Measurement.date <= "2017-08-23").\
        all()
#
    # creates JSONified list of dictionaries
    tobs_list = []
    for result in results:
        row = {}
        row["Station"] = result[0]
        row["Date"] = result[1]
        row["Temperature"] = int(result[2])
        tobs_list.append(row)

    return jsonify(tobs_list)


@app.route('/api/v1.0/<date>/')
def given_date(date):
    session, Measurement, Station = get_session_and_tables()
    """Return the average temp, max temp, and min temp for the date"""
    results = session.query(func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date >= date).all()

    # creates JSONified list of dictionaries
    data_list = []
    for result in results:
        row = {}
        row['Start Date'] = date
        row['End Date'] = '2017-08-23'
        row['Average Temperature'] = float(result[0])
        row['Highest Temperature'] = float(result[1])
        row['Lowest Temperature'] = float(result[2])
        data_list.append(row)

    return jsonify(data_list)

@app.route('/api/v1.0/<start_date>/<end_date>/')
def query_dates(start_date, end_date):
    session, Measurement, Station = get_session_and_tables()
    """Return the avg, max, min, temp over a specific time period"""
    results = session.query(func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

    # creates JSONified list of dictionaries
    data_list = []
    for result in results:
        row = {}
        row["Start Date"] = start_date
        row["End Date"] = end_date
        row["Average Temperature"] = float(result[0])
        row["Highest Temperature"] = float(result[1])
        row["Lowest Temperature"] = float(result[2])
        data_list.append(row)
    return jsonify(data_list)


if __name__ == '__main__':
    app.run(debug=True, port=5000)