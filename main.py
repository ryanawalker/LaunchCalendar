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
            'url': "https" + request.host_url.lstrip('http').rstrip('/') + url_for('events_detail', key=self.id),
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
def events_list():
    """
    List or create events.
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
            return event.get_JSON(), status.HTTP_201_CREATED
        else:
            return {"error": "calendar, date, and  name required"}, status.HTTP_400_BAD_REQUEST

    # request.method == 'GET'
    events = Event.query.all()
    return [event.get_JSON() for event in events]


@app.route("/<int:key>/", methods=['GET', 'PUT', 'DELETE'])
def events_detail(key):
    """
    Retrieve, update or delete events instances.
    """
    event = Event.query.get(key)
    
    if request.method == 'PUT':
        
        data_list = str(request.data.get('text', '')).split()
        calendar = data_list[0]
        name = data_list[1]
        date = data_list[2]
        if calendar != '' and name != '' and date != '':
            event.calendar = calendar
            event.name = name
            event.date = datetime.date.fromisoformat(date)
            db.session.add(event)
            db.session.commit()
            return event.get_JSON(), status.HTTP_201_CREATED
        else:
            return {"error": "calendar, date, and  name required"}, status.HTTP_400_BAD_REQUEST
        
        return date_repr(key)

    elif request.method == 'DELETE':
        db.session.delete(event)
        db.session.commit()
        return '', status.HTTP_204_NO_CONTENT

    # request.method == 'GET'
    if not event:
        raise exceptions.NotFound()
    return event.get_JSON()

@app.route("/week", methods=['GET'])
def events_weekly():
    events = Event.query.filter(Event.date > datetime.date.today(), Event.date < datetime.date.today() + datetime.timedelta(7)).all()
    return [event.get_JSON() for event in events]

@app.route("/day", methods=['GET'])
def events_daily():
    events = Event.query.filter(Event.date == datetime.date.today()).all()
    return [event.get_JSON() for event in events]

if __name__ == "__main__":
    app.run(debug=True)
