"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
Modified
"""

# Python modules
import json
import os
import sqlite3
import pandas as pd
from io import StringIO
import csv
import time

# Flask modules
from flask import render_template, request, url_for, redirect, send_from_directory, make_response
from flask_login import login_user, logout_user, current_user, login_required

# Import App modules
from app import app, lm
from app.models import User
from app.forms import LoginForm, RegisterForm
from app.cleanEmpress import find_species_and_types, clean_df
from app.dbscan import dbscan
from app.kmeans import kmeans

from rq import Queue
from worker import conn

q = Queue(connection=conn)


# Allow user to export data as .csv file
@app.route('/export.html', methods=['POST'])
@login_required
def export():
    try:
        if 'empres' in request.form:

            # Connect to the database.db
            si = StringIO()
            cw = csv.writer(si)
            path = 'app/database.db'
            con = sqlite3.connect(path)
            cur = con.execute('select * from empres')
            rows = cur.fetchall()
            cw.writerow([c[0] for c in cur.description])
            cw.writerows(rows)
            response = make_response(si.getvalue())
            response.headers['Content-Disposition'] = 'attachment; filename=empres.csv'
            response.headers["Content-type"] = "text/csv"
            return response

        elif 'dbscan' in request.form:
            path = 'app/database.db'
            con = sqlite3.connect(path)
            df = pd.read_sql_query(
                "SELECT * FROM empres WHERE serotypes = 'H5N1 HPAI' ORDER BY "
                "datetime(reportingDate) ASC", con)
            grouped = [pd.DataFrame(y) for x, y in df.groupby('quarters', as_index=False)]
            dfs, hov = dbscan(grouped)

            response = make_response(dfs.to_csv())
            response.headers['Content-Disposition'] = 'attachment; filename=dbscan.csv'
            response.headers["Content-type"] = "text/csv"
            return response

        elif 'kmeans' in request.form:
            path = 'app/database.db'
            con = sqlite3.connect(path)
            df = pd.read_sql_query(
                "SELECT * FROM empres WHERE serotypes = 'H5N1 HPAI' ORDER BY "
                "datetime(reportingDate) ASC", con)
            grouped = [pd.DataFrame(y) for x, y in df.groupby('quarters', as_index=False)]
            dfs, hov = kmeans(grouped)
            response = make_response(dfs.to_csv())
            response.headers['Content-Disposition'] = 'attachment; filename=k-means.csv'
            response.headers["Content-type"] = "text/csv"
            return response

    except sqlite3.OperationalError:
        return render_template('layouts/default.html',
                               content=render_template('pages/export.html'))


# Present analyzed data of HPAI H5N1
@app.route('/analysis.html', methods=['GET'])
@login_required
def analysis():
    if request.method == 'GET':
        try:
            # Connect to the database.db
            path = 'app/database.db'
            con = sqlite3.connect(path)
            cur = con.cursor()
            # Fetch necessary data from db

            info = cur.execute("SELECT quarters, count(*), region, speciesType FROM empres WHERE serotypes = 'H5N1 "
                               "HPAI' GROUP BY quarters ORDER BY datetime(reportingDate) ASC").fetchall()

            human = cur.execute(
                "SELECT quarters, count(*), region FROM empres WHERE serotypes = 'H5N1 HPAI' AND speciesType "
                "= 'human' GROUP BY quarters ORDER BY datetime(reportingDate) ASC").fetchall()

            animal = cur.execute("SELECT quarters, count(*) FROM empres WHERE serotypes = 'H5N1 HPAI' AND speciesType "
                                 "!= 'human' GROUP BY quarters ORDER BY datetime(reportingDate) ASC").fetchall()

            df_h = pd.read_sql_query(
                "SELECT * FROM empres WHERE serotypes = 'H5N1 HPAI' AND speciesType = 'human' ORDER BY "
                "datetime(reportingDate) ASC", con)
            grouped_h = [pd.DataFrame(y) for x, y in df_h.groupby('quarters', as_index=False)]

            df_an = pd.read_sql_query(
                "SELECT * FROM empres WHERE serotypes = 'H5N1 HPAI' AND speciesType != 'human' ORDER BY "
                "datetime(reportingDate) ASC", con)
            grouped_an = [pd.DataFrame(y) for x, y in df_an.groupby('quarters', as_index=False)]

            dfs_db, hover_db = dbscan(grouped_h)
            dfs_db_an, hover_db_an = dbscan(grouped_an)

            # Queue jobs
            # job_db_h = q.enqueue(dbscan, grouped_h, result_ttl=800)
            job_km_h = q.enqueue(kmeans, grouped_h, result_ttl=800)
            # job_db_a = q.enqueue(dbscan, grouped_an, result_ttl=800)
            job_km_a = q.enqueue(kmeans, grouped_an, result_ttl=800)
            while job_km_a.is_finished is False:
                time.sleep(0.5)
            # if job_db_h.is_finished:
            # Find human cluster using dbscan
            #   dfs_db, hover_db = job_db_h.result
            if job_km_h.is_finished:
                # Find human cluster using kmeans
                dfs_km, hover_km = job_km_h.result
            # if job_db_a.is_finished:
            # Find animal cluster using dbscan
            #    dfs_db_an, hover_db_an = job_db_a.result
            if job_km_a.is_finished:
                # Find animal cluster using kmeans
                dfs_km_an, hover_km_an = job_km_a.result


            return render_template('layouts/default.html',
                                   content=render_template('pages/analysis.html', info=json.dumps(info),
                                                           human=json.dumps(human), animal=json.dumps(animal),
                                                           rs_db=json.dumps(dfs_db.values.tolist()), hov_db=json.dumps(hover_db),
                                                           rs_km=json.dumps(dfs_km.values.tolist()), hov_km=json.dumps(hover_km),
                                                           rs_db_an=json.dumps(dfs_db_an.values.tolist()),
                                                           hov_db_an=json.dumps(hover_db_an),
                                                           rs_km_an=json.dumps(dfs_km_an.values.tolist()),
                                                           hov_km_an=json.dumps(hover_km_an)
                                                           ))
        except sqlite3.OperationalError:
            return render_template('layouts/default.html',
                                   content=render_template('pages/analysis.html'))


# Present heatmap of all data using Google Maps API
@app.route('/allTime.html', methods=['GET'])
@login_required
def view_map_all():
    try:
        if request.method == 'GET':
            # Connect to the database.db
            path = 'app/database.db'
            con = sqlite3.connect(path)
            cur = con.cursor()
            all_lat = cur.execute("SELECT latitude FROM empres").fetchall()
            all_long = cur.execute("SELECT longitude FROM empres").fetchall()
            return render_template('layouts/default.html',
                                   content=render_template('pages/allTime.html',
                                                           lat=json.dumps(all_lat), long=json.dumps(all_long)))

    except sqlite3.OperationalError:
        return render_template('layouts/default.html',
                               content=render_template('pages/allTime.html'))


# Query data and redirect to the correct page
@app.route('/query.html', methods=['GET', 'POST'])
@login_required
def query():
    if request.method == 'POST':
        # Get data from request form

        # Serotypes
        hpai = request.form.getlist('hpai')
        lpai = request.form.getlist('lpai')
        seros = hpai + lpai

        # Region
        region = request.form.getlist('region')

        # Types
        types = request.form.getlist('type')

        # Reporting Date
        to_date = request.form.get('to_date')

        from_date = request.form.get('from_date')

        from_d = [from_date]
        to_d = [to_date]

        # Connect to the database.db
        path = 'app/database.db'
        con = sqlite3.connect(path)
        cur = con.cursor()

        # Query data
        sql = """SELECT * FROM empres WHERE serotypes IN ({0}) AND region IN ({1})  AND speciesType IN ({2})
        AND date(reportingDate) <= date(?) AND date(reportingDate) >= date(?)
        ORDER BY datetime(reportingDate)
        ASC""".format(','.join(['?'] * len(seros)), ','.join(['?'] * len(region)), ','.join(['?'] * len(types)))
        data = cur.execute(sql, (seros + region + types + to_d + from_d)).fetchall()

        button = request.form['action']
        if button == "Heatmap":
            return render_template('layouts/default.html',
                                   content=render_template('pages/heatmap.html', data=json.dumps(data)))

        elif button == "Markers":
            return render_template('layouts/default.html',
                                   content=render_template('pages/interactive.html', data=json.dumps(data)))

        else:
            return render_template('layouts/default.html',
                                   content=render_template('pages/view.html', data=data))

    if request.method == 'GET':
        hpai = ['H5 HPAI', 'H5N1 HPAI', 'H5N2 HPAI', 'H5N5 HPAI', 'H5N6 HPAI', 'H5N8 HPAI',
                'H5N9 HPAI', 'H7N1 HPAI', 'H7 HPAI', 'H7N2 HPAI', 'H7N3 HPAI', 'H7N7 HPAI',
                'H7N9 HPAI', 'H9 HPAI']

        lpai = ['H3N1 LPAI', 'H2N2 LPAI', 'H5 LPAI', 'H5N1 LPAI', 'H5N2 LPAI', 'H5N3 LPAI',
                'H5N5 LPAI', 'H5N6 LPAI', 'H5N9 LPAI', 'H5N8 LPAI', 'H6N2 LPAI', 'H7 LPAI', 'H7N1 LPAI',
                'H7N2 LPAI', 'H7N3 LPAI', 'H7N4 LPAI', 'H7N6 LPAI', 'H7N7 LPAI', 'H7N8 LPAI', 'H7N9 LPAI',
                'H9 LPAI', 'H9N2 LPAI', 'H10N7 LPAI', 'H10N8 LPAI']

        region = ['Europe', 'Asia', 'Africa', 'Americas', 'Oceania']

        types = ['wild', 'domestic', 'captive', 'human']

        return render_template('layouts/default.html',
                               content=render_template('pages/query.html',
                                                       lpai=lpai, hpai=hpai, region=region, types=types))


# Import data to sqlite
@app.route('/importData.html', methods=['POST'])
@login_required
def import_data():
    if request.method == 'POST':
        df = pd.read_csv(request.files.get('file'), index_col='Id')

        df['speciesType'], df['species'] = zip(
            *df['speciesDescription'].apply(lambda x: find_species_and_types(x)))
        # Remove rows that does not have a confirmed status

        empres_df = clean_df(df)

        # Connect to the database.db
        path = 'app/database.db'
        con = sqlite3.connect(path)
        cur = con.cursor()

        empres_df.to_sql("empres", con, if_exists="append")

        try:
            # Remove duplicates rows
            remove_duplicates = """DELETE FROM empres WHERE rowid NOT IN (SELECT MIN(rowid) FROM empres 
            GROUP BY Id, source, latitude, longitude, region, country, admin1, localityName, localityQuality,
            observationDate, reportingDate, quarters, serotypes, speciesType, species, sumAtRisk, sumCases,
            sumDeaths, sumDestroyed, sumSlaughtered, humansGenderDesc, humansAge, humansAffected, humansDeaths)"""
            cur.execute(remove_duplicates)
            con.commit()
            con.close()

        except sqlite3.OperationalError:
            return render_template('layouts/default.html',
                                   content=render_template('pages/importSuccess.html'))

        return render_template('layouts/default.html',
                               content=render_template('pages/importSuccess.html'))


# Display data
@app.route('/viewEmpres.html')
@login_required
def display_data():
    try:
        # Connect to the database.db
        path = 'app/database.db'
        con = sqlite3.connect(path)
        cur = con.cursor()

        con.row_factory = sqlite3.Row
        rows = cur.execute("select * from empres ORDER BY Id ASC").fetchall()
        return render_template('layouts/default.html',
                               content=render_template('pages/viewEmpres.html', rows=rows))

    except sqlite3.OperationalError:
        return render_template('layouts/default.html',
                               content=render_template('pages/viewEmpres.html'))


# provide login manager with load_user callback
@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Logout user
@app.route('/logout.html')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# Register a new user
@app.route('/register.html', methods=['GET', 'POST'])
def register():
    # cut the page for authenticated users
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # declare the Registration Form
    form = RegisterForm(request.form)

    msg = None

    if request.method == 'GET':
        return render_template('layouts/default.html',
                               content=render_template('pages/register.html', form=form, msg=msg))

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str)
        email = request.form.get('email', '', type=str)

        # filter User out of database through username
        user = User.query.filter_by(user=username).first()

        # filter User out of database through username
        user_by_email = User.query.filter_by(email=email).first()

        if user or user_by_email:
            msg = 'Error: User exists!'

        else:
            user = User(username, email, password)

            user.save()

            msg = 'User created, please <a href="' + url_for('login') + '">login</a>'

    else:
        msg = 'Input error'

    return render_template('layouts/default.html',
                           content=render_template('pages/register.html', form=form, msg=msg))


# Authenticate user
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    # cut the page for authenticated users
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # Declare the login form
    form = LoginForm(request.form)

    # Flask message injected into the page, in case of any errors
    msg = None

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str)

        # filter User out of database through username
        user = User.query.filter_by(user=username).first()

        if user:
            if User.is_correct_password(user, password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                msg = "Wrong password. Please try again."
        else:
            msg = "Unknown user"

    return render_template('layouts/default.html',
                           content=render_template('pages/login.html', form=form, msg=msg))


# App main route + generic routing
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path>')
def index(path):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    try:
        # Connect to the database.db
        path_db = 'app/database.db'
        con = sqlite3.connect(path_db)
        cur = con.cursor()
        seros = cur.execute("SELECT serotypes, count(serotypes) FROM empres GROUP BY serotypes").fetchall()

        dates = cur.execute(
            "SELECT strftime('%Y-%m', reportingDate), count(*) "
            "FROM empres WHERE date(reportingDate) >= date('now','-10 months') GROUP BY strftime('%Y-%m', "
            "reportingDate)").fetchall()

        quarters = cur.execute("SELECT quarters, count(quarters) "
                               "FROM empres WHERE date(reportingDate) >= date('2011-01-01') GROUP BY quarters").fetchall()

        region = cur.execute("SELECT region, count(region) FROM empres GROUP BY region").fetchall()
        # try to match the pages defined in -> pages/<input file>
        return render_template('layouts/default.html',
                               content=render_template('pages/' + path,
                                                       seros=json.dumps(seros), dates=json.dumps(dates),
                                                       quarters=json.dumps(quarters),
                                                       region=json.dumps(region)))

    except sqlite3.OperationalError:
        return render_template('layouts/default.html',
                               content=render_template('pages/' + path))

    except:
        return render_template('layouts/auth-default.html',
                               content=render_template('pages/404.html'))


# Fix favicon error
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


# Return sitemap
@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'sitemap.xml')
