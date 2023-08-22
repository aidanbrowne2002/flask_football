import xGgraph4
from flask import Flask, render_template, request, session, redirect, url_for, flash
from data import get, credentials
import passingmapPNG
import psycopg2
from xGgraph4 import genGraphs
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "jfoiajfoijdz"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


global postgreSQL_pool
postgreSQL_pool = None

def get_db_pool():
    global postgreSQL_pool
    if postgreSQL_pool is None:
        keepalive_kwargs = {
            "keepalives": 1,
            "keepalives_idle": 60,
            "keepalives_interval": 10,
            "keepalives_count": 5
        }
        postgreSQL_pool = psycopg2.pool.SimpleConnectionPool(1, 5,
                            database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port,
                            **keepalive_kwargs)
    return postgreSQL_pool

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

    @staticmethod
    def get(user_id):
        get_db_pool()
        conn = postgreSQL_pool.getconn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            if user_data:
                return User(id=user_data[0], username=user_data[1])
        finally:
            cursor.close()
            postgreSQL_pool.putconn(conn)
        return None

    @staticmethod
    def authenticate(username, password):
        get_db_pool()
        conn = postgreSQL_pool.getconn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
            user_data = cursor.fetchone()
            if user_data and check_password_hash(user_data[2], password):
                return User(id=user_data[0], username=user_data[1])
        finally:
            cursor.close()
            postgreSQL_pool.putconn(conn)
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.authenticate(username, password)
        if user:
            login_user(user)
            return redirect('/') # assuming you have a dashboard route
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect('/')  # redirect to main page or you can redirect to 'login'





@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')



@app.route('/findplayer', methods=['GET', 'POST'])
@login_required
def findPlayer():
    players = get.players(get_db_pool())
    names_to_ids = {}
    fullnames = []
    for player in players:
        player_id, first_name, last_name = player
        full_name = f"{first_name} {last_name}"
        names_to_ids[full_name] = player_id
        fullnames.append(full_name)

    if request.method == 'POST':
        player_id = request.form.get('player')  # Now we're getting an ID, not a name
        name = get.playername(player_id, get_db_pool())
        session['player'] = f"{name[0]} {name[1]}"

        # Check if the received player_id exists in our data
        if player_id in [str(id) for id in names_to_ids.values()]:
            return redirect(f"player/{player_id}")
        else:
            flash('Player not found.', 'error')
            return redirect(url_for('findPlayer'))

    return render_template('findPlayer.html', autocompleteData=fullnames, nameToID=names_to_ids)


@app.route('/player/<player>')
@login_required
def player(player):
    try:
        passingmapPNG.generate_player_plot(player,1, get_db_pool())
        passingmapPNG.generate_player_plot(player, 0, get_db_pool())
    except:
        pass
    try:
        stats = get.stats(player,get_db_pool())
        xGgraph4.genGraphs(player)
    except:
        pass
    return render_template('player.html', player_name = session['player'], player=player, stats = stats)


if __name__ == '__main__':
    app.run()
