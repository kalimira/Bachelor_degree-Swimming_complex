from datetime import  date, time, datetime, timedelta
from flask import Flask, redirect, render_template, request, url_for, session
from db_checks import save_reservation, connect_to_db, check_status, admin_rights, show_reservations, measurements


app = Flask(__name__)
app.secret_key = "secret_key"
chairs = []
conn = connect_to_db()
temp_status = [0 for i in range(1, 41)]
temp_status_admin = [0 for i in range(1, 41)]
all_chairs = []
for elt in range(1, 41):
    all_chairs.append(elt)


@app.route("/admin_changes", methods=["GET", "POST"])
def admin_changes():
    global temp_status_admin
    if "code" not in session:
        return redirect("admin_map")
    if "free" in request.form:
        session["type"] = "free"
    elif "busy" in request.form:
        session["type"] = "busy"
    admin_rights(session, conn)
    temp_status_admin = [0 for i in range(1, 41)]
    session.pop("type")
    session.pop("code")
    return redirect("/admin_map")

@app.route("/admin_map", methods=["GET", "POST"])
def admin_map():
    if "admin" not in session:
        return redirect(url_for("login"))
    else:
        global temp_status_admin
        reservations = show_reservations(conn)
        date_time = datetime.now()
        current_time = date_time.strftime("%H:%M")
        statuses = []
        statuses = check_status(conn, current_time)
        if request.method == "POST":
            temp_code = request.form["code"]
            temp_status_admin[int(temp_code)-1] = 1
            if "code" in session:
                current_code = request.form["code"]
                old_codes = session["code"]
                session["code"] = merge_codes(old_codes, current_code)
            else:
                session["code"] = request.form["code"]
        return render_template("admin_map.html", temp_status=temp_status_admin, chair=all_chairs, status=statuses, reservations=reservations)

@app.route("/delete/<string:code>")
def delete_chair(code):
    global temp_status
    session.modified = True
    session["code"].remove(code)
    temp_status[int(code) - 1] = 0
    return redirect(url_for("reservation"))

@app.route("/", methods=["GET"])
def home():
    data = measurements(conn)
    return render_template("index.html", data=data)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "swimming_complex":
            session["admin"] = request.form["username"]
            return redirect(url_for("admin_map"))
        else:
            error = "Грешно потребителско име или парола. Опитайте отново."
    return render_template("login.html", error=error)

@app.route("/map", methods=["GET", "POST"])
def map():
    global temp_status
    date_time = datetime.now()
    current_date = date_time.strftime("%d/%m/%Y")
    current_time = date_time.strftime("%H:%M")
    hours_added = timedelta(hours=3)
    allowed_time = (date_time + hours_added).strftime("%H:%M")
    statuses = check_status(conn, current_time)
    if request.method == "POST":
        temp_code = request.form["code"]
        if statuses[int(temp_code)-1] == "free":
            temp_status[int(temp_code)-1] = 1
            if "code" in session:
                current_code = request.form["code"]
                old_codes = session["code"]
                session["code"] = merge_codes(old_codes, current_code)
            else:
                session["code"] = request.form["code"]
    return render_template("map.html", temp_status=temp_status, chair=all_chairs, current_date=current_date, current_time=current_time, allowed_time=allowed_time, status=statuses)

@app.route("/reserve", methods=["GET", "POST"])
def reservation():
    error = None
    global temp_status
    date_time = datetime.now()
    current_date = date_time.strftime("%d/%m/%Y")
    current_time = date_time.strftime("%H:%M")
    hours_added = timedelta(hours=3)
    allowed_time = (date_time + hours_added).strftime("%H:%M")
    available_hours = prepare_hours(date_time, timedelta(minutes=30))
    if "code" not in session:
        return redirect("map")
    if (type(session["code"])) == str:
        session["code"] = [(session["code"])]
    if "firstname" and "lastname" in request.form:
        if request.form["firstname"] and request.form["lastname"] and request.form["phone"]:
            session["name"] = "{} {}".format(request.form["firstname"], request.form["lastname"])
            session["phone"] = request.form["phone"]
            session["hour"] = request.form["hour"]
            save_reservation(session, current_date, conn)
            temp_status = [0 for i in range(1, 41)]
            session.clear()
            return redirect("/")
        else:
            error = "Моля въведете желаната информация!"
    return render_template("reserve.html", current_date=current_date, current_time=current_time, allowed_time=allowed_time, available_hours=available_hours, error=error)

def merge_codes(old_codes, current_code):
    if type(old_codes) is list:
        codes = old_codes
        if current_code not in codes:
            codes.append(current_code)
            session["code"] = codes
    else:
        if old_codes != current_code:
            codes = [old_codes, current_code]
            session["code"] = codes
    return session["code"]

def prepare_hours(date_time, delta):
    nearest_time = date_time + (datetime.min - date_time) % delta
    available_hours = []
    for i in range(6):
        available_hours.append(nearest_time.strftime("%H:%M"))
        nearest_time = nearest_time + delta
    hour = available_hours[0]
    temp_hour = hour.split(":")
    current_minute = int(date_time.strftime("%M"))
    temp_hour = [int(hour) for hour in temp_hour]
    if (abs(temp_hour[1] - current_minute) <= 5 or abs(temp_hour[1] - current_minute) >= 55):
        hour = available_hours[5]
        available_hours.pop(0)
        temp_hour = hour.split(":")
        temp_hour = [int(hour) for hour in temp_hour]
        if temp_hour[1] == 30:
            temp_hour[0] = temp_hour[0] + 1
            temp_hour[1] = "00"
        elif temp_hour[1] == 0:
            temp_hour[1] = 30
        additional_hour = ":".join([str(hour) for hour in temp_hour])
        available_hours.append(additional_hour)
    return available_hours

if __name__ == "__main__":
    app.run()
