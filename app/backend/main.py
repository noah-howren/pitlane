# Python file responsible for site backend implemented by Anthony Ganci
from flask import Flask, jsonify, request
from flask_cors import CORS
import fastf1
from fastf1 import plotting
import io
import base64
import numpy as np
import matplotlib as mpl
from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import pandas as pd
import warnings
import requests
from database.py import *

warnings.simplefilter(action='ignore', category=FutureWarning)
# non-interactive matplotlib backend
mpl.use('agg')

app = Flask(__name__)
app.config.from_object(__name__)

CORS(app, resources={r"/*":{'origins':"*"}})
@app.route("/", methods=['GET'])
def index():
    return (jsonify({'status': 200, 'message' :'Welcome to the Pitlane 🏎️'}))

@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if request.method == 'POST':
        post_data = request.get_json()
        year = post_data.get('season')
        path = f'https://ergast.com/api/f1/{year}.json'
        response = requests.get(path)
        jsondump = response.json()
        schedule = []
        for i in range(0, int(jsondump['MRData']['total'])):
            schedule.append((jsondump['MRData']['RaceTable']['Races'][i]['raceName'], jsondump['MRData']['RaceTable']['Races'][i]['date'], jsondump['MRData']['RaceTable']['Races'][i]['time']))
        return(jsonify({'status': 200, 'schedule': schedule, 'season': jsondump['MRData']['RaceTable']['season'] }))
    if request.method == 'GET':
        # year = request.headers['year']
        body = request.get_json()
        year = body.get('season')
        path = f'https://ergast.com/api/f1/{year}.json'
        response = requests.get(path)
        jsondump = response.json()
        schedule = []
        for i in range(0, int(jsondump['MRData']['total'])):
            schedule.append((jsondump['MRData']['RaceTable']['Races'][i]['raceName'], jsondump['MRData']['RaceTable']['Races'][i]['date'], jsondump['MRData']['RaceTable']['Races'][i]['time']))
        return(jsonify({'status': 200, 'schedule': schedule, 'season': jsondump['MRData']['RaceTable']['season']}))

@app.route('/schedule/nextprev', methods=['POST'])
def nextprev():
    if request.method == 'POST':
        post_data = request.get_json()
        isOffseason = post_data.get('Offseason')
        if isOffseason:
            response = requests.get('https://ergast.com/api/f1/current.json')
            total = int(response.json()['MRData']['total'])-1
            prevRace = response.json()['MRData']['RaceTable']['Races'][total]['raceName']
            prevRaceDate = response.json()['MRData']['RaceTable']['Races'][total]['date']
            prevRaceID = f"/track/{response.json()['MRData']['RaceTable']['Races'][total]['Circuit']['circuitId']}"
            nextSeason = int(response.json()['MRData']['RaceTable']['season']) + 1
            nextSeasonTable = requests.get(f'https://ergast.com/api/f1/{nextSeason}/1.json')
            nextRace = nextSeasonTable.json()['MRData']['RaceTable']['Races'][0]['raceName']
            nextRaceDate = nextSeasonTable.json()['MRData']['RaceTable']['Races'][0]['date']
            nextRaceID = f"/track/{nextSeasonTable.json()['MRData']['RaceTable']['Races'][0]['Circuit']['circuitId']}"
            print(nextRaceID, prevRaceID)
            return(jsonify({'status': 200, 'prevRace': [prevRace, prevRaceDate, prevRaceID], 'nextRace': [nextRace, nextRaceDate, nextRaceID]}))

@app.route("/standings", methods=['GET', 'POST'])
def standings():
    if request.method == 'GET':
        standings = getStandings(0)
        return(jsonify({'status': 200, 'drivers': standings}))
    if request.method == 'POST':
        post_data = request.get_json()
        standings = getStandings(int(post_data.get('year')))
        return(jsonify({'status': 200, 'standings': standings}))

