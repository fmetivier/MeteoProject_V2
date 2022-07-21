import matplotlib.pyplot as plt
import matplotlib.dates as md
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from sqlalchemy import create_engine


def weatherDB_connect():
    """Connect to weather database"""
    f = open("mylogin_me.txt", "r")
    mylogin = f.readline().strip("\n")
    mypass = f.readline().strip("\n")
    f.close()
    print(mylogin, mypass)
    engine = create_engine("mysql://%s:%s@localhost/weatherDB" % (mylogin, mypass))
    conn = engine.connect()

    return conn


def load_records(station_code="PA01", fname="METEOLOG.txt"):
    """Reads a meteolog file and loads TH and P
    data into the corresponding tables

    BEWARE not to import the data twice or more...

    params: station_code: str code of the meteorologic station
    params: fname: str name of the file to be parsed
    """
    conn = weatherDB_connect()
    f = open("../data/" + fname, "r")
    lines = f.readlines()
    for line in lines:
        data = line.strip("\n").split(",")
        if "w" in data[0]:
            sql = "insert into TH values (%s,%s,%s,%s,%s,NULL)"
            conn.execute(sql, [data[1], data[2], data[3], data[4], station_code])
        elif "p" in data[0]:
            sql = "insert into P values (NULL,%s,%s,%s,%s)"
            conn.execute(sql, [data[1], data[2], data[3], station_code])
    conn.close()


def temp_record(station_code="PA01"):
    """
    temperature record of the station
    the record is stored in a mysql database
    """
    conn = weatherDB_connect()

    sql = "select str_to_date(concat(mdate,' ',mtime),'%Y-%m-%d %T') as dt, avg(T) as Tm from TH  "
    sql += "where stcode = '%s' group by mdate, hour(mtime)" % (station_code)

    df = pd.read_sql(sql, conn)
    print(df.head())

    fig, ax = plt.subplots(1)
    ax.plot(df["dt"], df["Tm"].tolist(), "-", color="C1")
    myFmt = md.DateFormatter("%d:%h")
    ax.xaxis.set_major_formatter(myFmt)
    ax.set_ylabel("Temperature ($^o$C)")
    ax.set_xlabel("Date")

    conn.close()


def temperature_hour_avg(station_code="PA01"):
    """
    hourly temperature plot from the database record
    """
    conn = weatherDB_connect()

    sql = (
        "select hour(mtime) as hour, avg(T) as Tm from TH  where stcode = '%s' group by hour(mtime)"
        % (station_code)
    )

    df = pd.read_sql(sql, conn)

    plt.figure()

    plt.plot(df["hour"], df["Tm"].tolist(), color="C1")

    conn.close()


def precip_1(station_code="PA01"):
    """
    Calculation fo the rainfall intensity
    """
    conn = weatherDB_connect()

    sql = "select str_to_date(concat(mdate,' ',mtime),'%Y-%m-%d %T') as t,N  from P "
    sql += "where stcode = '%s'" % (station_code)

    df = pd.read_sql(sql, conn)
    temps = df["t"].tolist()
    precip = df["N"].tolist()

    tts = [0]  # arbitrary first timestamp
    for t in temps:
        tts.append(t.timestamp())

    I = np.array(precip) / np.diff(np.array(tts))

    c = 0
    tbar = [temps[0]]
    pbar = [I[0]]
    while c < len(I) - 1:
        tbar.append(temps[c])
        tbar.append(temps[c + 1])
        pbar.append(I[c + 1])
        pbar.append(I[c + 1])
        c += 1

    fig, ax = plt.subplots(1)
    ax.plot(tbar, pbar, "-")
    myFmt = md.DateFormatter("%d:%h")
    ax.xaxis.set_major_formatter(myFmt)
    ax.set_ylabel("Rainfall rate (mm/s)")
    ax.set_xlabel("Date")


if __name__ == "__main__":
    # load_records(fname="METEOLOG_2.TXT")
    temp_record()
    temperature_hour_avg()
    precip_1()
    plt.show()
