import json
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    email = request.form.get('email', '').strip()
    club = next((club for club in clubs if club.get('email') == email), None)

    if club is None:
        flash("Sorry, that email wasn't found.")
        return render_template('index.html')

    return render_template('welcome.html',club=club,competitions=competitions)

@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        availablePoints = int(foundClub['points'])
        availablePlaces = int(foundCompetition['numberOfPlaces'])
        maxPlaces = min(availablePoints, availablePlaces)
        return render_template('booking.html',club=foundClub,competition=foundCompetition,max_places=maxPlaces)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    availablePoints = int(club['points'])
    placesRequired = int(request.form['places'])
    if placesRequired > availablePoints:
        flash('You do not have enough points to book that many places.')
        return render_template(
            'booking.html',
            club=club,
            competition=competition,
            max_places=min(availablePoints, int(competition['numberOfPlaces']))
        )
    competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
    club['points'] = int(club['points']) - placesRequired
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))