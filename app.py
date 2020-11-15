# Import dependencies
import numpy as np

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<br/> <b>Available Routes:</b> <br/><br/>"
        f"<b>Precipitation:</b> <br/> /api/v1.0/precipitation <br/>"
        f"<b>Stations: </b><br/> /api/v1.0/stations <br/>"
        f"<b>Temperature: </b><br/> /api/v1.0/tobs <br/>"
        f"<b>Start date: </b><br/> /api/v1.0/YYYY-mm-dd <br/>"
        f"<b>Start and end date: </b><br/> /api/v1.0/YYYY-mm-dd/YYYY-mm-dd <br/>"
    )


# Route to precipitation data from past year as in Jupyter notebook section
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find lastest date from database
    # results = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    # Already know last date from previous section
    date_end = dt.datetime(2017, 8, 23)

    # Calculate one year before from end date
    # Set start date one day earlier to capture 2016-08-23
    date_start = date_end - dt.timedelta(days=366)

    # Perform a query to retrieve the date and precipitation values
    # Order results by date for easier reading
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > date_start).filter(Measurement.date <= date_end).order_by(Measurement.date).all()

    # Close session to DB
    session.close()

    # Convert the query results to a dictionary using date as the key and prcp as the value
    # Set up empty dictionary
    precipitation_one_year = []
    for date, prcp in results:
        # Retrieve each data point and save in dictionary
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp

        # Append dictionary of one data point to dictionary for all data points
        precipitation_one_year.append(precipitation_dict)

    # Return the JSON representation of the dictionary
    return jsonify(precipitation_one_year)

# Route to list of stations 
@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the list of stations
    station_list = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    
    # Close session to DB
    session.close()

     # Return the JSON representation of station_list
    return jsonify(station_list)

# Route to temperature observations for most active station in last year of data 
@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query counts how many times each station's name appears and sorts in descending order
    station_activity = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    # Already know last date from previous Jupyter notebook section
    date_end = dt.datetime(2017, 8, 23)

    # Calculate one year before from end date
    # Set start date one day earlier to capture 2016-08-23
    date_start = date_end - dt.timedelta(days=366)

    # Station with mosts activity at location [0][0] in station_activity
    # Order results by date for easier reading
    most_active_station_temps = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == station_activity[0][0]).filter(Measurement.date > date_start).filter(Measurement.date <= date_end).order_by(Measurement.date).all()

    # Close session to DB
    session.close()

    # Return the JSON representation of temperaturess with date for most active station
    return jsonify(most_active_station_temps)


    
if __name__ == '__main__':
    app.run(debug=True)
