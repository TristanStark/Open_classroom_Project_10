import json
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    flash,
    url_for
)

MAX_PLACES_PER_BOOKING = 12

def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def getMaxBookablePlaces(club, competition):
    return min(
        int(club['points']),
        int(competition['numberOfPlaces']),
        MAX_PLACES_PER_BOOKING
    )

def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions

def redeemPlaces(club, competition, placesRequired):
    """Deduct booked places from both the competition and the club balance."""
    availablePoints = int(club['points'])
    availablePlaces = int(competition['numberOfPlaces'])

    competition['numberOfPlaces'] = availablePlaces - placesRequired
    club['points'] = availablePoints - placesRequired


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

    return render_template(
        'welcome.html',
        club=club,
        competitions=competitions,
        clubs=clubs
    )

@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        maxPlaces = getMaxBookablePlaces(foundClub, foundCompetition)
        return render_template('booking.html',club=foundClub,competition=foundCompetition,max_places=maxPlaces)
    else:
        flash("Something went wrong-please try again")
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions,
            clubs=clubs
        )


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    availablePoints = int(club['points'])
    availablePlaces = int(competition['numberOfPlaces'])
    placesRequired = int(request.form['places'])
    if placesRequired > MAX_PLACES_PER_BOOKING:
        flash('You cannot book more than 12 places for one competition.')
        return render_template(
            'booking.html',
            club=club,
            competition=competition,
            max_places=getMaxBookablePlaces(club, competition)
        )
    if placesRequired > availablePoints:
        flash('You do not have enough points to book that many places.')
        return render_template(
            'booking.html',
            club=club,
            competition=competition,
            max_places=getMaxBookablePlaces(club, competition)
        )
    if placesRequired > availablePlaces:
        flash('There are not enough places remaining for that competition.')
        return render_template(
            'booking.html',
            club=club,
            competition=competition,
            max_places=getMaxBookablePlaces(club, competition)
        )

    redeemPlaces(club, competition, placesRequired)
    flash('Great-booking complete!')
    return render_template(
        'welcome.html',
        club=club,
        competitions=competitions,
        clubs=clubs
    )


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