@app.route("/pitlane", methods=['GET', 'POST'])
def pitlane():
    fastf1.Cache.enable_cache('cache/')
    if request.method == 'POST':
        post_data = request.get_json()['form']
        print(request.get_json())
        if post_data['method'] == 'h2h':
            # data dictionary for the form data retreived
            DATA = {'driver1': '', 'driver2': '', 'track': '', 'year': 0, 'session' : ''}
            DATA.update({
                'driver1': post_data.get('driver1'),
                'driver2': post_data.get('driver2'),
                'track': post_data.get('track'),
                'year': int(post_data.get('year')),
                'session': post_data.get('session')
            })
            plotting.setup_mpl()
            race = fastf1.get_session(DATA['year'], DATA['track'], DATA['session'])
            race.load()

            driver1Name = race.get_driver(DATA['driver1'])['LastName']
            driver2Name = race.get_driver(DATA['driver2'])['LastName']
            driver1 = race.laps.pick_driver(DATA['driver1'])
            driver2 = race.laps.pick_driver(DATA['driver2'])
            driver1Color = plotting.driver_color(DATA['driver1'])
            driver2Color = plotting.driver_color(DATA['driver2'])

            # Based on information given by FastF1 documentation on how to do basic plotting
            fig, ax = plt.subplots(figsize=(10, 6.75))
            title = plt.suptitle(
                f"Driver Head-to-Head\n"
                f"{race.event['EventName']} {race.event.year}\n"
                f"{driver1Name} vs. {driver2Name}")
            line1, = ax.plot(driver1['LapNumber'], driver1['LapTime'], color=driver1Color, label=driver1Name)
            line2, = ax.plot(driver2['LapNumber'], driver2['LapTime'], color=driver2Color, label=driver2Name)
            # ax.set_title(f"{driver1Name} vs. {driver2Name}")
            ax.set_xlabel("Lap Number")
            ax.set_ylabel("Lap Time")
            ax.legend(handles=[line1, line2])
            
            # converting matplotlib image to base64 so i can display it easy
            pngImage = io.BytesIO()
            FigureCanvas(fig).print_png(pngImage)

            pngImageB64String = "data:image/png;base64,"
            pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')
            return jsonify({'src': pngImageB64String, 'status': 'success'})
        if post_data['method'] == 'gear':
            # data dictionary for the form data retreived
            DATA = {'track': '', 'year': 0, 'session' : ''}
            DATA.update({
                'track': post_data.get('track'),
                'year': int(post_data.get('year')),
                'session': post_data.get('session')
            })
            plotting.setup_mpl()

            session = fastf1.get_session(DATA['year'], DATA['track'], DATA['session'])
            session.load()

            lap = session.laps.pick_fastest()
            lastname = session.get_driver(lap['Driver'])['LastName']

            # Based on information given by FastF1 documentation on how to do basic plotting
            tel = lap.get_telemetry()

            x = np.array(tel['X'].values)
            y = np.array(tel['Y'].values)

            points = np.array([x, y]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)
            gear = tel['nGear'].to_numpy().astype(float)

            fig = plt.figure(figsize=(10, 6.75))
            # cmap = cm.get_cmap('gnuplot', 8)
            cmap = cm.get_cmap('plasma', 8)
            lc_comp = LineCollection(segments, norm=plt.Normalize(1, cmap.N+1), cmap=cmap)
            lc_comp.set_array(gear)
            lc_comp.set_linewidth(4)

            plt.gca().add_collection(lc_comp)
            plt.axis('equal')
            plt.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

            title = plt.suptitle(
                f"Fastest Lap Gear Shift\n"
                f"{lastname} - {session.event['EventName']} {session.event.year}"
            )

            cbar = plt.colorbar(mappable=lc_comp, label="Gear", boundaries=np.arange(1, 10))
            cbar.set_ticks(np.arange(1.5, 9.5))
            cbar.set_ticklabels(np.arange(1, 9))

            # converting matplotlib image to base64 so i can display it easy
            pngImage = io.BytesIO()
            FigureCanvas(fig).print_png(pngImage)

            pngImageB64String = "data:image/png;base64,"
            pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')
            return jsonify({'src': pngImageB64String, 'status': 'success'})
        if post_data['method'] == 'speed':
            # data dictionary for the form data retreived
            DATA = {'driver': '', 'track': '', 'year': 0, 'session' : ''}
            DATA.update({
                'driver': post_data.get('driver'),
                'track': post_data.get('track'),
                'year': int(post_data.get('year')),
                'session': post_data.get('session')
            })
            
            plotting.setup_mpl()
            session = fastf1.get_session(DATA['year'], DATA['track'], DATA['session'])
            session.load()
            lap = session.laps.pick_driver(DATA['driver']).pick_fastest()
            lastname = session.get_driver(lap['Driver'])['LastName']
            colormap = mpl.cm.plasma
            
            # Based on information given by FastF1 documentation on how to do basic plotting
            x = lap.telemetry['X']              
            y = lap.telemetry['Y']              
            color = lap.telemetry['Speed']      

            points = np.array([x, y]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)

            fig, ax = plt.subplots(sharex=True, sharey=True, figsize=(10, 6.75))
            title = plt.suptitle(
                f"Fastest Lap Speed Visualization\n"
                f"{lastname} - {session.event['EventName']} {session.event.year}\n"
            )
            plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.12)
            ax.axis('off')
            ax.plot(lap.telemetry['X'], lap.telemetry['Y'], color='black', linestyle='-', linewidth=16, zorder=0)
            norm = plt.Normalize(color.min(), color.max())
            lc = LineCollection(segments, cmap=colormap, norm=norm, linestyle='-', linewidth=5)
            lc.set_array(color)
            line = ax.add_collection(lc)
            cbaxes = fig.add_axes([0.25, 0.05, 0.5, 0.05])
            normlegend = mpl.colors.Normalize(vmin=color.min(), vmax=color.max())
            legend = mpl.colorbar.ColorbarBase(cbaxes, norm=normlegend, cmap=colormap, orientation="horizontal")
            
            # converting matplotlib image to base64 so i can display it easy
            pngImage = io.BytesIO()
            FigureCanvas(fig).print_png(pngImage)

            pngImageB64String = "data:image/png;base64,"
            pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')
            return jsonify({'src': pngImageB64String, 'status': 'success'})

    if request.method == 'GET':    
        # return jsonify({'msg': "Welcome to Pitlane 🏎️! Enter information to get started!", 'status': 'success'})
        return jsonify({'status': 'success'})

# MOVED ALL OTHER DATABASE FUNCTIONS (and the new create_league and create_team functions to app/backend/database.py)

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=3001)