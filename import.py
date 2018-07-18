import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():

    z = open("zips.csv")
    reader = csv.reader(z)

    for zip, city, state, latitude, longitude, population in reader:

        db.execute("INSERT INTO locations (zip, city, state, latitude, longitude, population) VALUES (:zip, :city, :state, :latitude, :longitude, :population)", {"zip": zip, "city": city, "state": state, "latitude": latitude, "longitude": longitude, "population": population})
    db.commit()

if __name__ == "__main__":
    main()