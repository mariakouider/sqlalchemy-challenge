from flask import Flask, jsonify
import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

# Create a Flask app
app = Flask(__name__)

# Connect to the database
database_path = "/Users/mariakouiderelouahed/Desktop/hawaii.sqlite"
engine = create_engine(f"sqlite:///{database_path}")

# Reflect the database
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

# Define the routes
@app.route("/")
def home():
    return (
        f"Welcome to the Climate App API!<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = dt.datetime.strptime(last_date[0], "%Y-%m-%d") - dt.timedelta(days=365)
    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year).all()
    prcp_dict = {date: prcp for date, prcp in precipitation_data}
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    station_results = session.query(Station.station).all()
    stations_list = list(np.ravel(station_results))
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Get the most active station ID
    most_active_station_id = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    most_active_station_id = most_active_station_id[0]

    # Calculate the date one year from the last date in the dataset
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=365)

    # Query temperature data for the most active station for the last year
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station_id, Measurement.date >= one_year_ago).all()

    # Create a list of dictionaries containing date and temperature
    temperature_list = [{"date": date, "tobs": tobs} for date, tobs in temperature_data]
    return jsonify(temperature_list)

# Define routes for <start> and <start>/<end>

if __name__ == "__main__":
    app.run(debug=True)

