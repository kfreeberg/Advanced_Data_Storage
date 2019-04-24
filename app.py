
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func

import pandas as pd
import numpy as np
import datetime as dt

app = Flask(__name__)
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
connect_args={'check_same_thread': False}
echo=True
Base=automap_base()
Base.prepare(engine, reflect=True)
Measurement=Base.classes.measurement
Station = Base.classes.station

session=Session(engine)


@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (f"Available Routes: <br><br/>"
        f"  1. Precipitation:   /api/v1.0/precipitation/ <br><br/>" 
        f"  2. Station List:    /api/v1.0/stations/ <br><br/>" 
        f"  3. Temperature Observations:  /api/v1.0/tobs/ <br><br/>"
        f"  4. Stats.  Enter Start date(dd-mm-yyyy)  A sample date has been provided:  /api/v1.0/01-01/2015 <br><br/>" 
        f"  5. Stats.  Enter Start & End Date (dd-mm-yyyy/dd-mm-yyyy) Sample date have been provided:   /api/v1.0/01-01-2015/31-12-2015<br><br/>"
        )


 #  Precipitation Dictonary JSON
@app.route("/api/v1.0/precipitation/")
def precipitation():
    precipitation_query = session.query(Measurement.date, Measurement.tobs).all()
    precipitation_query_results = dict(precipitation_query)
    print()
    print("Precipitation")
    return jsonify(precipitation_query_results) 

#  Station List JSON
@app.route("/api/v1.0/stations/")
def station():
    station_query=session.query(Station.station, Station.name).\
                                group_by(Station.id).all()
    station_query_results = dict(station_query)
    print()
    print("Stations")
    return jsonify(station_query_results) 

#  Last year of precipitation data JSON
@app.route("/api/v1.0/tobs/")    
def tobs():
    last_obs_date=session.query(Measurement.date).\
        order_by(Measurement.date.desc()).first().date
    
    year_ago = dt.datetime.strptime(last_obs_date, '%Y-%m-%d') - dt.timedelta(days=365)
    yr_precip_year_query=session.query(Measurement.date, Measurement.prcp).\
                                filter(Measurement.date >= year_ago).\
                                all()

    yr_precip_query_results = dict(yr_precip_year_query)

    print("Precipitation Data")
    return jsonify(yr_precip_query_results) 

#  JSON of the minimum temperature, the average temperature, and the max temperature for a given start date
@app.route("/api/v1.0/<start_date>/")
def calc_temps(start_date=None):
    stats_start=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start_date).all()
    stats_start_list=list(stats_start)

    return jsonify(stats_start_list)


# JSON of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
@app.route("/api/v1.0/<start_date>/<end_date>/")    
def calc_temps_start_end(start_date=None, end_date=None):
    stats_start_end=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    stats_start_end_list=list(stats_start_end)                            
    return jsonify(stats_start_end_list)


if __name__ == "__main__":
    app.run(debug=True)
