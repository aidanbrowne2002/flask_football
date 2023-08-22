import xGgraph4
from flask import Flask, render_template, request, session, redirect, url_for, flash
from data import get, credentials
import passingmapPNG
import psycopg2
from xGgraph4 import genGraphs

app = Flask(__name__)
app.secret_key = "jfoiajfoijdz"

keepalive_kwargs = {
  "keepalives": 1,
  "keepalives_idle": 60,
  "keepalives_interval": 10,
  "keepalives_count": 5
}

postgreSQL_pool = psycopg2.pool.SimpleConnectionPool(1,20,
                        database=credentials.database,
                        host=credentials.host,
                        user=credentials.user,
                        password=credentials.password,
                        port=credentials.port)

@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')


@app.route('/findplayer', methods=['GET', 'POST'])
def findPlayer():
    players = get.players(postgreSQL_pool)
    names_to_ids = {}
    fullnames = []
    for player in players:
        player_id, first_name, last_name = player
        full_name = f"{first_name} {last_name}"
        names_to_ids[full_name] = player_id
        fullnames.append(full_name)

    if request.method == 'POST':
        player_id = request.form.get('player')  # Now we're getting an ID, not a name
        name = get.playername(player_id, postgreSQL_pool)
        session['player'] = f"{name[0]} {name[1]}"

        # Check if the received player_id exists in our data
        if player_id in [str(id) for id in names_to_ids.values()]:
            return redirect(f"player/{player_id}")
        else:
            flash('Player not found.', 'error')
            return redirect(url_for('findPlayer'))

    return render_template('findPlayer.html', autocompleteData=fullnames, nameToID=names_to_ids)


@app.route('/player/<player>')
def player(player):
    passingmapPNG.generate_player_plot(player,1, postgreSQL_pool)
    passingmapPNG.generate_player_plot(player, 0, postgreSQL_pool)
    stats = get.stats(player,postgreSQL_pool)
    xGgraph4.genGraphs(player)
    return render_template('player.html', player_name = session['player'], player=player, stats = stats)


if __name__ == '__main__':
    app.run()
