from flask import request, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_api import FlaskAPI, status, exceptions
import datetime


app = FlaskAPI(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://launchcalendar:launch@localhost:8889/launchcalendar'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Event(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    date = db.Column(db.Date)
    calendar = db.Column(db.String(120))

    def __init__(self, calendar: str, name: str, date: str):
        self.calendar = calendar
        self.name = name
        self.date = datetime.date.fromisoformat(date)

    def get_JSON(self):
        return {
            'url': "https" + request.host_url.lstrip('http').rstrip('/') + url_for('dates_detail', key=self.id),
            "calendar": self.calendar,
            "name": self.name,
            "date": self.date
        }

dates = {
    0: {"calendar": "LC101", "name": "Ryan", "date": datetime.date.fromisoformat("2018-05-22")},
    1: {"calendar": "Liftoff", "name": "Dave", "date": datetime.date.fromisoformat("2018-07-04")},
    2: {"calendar": "LC101", "name": "Matt", "date": datetime.date.fromisoformat("2018-07-30")},
    3: {"calendar": "LC101", "name": "Koko", "date": datetime.date.fromisoformat("2018-08-23")},
    4: {"calendar": "Liftoff", "name": "Blake", "date": datetime.date.fromisoformat("2018-09-03")}
}

def date_repr(key):
    return {
        'url': "https" + request.host_url.lstrip('http').rstrip('/') + url_for('dates_detail', key=key),
        "calendar": dates[key]["calendar"],
        "name": dates[key]["name"],
        "date": dates[key]["date"].isoformat()
    }


@app.route("/", methods=['GET', 'POST'])
def dates_list():
    """
    List or create dates.
    """
    if request.method == 'POST':
        data_list = str(request.data.get('text', '')).split()
        calendar = data_list[0]
        name = data_list[1]
        date = data_list[2]
        if calendar != '' and name != '' and date != '':
            event = Event(calendar, name, date)
            db.session.add(event)
            db.session.commit()
            return event.getJSON(), status.HTTP_201_CREATED
        else:
            return {"error": "calendar, date, and  name required"}, status.HTTP_400_BAD_REQUEST

    # request.method == 'GET'
    events = Event.query.all()
    return [event.get_JSON() for event in events]


@app.route("/<int:key>/", methods=['GET', 'PUT', 'DELETE'])
def dates_detail(key):
    """
    Retrieve, update or delete date instances.
    """
    if request.method == 'PUT':
        date = str(request.data.get('name', ''))
        dates[key] = date
        return date_repr(key)

    elif request.method == 'DELETE':
        dates.pop(key, None)
        return '', status.HTTP_204_NO_CONTENT

    # request.method == 'GET'
    if key not in dates:
        raise exceptions.NotFound()
    return date_repr(key)

@app.route("/week", methods=['GET'])
def dates_weekly():
    return [date_repr(idx) for idx in sorted(dates.keys()) if datetime.date.today() - dates[idx]["date"] < datetime.timedelta(7) and dates[idx]["date"] > datetime.date.today()]

if __name__ == "__main__":
    app.run(debug=True)