# Application maintains city population records in a DB and includes
# a route to look up a city's population given its name.  

# To run application you need to first install the following:
# SQLite:     sudo apt-get install sqlite
# SQLAlchemy: pip3 install flask-sqlalchemy
#
# Then create the tables in SQLite. DO THIS BEFORE RUNNING APP.
# Create FLASK_APP and FLASK_DEBUG:
# export FLASK_APP=cities.py
# export FLASK_DEBUG=1
# Run Flask in shell mode:  python3 -m flask shell
# At the shell, type:     from cities import db
# And then:               db.create_all()
# To delete tables+data:  db.drop_all() 

import os
from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)


# Database model defining a single table cities that contains
# city name and population. 
class City(db.Model):
    __tablename__ = 'cities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    population = db.Column(db.Integer, unique=False)

    def __repr__(self):
        return self.name + ':' + str(self.population)


class AddCityForm(FlaskForm):
    name = StringField('City name: ', validators=[DataRequired()])
    population = StringField('Population: ', validators=[DataRequired()])
    submit = SubmitField('Submit')


class LookupForm(FlaskForm):
    name = StringField('City name: ', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/add_city', methods=['GET', 'POST'])
def add_city():
    form = AddCityForm()
    if form.validate_on_submit():
        # First check if the city exists already
        city = City.query.filter_by(name=form.name.data).first()
        # Add record
        if city is None:
            city = City(name=form.name.data, population=form.population.data)
            db.session.add(city)
            db.session.commit()
        form.name.data = ""
        form.population.data = ""
    return render_template('index.html', form=form)


@app.route('/lookup_city', methods=['GET', 'POST'])
def find_city():
    form = LookupForm()
    city_name = None
    city_population = None
    if form.validate_on_submit():
        city_record = City.query.filter_by(name=form.name.data).first()
        form.name.data = ""
        if city_record:
            city_name = city_record.name
            city_population = city_record.population
    return render_template('lookup.html', form=form,
                           name=city_name, population=city_population)
