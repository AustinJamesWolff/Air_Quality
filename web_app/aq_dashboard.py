"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import openaq

APP = Flask(__name__)

APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(APP)

API = openaq.OpenAQ()


def get_results():
    status, body = API.measurements(city='Los Angeles', parameter='pm25')
    get_tuples = []
    for result in body['results']:
        get_tuples.append((result['date']['utc'], result['value']))
    return get_tuples


class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f'<Time {self.datetime} ----- Value {self.value}>'

    def __getitem__(self, field):
        return self.__dict__[field]


@APP.route('/')
def root():
    """Base view."""
    results = Record.query.filter(Record.value >= 10).all()
    return str(list(results))

    # datas = []
    # for i, result in enumerate(results):
    #     datas.append((result[i].datetime, result[i].value))
    # return str(datas)

    # return str(Record.query.filter(Record.value >= 10).all())


@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    # TODO Get data from OpenAQ, make Record objects with it, and add to db
    list_data = get_results()
    for i, result in enumerate(list_data):
        db_record = Record(id=i,
                           datetime=result[0],
                           value=result[1])
        DB.session.add(db_record)
    DB.session.commit()
    return 'Data refreshed!'
