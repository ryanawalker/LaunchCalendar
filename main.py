from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
import datetime

app = FlaskAPI(__name__)


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
            idx = max(dates.keys()) + 1
            dates[idx] = {"calendar": calendar, "name": name, "date": datetime.date.fromisoformat(date)}
            return date_repr(idx), status.HTTP_201_CREATED
        else:
            return {"error": "calendar, date, and  name required"}, status.HTTP_400_BAD_REQUEST

    # request.method == 'GET'
    return [date_repr(idx) for idx in sorted(dates.keys())]


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