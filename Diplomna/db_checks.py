from datetime import timedelta, datetime
from flask import session
import mysql.connector


def connect_to_db():
    conn = mysql.connector.connect(host="localhost",user="root",password="",database="swimming_complex")
    return conn

def save_reservation(session, current_date, conn):
    cursor = conn.cursor()
    chairs = session["code"]
    name = session["name"]
    phone = session["phone"]
    booking_hour = session["hour"]
    time = booking_hour.split(":")
    hours = int(time[0])
    minutes = int(time[1])
    expiring_hour = "{}{}{}".format(time[0], ":", str(minutes + 15))
    query = "UPDATE reservations SET status=%s, name=%s, phone_number=%s, date=%s, booking_time=%s, expiring_hour=%s WHERE id=%s;"
    if type(chairs) is list:
        for chair in chairs:
            val = ("reserved", name, phone, current_date, booking_hour, expiring_hour, chair)
            cursor.execute(query, val)
    else:
        val = ("reserved", name, phone,current_date, booking_hour, expiring_hour, chairs)
        cursor.execute(query, val)
    conn.commit()

def check_status(conn, current_time):
    cursor = conn.cursor()
    query = "SELECT id, status, expiring_hour FROM reservations"
    cursor.execute(query)
    records = cursor.fetchall()
    statuses = []
    for row in records:
        row = list(row)
        if row[1] == "reserved":
            reservation_time = row[2].split(":")
            reservation_time = [int(elt) for elt in reservation_time]
            res_hour, res_min = reservation_time[0], reservation_time[1]
            now = current_time.split(":")
            now = [int(elt) for elt in now]
            now_hour, now_min = now[0], now[1]
            query = query = "UPDATE reservations SET status='free', name=NULL, phone_number=NULL, date=NULL, booking_time=NULL, expiring_hour=NULL WHERE id=%s;"
            val = (row[0], )
            if now_min > res_min:
                if now_hour >= res_hour:
                    cursor.execute(query, val)
                    conn.commit()
                    row[1] = "free" 
            elif now_hour > res_hour:
                cursor.execute(query, val)
                conn.commit()
                row[1] = "free"
        cursor.close
        statuses.append(row[1])
    return statuses

def admin_rights(session, conn):
    cursor = conn.cursor()
    chairs = session["code"]
    query = "UPDATE reservations SET status=%s, name=%s, phone_number=%s, date=%s, booking_time=%s, expiring_hour=%s WHERE id=%s;"
    if type(chairs) is list:
        for chair in chairs:
            if session["type"] == "free":
                val = ("free", "NULL", "NULL", "NULL", "NULL", "NULL", chair)
            else:
                val = ("busy", "NULL", "NULL", "NULL", "NULL", "NULL", chair)
            cursor.execute(query, val)
    else:
        if session["type"] == "free":
            val = ("free", "NULL", "NULL", "NULL", "NULL", "NULL", chairs)
        else:
            val = ("busy", "NULL", "NULL", "NULL", "NULL", "NULL", chairs)
        cursor.execute(query, val)
    conn.commit()
    cursor.close()

def measurements(conn):
    cursor = conn.cursor()
    query = "SELECT * FROM measurements WHERE id=(SELECT max(id) FROM measurements)"
    cursor.execute(query)
    records = cursor.fetchall()
    conn.commit()
    cursor.close()
    data = {}
    for row in records:
        data["date_time"] = row[1].strftime("%d/%m/%Y, %H:%M")
        data["pool_temp1"] = row[2]
        data["pool_temp2"] = row[3]
        data["air_temp"] = row[4]
        data["uv_index"] = row[5]
    return data

def show_reservations(conn):
    cursor = conn.cursor()
    query = "SELECT id, name FROM reservations WHERE status='reserved'"
    cursor.execute(query)
    records = cursor.fetchall()
    return records
