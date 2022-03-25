"""FPL_Analytics app."""
from flask import Flask, redirect, render_template, url_for, flash, session, g, jsonify, request
from flask_debugtoolbar import DebugToolbarExtension
from flask_cors import CORS
from models import db, connect_db, Player, Team, User
from forms import RegisterForm, LoginForm, UserEditDataForm, UserEditPasswordForm
from sqlalchemy.exc import IntegrityError
import requests
import os
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','postgresql:///fpl_analytics')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "shh")
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

CORS(app)

connect_db(app)
db.create_all()

CURR_USER_KEY = "curr_user"
team_names = {}
BASE_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"

##############################################################################
# Helper functions
def do_log_in(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id

def do_log_out():
    """Log out user."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

def check_logged_in():
    """Check if user is logged in."""
    return CURR_USER_KEY in session

def get_all_data():
    """Query FPL website and get all data."""
    db.drop_all()
    db.create_all()

    all_data = requests.get(BASE_URL).json()

    for team in all_data["teams"]:
        db.session.add(Team(id=team["id"], name=team["name"], photo_code=team["code"]))
        team_names[team["id"]] = team["name"]
    db.session.commit()

    for player in all_data["elements"]:
        p = Player(id=player["id"], first_name=player["first_name"], last_name=player["second_name"], photo_code=player["code"], 
                    team_id=player["team"], now_cost=player["now_cost"]/10, ppg=player["points_per_game"], total_points=player["total_points"]
        )
        db.session.add(p)
    db.session.commit()

    user = User.signup(first_name="Damilola", last_name="Olaiya", email="daolaiya@gmail.com", user_name="d_olaiya", password="password", team_name="Damilola United")
    user.user_players = "1,2,3,4,5,6,7,8,9,10"
    
    db.session.add(user)
    db.session.commit()

###############################################################################################################################################################################
# General routes
@app.route("/")
def root():
    """Home page."""
    return render_template("home.html")

@app.route("/test")
def test_route():
    """Test route."""
    print(json.dumps(5))
    print(json.dumps([1,2,3,4,5]))
    print(json.dumps({"a":5,"b":10}))
    return jsonify(5)

    # return jsonify(5)
    # return "5"
    # return json.dumps(5)
    
    # redirect_url = url_for("my_team")
    # return redirect(redirect_url)

@app.route("/admin")
def admin():
    """Admin route."""
    if check_logged_in():
        return render_template("admin.html") 
    
    else:
        flash("User must be logged in to access Admin page")
        return redirect(url_for("root"))

@app.route("/login", methods=["GET", "POST"])
def log_in_user():
    """
    Form to log in user:

    - if form not filled out or invalid: show form
    - if valid: sign_in user and redirect to home page
    """
    form = LoginForm()

    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != "csrf_token"}
        user = User.authenticate(user_name = data["user_name"], password=data["password"])

        if user:
            do_log_in(user)
            flash(f"User {user.user_name} logged in.")
            return redirect(url_for("root"))
        else:
            flash(f"Incorrect credentials.")
            return redirect(url_for("log_in_user"))
    else:
        return render_template("login_user.html",form=form)

@app.route("/logout")
def log_out_user():
    """Log out user."""
    if not check_logged_in():
        flash("User not logged in.")
        return redirect(url_for("root"))
    else:
        flash(f"User logged out.")
        do_log_out()
        return redirect(url_for("root"))

@app.route("/update-db")
def update_db():
    """Update DB."""
    if check_logged_in():
        get_all_data()
        session["team_names"] = team_names
        flash("DB updated!")
        return redirect(url_for("admin"))
    else:
        return redirect(url_for("not_logged_in"))

@app.route("/clear-db")
def clear_db():
    """Clear DB."""
    if check_logged_in():
        db.drop_all()
        db.create_all()
        do_log_out()

        new_user = User.signup(first_name="Damilola", last_name="Olaiya", email="daolaiya@gmail.com", user_name="d_olaiya", password="password", team_name="Damilola United")
        new_user.user_players = "1,2,3,4,5,6,7,8,9,10"
        
        do_log_in(new_user)

        flash("DB cleared!")
        return redirect(url_for("admin"))
    else:
        return redirect(url_for("not_logged_in"))

@app.route("/not-logged-in")
def not_logged_in():
    """Action to be taken if certain routes are accessed without being logged in."""
    flash("You must be logged in to view that page.")
    return redirect(url_for("root"))

##############################################################################
# User routes
@app.route("/users/register", methods=["GET", "POST"])
def register_user():
    """Form to register user:

    - if form not filled out or invalid: show form
    - if valid: add user to user table and redirect to home page
    """
    form = RegisterForm()

    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k not in ["csrf_token", "confirm"]}
        new_user = User.signup(**data)
        db.session.add(new_user)
        db.session.commit()
        do_log_in(new_user)
        flash(f"User {new_user.user_name} registered.")
        return redirect(url_for("root"))
    else:
        return render_template("register_user.html", form=form)

@app.route("/users/my-team")
def my_team():
    """Return analytical information about a user's team."""
    if check_logged_in():
        team_names = [team.name for team in Team.query.all()]
        user_id = int(session[CURR_USER_KEY])
        user = User.query.get(user_id)
        ids = user.user_players_list()
        user_players = [Player.query.get(i) for i in ids]
        return render_template("my_team.html", user_players=user_players, user=user, team_names=team_names)
    else:
        return redirect(url_for("not_logged_in"))

@app.route('/users/my-account', methods=["GET", "POST"])
def my_account():
    """Update profile for current user."""
    if not check_logged_in():
        return redirect(url_for("not_logged_in"))
    
    user = User.query.get(session[CURR_USER_KEY])
    form = UserEditDataForm(obj=user)
    
    if form.validate_on_submit():       
        if User.authenticate(user.user_name, form.password.data):
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.email = form.email.data
            user.user_name = form.user_name.data
            user.team_name = form.team_name.data
            db.session.commit()
            flash("User information updated.")
            return redirect("/users/my-account")
        flash("Wrong password, please try again.")
    
    return render_template('edit_user_data.html', form=form)

@app.route('/users/change-password', methods=["GET", "POST"])
def change_password():
    """Update password for current user."""
    if not check_logged_in():
        return redirect(url_for("not_logged_in"))
    
    user = User.query.get(session[CURR_USER_KEY])
    form = UserEditPasswordForm()
    
    if form.validate_on_submit():
        if User.authenticate(user.user_name, form.old_password.data):
            user.change_password(form.new_password.data)
            flash("Password changed successfully.")
            return redirect("/users/change-password")
        flash("Wrong password, please try again.")

    return render_template('edit_user_password.html', form=form)

###################################################################################################################################################################################
# Player routes
@app.route("/players")
def show_all_players():
    """Return a list of players."""    
    players = Player.query.all()
    
    if check_logged_in():
        user = User.query.get(session[CURR_USER_KEY])
        user_players = user.user_players_list()
        return render_template("players.html", players=players, user_players=user_players, logged_in=json.dumps(True))
    else:
        return render_template("players.html", players=players, user_players=[], logged_in=json.dumps(False))

@app.route("/players/<int:player_id>")
def show_player(player_id):
    """Return information on a player."""
    player = Player.query.get_or_404(player_id)
    signed_in = check_logged_in()    

    team_names = [team.name for team in Team.query.all()]
    
    if signed_in:
        user = User.query.get_or_404(session[CURR_USER_KEY])
        in_team = player.id in user.user_players_list()
        return render_template("player.html", player=player, club=team_names[player.team_id-1], signed_in=signed_in, user=user, in_team=in_team)
    else:
        return render_template("player.html", player=player, club=team_names[player.team_id-1], signed_in=signed_in, user=None, in_team=None)

@app.route("/players/players-add-1/<int:p_id>", methods=["POST"])
def players_add(p_id):
    """Add a player to a signed in user's team."""
    if check_logged_in():
        user_id = session[CURR_USER_KEY]
        user = User.query.get(user_id)
        user.add_player(user_id, p_id)
        
        flash("Player added!")
        return redirect(url_for("show_player", player_id=p_id))
    else:
        return redirect(url_for("not_logged_in"))

@app.route("/players/players-remove-1/<int:p_id>", methods=["POST"])
def players_remove(p_id):
    """Remove a player from signed in user's team."""
    if check_logged_in():
        user_id = session[CURR_USER_KEY]
        user = User.query.get(user_id)
        user.remove_player(user_id, p_id)
        
        flash("Player removed!")
        return redirect(url_for("show_player", player_id=p_id))
    else:
        return redirect(url_for("not_logged_in"))

@app.route("/players/players-add-2/<int:p_id>", methods=["POST"])
def players_add_2(p_id):
    """Add a player to a signed in user's team."""
    if check_logged_in():
        user_id = session[CURR_USER_KEY]
        user = User.query.get(user_id)
        user.add_player(session[CURR_USER_KEY], p_id)
        
        return jsonify("Player added.")
    else:
        return jsonify("Must be logged in to perform that action.")

@app.route("/players/players-remove-2/<int:p_id>", methods=["POST"])
def players_remove_2(p_id):
    """Remove a player from signed in user's team."""
    if check_logged_in():
        user_id = session[CURR_USER_KEY]
        user = User.query.get(user_id)
        user.remove_player(session[CURR_USER_KEY], p_id)
        
        return jsonify("Player removed.")
    else:
        return jsonify("Must be logged in to perform that action.")

@app.route("/players/players-remove-3/<int:p_id>", methods=["POST"])
def players_remove_3(p_id):
    """Remove a player from signed in user's team."""
    if check_logged_in():
        user_id = session[CURR_USER_KEY]
        user = User.query.get(user_id)
        user.remove_player(user_id, p_id)
        
        flash("Player removed!")
        return redirect(url_for("my_team"))
    else:
        return redirect(url_for("not_logged_in"))
    
@app.route("/players/players-db-search")
def player_search():
    """Player Search."""
    name = request.args.get("name","na")
    player_data = Player.search(name)
    teams = [team.name for team in Team.query.all()]
    player_list = [{"first_name":player.first_name, "last_name":player.last_name, "id":player.id, "team_id":player.team_id, "team_name":teams[player.team_id - 1]} for player in player_data]
    return jsonify(player_list=player_list)

##############################################################################
# Team routes
@app.route("/teams")
def show_all_teams():
    """Return a list of teams."""
    teams = Team.query.all()
    return render_template("teams.html", teams=teams)

@app.route("/teams/<int:team_id>")
def show_team(team_id):
    """Return information on a team."""
    team = Team.query.get_or_404(team_id)
    return render_template("team.html", team=team)

@app.route("/teams/names")
def team_names_query():
    """Team names."""
    teams = [team.name for team in Team.query.all()]
    return jsonify(teams=teams)

##############################################################################
# For anything else, reference Database DJ or Warbler
