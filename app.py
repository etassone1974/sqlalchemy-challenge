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
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    # Convert date from query above to required datetime object
    date_time_obj = dt.datetime.strptime(last_date[0],"%Y-%m-%d")

    # Extract date from datetime object
    date_end = date_time_obj.date()

    # Calculate one year before from end date
    date_start = date_end - dt.timedelta(days=365)

    # Perform a query to retrieve the date and precipitation values for date range
    # Order results by date for easier reading
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= date_start).filter(Measurement.date <= date_end).order_by(Measurement.date).all()

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

    # Find lastest date from database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    # Convert date from above query to required datetime object
    date_time_obj = dt.datetime.strptime(last_date[0],"%Y-%m-%d")

    # Extract date from datetime object
    date_end = date_time_obj.date()

    # Calculate one year before from end date
    date_start = date_end - dt.timedelta(days=365)

    # Station with mosts activity at location [0][0] in station_activity
    # Retrieve for one year date range
    # Order results by date for easier reading
    most_active_station_temps = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == station_activity[0][0]).filter(Measurement.date >= date_start).filter(Measurement.date <= date_end).order_by(Measurement.date).all()

    # Close session to DB
    session.close()

    # Return the JSON representation of temperatures with date for most active station
    return jsonify(most_active_station_temps)

# Route to min, average and max temperature for a given start date
# Start date given in YYYY-mm-dd format
@app.route("/api/v1.0/<start>")
def min_average_max_tobs(start):

    # Convert date given in API call to required datetime object
    date_time_obj = dt.datetime.strptime(start,"%Y-%m-%d")

    # Extract date from datetime object
    start_date = date_time_obj.date()

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the min, average and max temperature values on any date after the start date inclusive
    temp_obs = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
   
    # Close session to DB
    session.close()

    # Return the JSON representation of min, average, and max temperature
    if temp_obs[0][0]:
        return jsonify(temp_obs)

    # Return 404 error if date not in dataset
    return jsonify({"error": "Date not found"}), 404

# Route to min, average and max temperature for a given start and end date
# Start date given in YYYY-mm-dd format
@app.route("/api/v1.0/<start>/<end>")
def min_average_max_tobs_range(start, end):

    # Convert dates given in API call to required datetime object
    date_time_obj1 = dt.datetime.strptime(start,"%Y-%m-%d")
    date_time_obj2 = dt.datetime.strptime(end,"%Y-%m-%d")

    # Extract start date from datetime object
    start_date = date_time_obj1.date()

    # Extract end date from datetime object
    end_date = date_time_obj2.date()

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the min, average and max temperature values on any date after the start date inclusive
    temp_obs = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
   
    # Close session to DB
    session.close()

    # Return the JSON representation of min, average, and max temperature
    if temp_obs[0][0]:
        return jsonify(temp_obs)

    # Return 404 error if date not in dataset
    return jsonify({"error": "Date not found"}), 404



if __name__ == '__main__':
    app.run(debug=True)
