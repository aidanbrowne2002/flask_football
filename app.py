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
    return render_template('index.html', active_page = 'home')



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
        selected_name = request.form.get('playerName')  # Get the selected player name
        session['players'][0] = selected_name
        player_id = names_to_ids.get(selected_name)  # Look up the corresponding player ID
        session['player'] = selected_name

        if player_id:
            return redirect(f"player/{player_id}")
        else:
            flash('Player not found.', 'error')
            return redirect(url_for('findPlayer'))

    return render_template('findPlayer.html', autocompleteData=fullnames, nameToID=names_to_ids, active_page = 'findplayer')




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
    return render_template('player.html', player_name = session['player'], player=player, stats = stats, active_page = 'player')

@app.route('/comparison', methods=['GET', 'POST'])
@login_required
def comparison():
    players = get.players(get_db_pool())
    names_to_ids = {}
    fullnames = []
    selected_names = session.get('players', ['',''])  # Get the previously selected names from the session, default to an empty list
    for player in players:
        player_id, first_name, last_name = player
        full_name = f"{first_name} {last_name}"
        names_to_ids[full_name] = player_id
        fullnames.append(full_name)

    if request.method == 'POST' or (session.get('players', [])[0] and session.get('players', [])[1]):
        if request.form.getlist('playerName'):
            selected_names = request.form.getlist('playerName')  # Get the selected player names as a list
        if not selected_names or selected_names[0] == '':
            selected_names[0] = session.get('players', [])[0]
        if not selected_names or selected_names[1] == '':
            selected_names[1] = session.get('players', [])[1]
        print(selected_names)
        player_ids = [names_to_ids.get(name) for name in selected_names]  # Look up the corresponding player IDs
        print(player_ids)  # For debugging purposes
        session['players'] = selected_names

        if all(player_ids):
            for p in player_ids:
                try:
                    passingmapPNG.generate_player_plot(p, 1, get_db_pool())
                    passingmapPNG.generate_player_plot(p, 0, get_db_pool())
                except:
                    pass
                try:
                    stats = get.stats(p, get_db_pool())
                    xGgraph4.genGraphs(p)
                except:
                    pass
            return render_template('comparison.html', autocompleteData=fullnames, compare=True, players=player_ids, playernames=selected_names, player1=str(player_ids[0]), player2=str(player_ids[1]), active_page='comparison')
        else:
            flash('One or more players not found.', 'error')
            print("One or more players not found.")
            return redirect(url_for('comparison'))

    return render_template('comparison.html', autocompleteData=fullnames, active_page='comparison')



@app.route('/load_stats', methods=['POST'])
def load_stats():
  playerIDs = request.json.get('playerIDs')
  # Process the playerIDs and load the stats
  print (playerIDs)

  return jsonify({'message': 'Stats loaded'})  # Return a response to the frontend


if __name__ == '__main__':
    app.run()

