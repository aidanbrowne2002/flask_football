import data.sankey
import xGgraph4
from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from data import get, credentials, sankey, update
import passingmapPNG
import passingMapPNG2
import psycopg2
from xGgraph4 import genGraphs
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import colourkey
import importlib
import tigerXRating
import keyPassPNG
import numpy as np




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
        postgreSQL_pool = psycopg2.pool.SimpleConnectionPool(1, 10,
                            database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port,
                            **keepalive_kwargs)
    return postgreSQL_pool


#initialise the averages to save compute time for end user
print("Initialising averages")
avgGoalsTotals, avgxGTotals = xGgraph4.initialisexgraph4(get_db_pool())
print("Initialising averages complete")
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

@app.context_processor
def inject_user():
    if current_user.is_authenticated:
        username = current_user.username
    else:
        username = None
    return dict(user_current=username)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.authenticate(username, password)
        if user:
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = '/'  # Redirect to the homepage if 'next' is invalid
            return redirect(next_page)
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html',)

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
    if 'players' not in session:
        session['players'] = []
    for player in players:
        player_id, first_name, last_name = player
        full_name = f"{first_name} {last_name}"
        names_to_ids[full_name] = player_id
        fullnames.append(full_name)

    if request.method == 'POST':
        selected_name = request.form.get('playerName')  # Get the selected player name

        player_id = names_to_ids.get(selected_name)  # Look up the corresponding player ID
        session['player'] = selected_name
        if session['selected_names']:
            session['selected_names'][0] = selected_name
        else:
            session['selected_names'].append(selected_name)

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

@app.route('/initialise_comparison')
@login_required
def initialise_comparison():
    return render_template('initialisecomparison.html', active_page = 'comparison')
    return redirect(url_for('comparison'))

