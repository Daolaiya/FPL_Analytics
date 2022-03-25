"""Models for my FPL_Analytics app."""
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import requests

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)

class Player(db.Model):
    """Player Profile"""
    __tablename__="players"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    photo_code = db.Column(db.Text, nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id', ondelete='CASCADE'))
    now_cost = db.Column(db.Integer, nullable=False)
    ppg = db.Column(db.Float)
    total_points = db.Column(db.Integer)

    team = db.relationship("Team", backref="players")

    def __repr__(self):
        """Show info about player."""
        p = self
        return f"<Player: id:{p.id} first name:{p.first_name} last name:{p.last_name} team id: {p.team_id}>"
    
    @classmethod
    def search(cls, name):
        player_list = Player.query.filter(db.or_(Player.first_name.ilike('%' + name + '%'), Player.last_name.ilike('%' + name + '%'))).all()
        return player_list

class Team(db.Model):
    """Premier League Team."""
    __tablename__="teams"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False,  unique=True)
    photo_code = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        """Show info about Team."""
        p = self
        return f"<Team: id:{p.id} name:{p.name}>"

class User(db.Model):
    """A user"""
    __tablename__="users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    user_name = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    team_name = db.Column(db.Text, nullable=False)
    user_players = db.Column(db.Text, default='')

    def __repr__(self):
        """Show info about player."""
        p = self
        return f"<User: id:{p.id} first name:{p.first_name} last name:{p.last_name} team name: {p.team_name}>"
    
    def user_players_list(self):
        """Return integer list of user players."""
        if self.user_players == '':
            return []
        
        text_array = self.user_players.split(",")
        user_players_ids = [int(i) for i in text_array]
        return user_players_ids

    @classmethod
    def signup(cls, first_name, last_name, email, user_name, password, team_name):
        """Register a user."""
        user = User(
            first_name = first_name,
            last_name = last_name,
            email = email,
            user_name = user_name,
            password = bcrypt.generate_password_hash(password).decode('UTF-8'),
            team_name = team_name
        )

        db.session.add(user)
        db.session.commit()
        
        return user
    
    @classmethod
    def authenticate(cls, user_name, password):
        """
        Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """
        user = cls.query.filter_by(user_name=user_name).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            
            if is_auth:
                return user

        return False
    
    def remove_player(self, user_id, player_id):
        """Remove a player from a user's personal team."""
        user = self
        players = user.user_players.split(",")
        players.remove(str(player_id))
        user.user_players = ",".join(players)

        db.session.commit()
    
    def add_player(self, user_id, player_id):
        """Add a player to a user's personal team."""
        user = self
        
        player_ids = user.user_players_list()
        
        if not (player_id in player_ids):
            if user.user_players == "":
                user.user_players += str(player_id)
            else:
                user.user_players += "," + str(player_id)
            db.session.commit()

    def change_password(self, password):
        """Change a user's password."""
        user = self

        user.password = bcrypt.generate_password_hash(password).decode('UTF-8')

        db.session.commit()
        return user
