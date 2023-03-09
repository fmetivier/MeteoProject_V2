import matplotlib.pyplot as plt
import matplotlib.dates as md
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from sqlalchemy import create_engine
from getpass import getpass


def weatherDB_connect(fname=None):
    """Connect to weather database"""
    if fname:
        f = open(fname, "r")
        mylogin = f.readline().strip("\n")
        mypass = f.readline().strip("\n")
        f.close()
    else:
        mylogin = input("login:")
        mypass = getpass("password:")

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
        # if "w" in data[0]:
        #     sql = "insert into TH values (%s,%s,%s,%s,%s,NULL)"
        #     conn.execute(sql, [data[1], data[2], data[3], data[4], station_code])
        if "p" in data[0]:
            try:
                sql = "insert into P values (NULL,%s,%s,%s,%s)"
                conn.execute(sql, [data[1], data[2], data[3], station_code])
            except:
                print("record registration failed for line %s" % (line))
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

    sql = """select concat(mdate,' ',mtime) as t, N from P  where stcode = '%s'""" % (
        station_code
    )

    res = conn.execute(sql).fetchall()
    temps = []
    precip = []

    for r in res:
        temps.append(datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S"))
        precip.append(r[1])

    # df = pd.read_sql(sql, conn)
    # temps = df["t"].tolist()
    # precip = df["N"].tolist()

    tts = [0]  # arbitrary first timestamp
    for t in temps:
        tts.append(t.timestamp())

    I = np.ones(len(precip)) * 0.25 / np.diff(np.array(tts)) * 3600

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
    ax.set_ylabel("Rainfall rate (mm/h)")
    ax.set_xlabel("Date")


def hourly_precip(mdate):
    """
    extraction of hourly precipitation and intensity
    """
    conn = weatherDB_connect()

    sql = "select str_to_date(concat(mdate,' ',mtime),'%Y-%m-%d %T') as t, N from P"
    sql += " where stcode = 'PA01' and mdate='2022-08-16' group by hour(mtime)"


def bin_p(t, pval, tstart, tstep):
    "bins the precipitation data pval from tstart with tstep (in seconds) returns the binned values"

    pbin = []
    i = 0
    tbin = [tstart]

    while i < len(pval) - 1:
        tval = tbin[-1] + timedelta(seconds=tstep)
        p = 0
        while t[i] < tval and i < len(pval) - 1:
            p += 0.25
            i += 1
        pbin.append(p)
        tbin.append(tval)

    tbin = tbin[:-1]

    return np.array(tbin), np.array(pbin)


def precip_compare_16():
    """
    Calculation fo the rainfall intensity
    """
    conn = weatherDB_connect()

    sql = "select str_to_date(concat(mdate,' ',hour(date_sub(mtime, interval 1 hour))),'%Y-%m-%d %T') as t, count(*) as N from P"
    sql += " where stcode = 'PA01' and mdate='2022-08-16' group by hour(mtime)"

    df = pd.read_sql(sql, conn)

    tempsh = df["t"].tolist()
    preciph = np.array(df["N"].tolist()) * 0.25

    sql = "select str_to_date(concat(mdate,' ',date_sub(mtime, interval 1 hour)),'%Y-%m-%d %T') as t, N from P"
    sql += " where stcode = 'PA01' and mdate='2022-08-16'"

    df = pd.read_sql(sql, conn)
    temps = df["t"].tolist()
    precip = df["N"].tolist()

    tts = [0]  # arbitrary first timestamp
    for t in temps:
        tts.append(t.timestamp())

    I = np.ones(len(precip)) * 0.25 / np.diff(np.array(tts)) * 3600

    c = 0
    tbar = [temps[0]]
    pbar = [I[0]]
    while c < len(I) - 1:
        tbar.append(temps[c])
        tbar.append(temps[c + 1])
        pbar.append(I[c + 1])
        pbar.append(I[c + 1])
        c += 1

    print(tbar)
    print(tempsh)

    sgp = open(
        "/home/metivier/Nextcloud/cours/Field/Meteo/MeteoProject_V2/data/SGP.txt", "r"
    )

    sgp.readline()
    lines = sgp.readlines()
    t_sgp = []
    p_sgp = []
    for line in lines:
        line = line.strip("\n").split(",")
        t_sgp.append(datetime.fromisoformat(line[0]))
        p_sgp.append(float(line[1]))

    print(t_sgp, p_sgp)
    sgp.close()

    latmos = open(
        "/home/metivier/Nextcloud/cours/Field/Meteo/MeteoProject_V2/data/LATMOS.txt",
        "r",
    )

    latmos.readline()
    lines = latmos.readlines()
    t_latmos = []
    p_latmos = []
    for line in lines:
        line = line.strip("\n").split(",")
        t_latmos.append(datetime.fromisoformat(line[0]))
        p_latmos.append(float(line[1]))

    print(t_latmos, p_latmos)
    latmos.close()

    fig, ax = plt.subplots(4, sharex=True)

    for i in range(4):

        if i == 0:
            ax[i].bar(
                tempsh,
                preciph,
                width=(tempsh[1] - tempsh[0]),
                align="edge",
                fc="C2",
                ec="C2",
                alpha=0.2,
                label="1 h",
            )

            ax[i].bar(
                t_sgp,
                p_sgp,
                width=(t_sgp[1] - t_sgp[0]),
                align="edge",
                fc="none",
                ec="C1",
                # alpha=0.4,
                label="Saint Germain",
            )

            ax[i].bar(
                t_latmos,
                p_latmos,
                width=(t_latmos[1] - t_latmos[0]),
                align="edge",
                fc="none",
                ec="C0",
                # alpha=0.4,
                label="LATMOS",
            )

        else:
            tstep = [600, 300, 60]
            tbin, pbin = bin_p(temps, precip, tempsh[0], tstep[i - 1])

            ax[i].bar(
                tbin,
                pbin * 3600 / tstep[i - 1],
                width=(tbin[1] - tbin[0]),
                align="edge",
                fc="C2",
                ec="C2",
                alpha=0.4,
                label="%i mn" % (tstep[i - 1] / 60),
            )

        ax[i].plot(tbar, pbar, "-", color="C4", label="Raw")
        ax[i].legend()

        ax[i].set_xlim(
            (
                datetime(2022, 8, 16, 16, 30, 0),
                datetime(2022, 8, 16, 19, 0, 0),
            )
        )

    myFmt = md.DateFormatter("%H:%M")
    ax[3].xaxis.set_major_formatter(myFmt)
    ax[3].set_xlabel("Time (UTC)")
    fig.autofmt_xdate()

    # beurk !!!
    ax[2].set_ylabel("Rainfall rate (mm/h)")

    plt.savefig("./storm_20220816.pdf", bbox_inches="tight")


if __name__ == "__main__":
    # load_records(fname="METEOLOG_0803.TXT")
    # temp_record()
    # temperature_hour_avg()
    precip_1()
    # precip_compare_16()

    plt.show()