@app.route('/comparison', methods=['GET', 'POST'])
@login_required
def comparison():

    players = get.players(get_db_pool())
    names_to_ids = {}
    fullnames = []

    for player in players:
        player_id, first_name, last_name = player
        full_name = f"{first_name} {last_name}"
        names_to_ids[full_name] = player_id
        fullnames.append(full_name)

    if request.method == 'POST':
        selected_names = request.form.getlist('playerName')
        session['selected_names'] = selected_names
    else:
        selected_names = session.get('selected_names', ['', ''])

    if selected_names[0] == '':
        if session.get('players'):
            selected_names[0] = session['players'][0]
        else:
            striker_1 = get.playerRanks(get_db_pool(), 'Striker')[0]
            selected_names[0] = f"{striker_1[0]} {striker_1[1]}"

    if selected_names[1] == '':
        if session.get('players'):
            selected_names[1] = session['players'][1]
        else:
            striker_2 = get.playerRanks(get_db_pool(), 'Striker')[1]
            selected_names[1] = f"{striker_2[0]} {striker_2[1]}"

    session['selected_names'] = selected_names
    print (session.get('selected_names'))

    player_ids = [names_to_ids.get(name) for name in session['selected_names']]
    print(player_ids)  # For debugging purposes
    session['players'] = session['selected_names']
    stats = []
    spasses = []
    upasses = []
    ranks = []
    sthreatvals = []
    uthreatvals = []
    if all(player_ids):
        for p in player_ids:
            try:
                threatval, passes = passingMapPNG2.generate_player_plot(p, 1, get_db_pool())
                spasses.append(passes)
                sthreatvals.append(threatval)
            except:
                print ("failed passes s")
                spasses.append(0)
                sthreatvals.append(0)
            try:
                threatval, passes = passingMapPNG2.generate_player_plot(p, 0, get_db_pool())
                upasses.append(passes)
                uthreatvals.append(threatval)
            except:
                print("failed passes u")
                upasses.append(0)
                uthreatvals.append(0)
            try:
                grank = ''
                xrank = ''
                stats.append(get.stats(p, get_db_pool()))
                grank, xrank = xGgraph4.genGraphs(p, get_db_pool(), avgGoalsTotals, avgxGTotals)
            except Exception as error:
                print ("failed", error)
                pass
            if grank is None or grank == '':
                grank = 'N/A'
            if xrank is None or xrank == '':
                xrank = 'N/A'
            ranks.append([grank, xrank])
        p1stats = stats[0]
        p2stats = stats[1]
        #print(spasses)
        colourkey.save_color_key_image(sthreatvals[0],sthreatvals[1],str(player_ids[0]),str(player_ids[1]),1)
        colourkey.save_color_key_image(uthreatvals[0],uthreatvals[1],str(player_ids[0]),str(player_ids[1]),0)
        source1, target1, value1 = data.sankey.sankey(player_ids[0], get_db_pool())
        source2, target2, value2 = data.sankey.sankey(player_ids[1], get_db_pool())

        player1position = get.playerPosition(get_db_pool(), player_ids[0])
        player2position = get.playerPosition(get_db_pool(), player_ids[1])
        p1type = get.type(str(player1position))
        p2type = get.type(str(player2position))

        p1tackles = get.getPlayerTackles(player_ids[0], get_db_pool())
        p2tackles = get.getPlayerTackles(player_ids[1], get_db_pool())
        p1onTarget, p1scored = get.shotPos(get_db_pool(), player_ids[0])
        p2onTarget, p2scored = get.shotPos(get_db_pool(), player_ids[1])
        p1interceptions = get.getPlayerInterceptions(player_ids[0], get_db_pool())
        p2interceptions = get.getPlayerInterceptions(player_ids[1], get_db_pool())
        p1aerials = get.getPlayeraerial(player_ids[0], get_db_pool())
        p2aerials = get.getPlayeraerial(player_ids[1], get_db_pool())
        p1blocks = get.getPlayerblocks(player_ids[0], get_db_pool())
        p2blocks = get.getPlayerblocks(player_ids[1], get_db_pool())
        p1nationality = get.playerNationality(player_ids[0], get_db_pool())
        p2nationality = get.playerNationality(player_ids[1], get_db_pool())
        p1flag = get.flag(p1nationality)
        p2flag = get.flag(p2nationality)
        p1rating, p1info = tigerXRating.ratePlayer(p1scored, get.playerxG(player_ids[0], get_db_pool()), p1interceptions, p1aerials["successful_aerials"], p1onTarget * (p1stats[1][1]), p1stats[0][2], np.mean(sthreatvals[0]), p1stats[0][3], np.mean(uthreatvals[0]), float(p1tackles["successful_tackles"]), float(p1tackles["total_tackles"]-p1tackles["successful_tackles"]), round(p1stats[1][1]*(1-p1onTarget),2), float(p1aerials["total_aerials"]-p1aerials["successful_aerials"]),get.totalTimePlayed(player_ids[0], get_db_pool()))
        p2rating, p2info = tigerXRating.ratePlayer(p2scored, get.playerxG(player_ids[1], get_db_pool()), p2interceptions, p2aerials["successful_aerials"], p2onTarget * (p2stats[1][1]), p2stats[0][2], np.mean(sthreatvals[1]), p2stats[0][3], np.mean(uthreatvals[1]), float(p2tackles["successful_tackles"]), float(p1tackles["total_tackles"]-p1tackles["successful_tackles"]), round(p2stats[1][1]*(1-p2onTarget),2), float(p2aerials["total_aerials"]-p2aerials["successful_aerials"]),get.totalTimePlayed(player_ids[1], get_db_pool()))
        p1assists, p1keypasses = get.assists(player_ids[0], get_db_pool())
        p2assists, p2keypasses = get.assists(player_ids[1], get_db_pool())
        p1assistthreats, p1assiststhreatsavg = keyPassPNG.generate_player_plot(player_ids[0], 1, get_db_pool())
        p2assistthreats, p2assiststhreatsavg = keyPassPNG.generate_player_plot(player_ids[1], 1, get_db_pool())
        p1keypassthreats, p1keypassthreatsavg = keyPassPNG.generate_player_plot(player_ids[0], 0, get_db_pool())
        p2keypassthreats, p2keypassthreatsavg = keyPassPNG.generate_player_plot(player_ids[1], 0, get_db_pool())
        colourkey.save_color_key_image(p1assistthreats, p2assistthreats, str(player_ids[0]), str(player_ids[1]), 2)
        colourkey.save_color_key_image(p1keypassthreats, p2keypassthreats, str(player_ids[0]), str(player_ids[1]), 3)

    return render_template('comparison2.html', autocompleteData=fullnames, compare=True, players=player_ids,
                           playernames=session['selected_names'], player1=str(player_ids[0]),
                           player2=str(player_ids[1]), active_page='comparison', p2stats = p2stats, p1stats = p1stats,
                           source1 = source1, target1 = target1, value1 = value1, source2 = source2, target2 = target2,
                           value2 = value2, ranks=ranks,
                           player1position = player1position, player2position = player2position, p1tackles = p1tackles,
                           p2tackles = p2tackles, p1type = p1type, p2type = p2type, p1onTarget = p1onTarget,
                           p2onTarget = p2onTarget, p1interceptions = p1interceptions, p2interceptions = p2interceptions,
                           p1aerials = p1aerials, p2aerials = p2aerials, p1blocks = p1blocks, p2blocks = p2blocks,
                           p1rating = p1rating, p2rating = p2rating, p1info = p1info, p2info = p2info, p1flag = p1flag,
                           p2flag = p2flag, p1assists = p1assists, p2assists = p2assists, p1keypasses = p1keypasses,
                           p2keypasses = p2keypasses)



@app.route('/admin_page', methods=['DELETE', 'POST', 'GET'])
@login_required
def admin_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin':
            flash('Cannot change admin user', 'danger')
            return redirect('/admin_page')
        else:
            update.addUser(get_db_pool(), username, password)
            return redirect('/admin_page')
    if request.method == 'DELETE':
        data = request.get_json()
        username_to_remove = data.get('username')

        if username_to_remove == 'admin':
            flash('Cannot change admin user', 'danger')
            return redirect('/admin_page')

        if current_user.username == 'admin':
            # Call your remove user function here
            update.removeUser(get_db_pool(), username_to_remove)

            # Send a JSON response indicating success
            return jsonify({'message': 'User removed successfully'})
        else:
            # Send a JSON response indicating lack of permission
            return jsonify({'error': 'You do not have permission to remove users'})



    if current_user.username == 'admin':
        # Only allow access to users with the username 'admin'
        users = get.users(get_db_pool())
        return render_template('admin_page.html', users=users, active_page='admin')
    else:
        flash('You do not have permission to access this page.', 'danger')
        return redirect('/')

@app.route('/load_stats', methods=['POST'])
def load_stats():
  playerIDs = request.json.get('playerIDs')
  # Process the playerIDs and load the stats
  print (playerIDs)

  return jsonify({'message': 'Stats loaded'})  # Return a response to the frontend


'''@app.errorhandler(Exception)
def exception_handler(error):
    return "!!!!"  + repr(error)'''

if __name__ == '__main__':
    app.run()

