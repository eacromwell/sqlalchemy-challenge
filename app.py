# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################


#################################################
# Landing Page
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation - Precipitation data for the last year<br/>"
        f"/api/v1.0/stations - List of weather stations<br/>"
        f"/api/v1.0/tobs - Temperature observations of the most-active station for the previous year of data.<br/>"
        f"/api/v1.0/start_date - Min, Avg, and Max temperature for a given start date (format: YYYY-MM-DD)<br/>"
        f"/api/v1.0/start_date/end_date - Min, Avg, and Max temperature for a given start date and end date (format: YYYY-MM-DD)"
    )


#################################################
# Precipitation
#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.date.fromisoformat(most_recent_date) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    precipitation_data = {date: prcp for date, prcp in results}
    session.close()  # Added session close
    return jsonify(precipitation_data)


#################################################
# Stations
#################################################

@app.route("/api/v1.0/stations")
def stations():
    # Query the list of stations
    results = session.query(Station.station).all()
    # Convert the results to a list
    station_list = list(np.ravel(results))
    session.close()  # Added session close
    return jsonify(station_list)

#################################################
# Temperature Observations
#################################################

@app.route("/api/v1.0/tobs")
def tobs():
    # Find the most recent date in the data set
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    # Calculate the date one year from the last date in data set
    one_year_ago = dt.date.fromisoformat(most_recent_date) - dt.timedelta(days=365)
    # Query the most active station based on the highest count of temperature observations
    most_active_station = session.query(Measurement.station)\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.tobs).desc())\
        .first()
    # Query temperature observations for the most active station in the last year
    results = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.date >= one_year_ago)\
        .filter(Measurement.station == most_active_station[0])\
        .all()
    # Create a list of dictionaries with date and temperature observations
    temperature_data = [{'date': date, 'tobs': tobs} for date, tobs in results]
    session.close()  # Close the session
    return jsonify(temperature_data)

    
#################################################
# Start Date
#################################################

@app.route("/api/v1.0/<start>")
def temperature_by_start_date(start):
    # Query the minimum, average, and maximum temperatures for a given start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    # Create a dictionary with the temperature data
    temperature_data = {
        "Min Temperature": results[0][0],
        "Avg Temperature": results[0][1],
        "Max Temperature": results[0][2]
    }
    session.close()  # Added session close
    return jsonify(temperature_data)

    
#################################################
# Start and End Date
#################################################

@app.route("/api/v1.0/<start>/<end>")
def temperature_by_start_end_date(start, end):
    # Query the minimum, average, and maximum temperatures for a given start and end date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    # Create a dictionary with the temperature data
    temperature_data = {
        "Min Temperature": results[0][0],
        "Avg Temperature": results[0][1],
        "Max Temperature": results[0][2]
    }
    session.close()  # Added session close
    return jsonify(temperature_data)
if __name__ == '__main__':
    app.run(debug=True)

