from data import credentials
import psycopg2
from psycopg2 import pool
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import image
import data.update




def players(postgreSQL_pool):
    # Use getconn() to Get Connection from connection pool
    ps_connection = postgreSQL_pool.getconn()
    # use cursor() to get a cursor as normal
    ps_cursor = ps_connection.cursor()
    #
    query = """select id, f_name, l_name from players;"""
    ps_cursor.execute(query)
    data = ps_cursor.fetchall()

    #
    # close cursor
    ps_cursor.close()
    # release the connection back to connection pool
    postgreSQL_pool.putconn(ps_connection)
    return data

def playername(playerid, postgreSQL_pool):
    # Use getconn() to Get Connection from connection pool
    ps_connection = postgreSQL_pool.getconn()
    # use cursor() to get a cursor as normal
    ps_cursor = ps_connection.cursor()
    #
    query = """select f_name, l_name from players where id = %s;"""
    ps_cursor.execute(query, (playerid,))
    data = ps_cursor.fetchall()

    #
    # close cursor
    ps_cursor.close()
    # release the connection back to connection pool
    postgreSQL_pool.putconn(ps_connection)
    data = list(data[0])
    return data

def stats(playerID, postgreSQL_pool):


    # Function to extract stats for a given outcome and event types
    def extract_stats(outcome, event_types):
        ps_connection = postgreSQL_pool.getconn()
        # use cursor() to get a cursor as normal
        ps_cursor = ps_connection.cursor()
        data = (playerID, outcome) + tuple(event_types)
        placeholders = ', '.join(['%s' for _ in event_types])
        query = f"""select count(event_id), event_type from eventfact
                    where player_id = %s and outcome = %s and event_type in ({placeholders})
                    group by event_type;"""
        ps_cursor.execute(query, data)
        results = ps_cursor.fetchall()
        ps_cursor.close()
        # release the connection back to connection pool
        postgreSQL_pool.putconn(ps_connection)
        results_array = np.array(results, dtype=object)
        counts = {event_type: 0 for event_type in event_types}
        for item in results_array:
            counts[item[1]] = item[0]
        return sum(counts.values()), counts

    # Get stats for passes
    unsuccessful_passes_count, _ = extract_stats(0, [1])
    successful_passes_count, _ = extract_stats(1, [1])
    total_passes = unsuccessful_passes_count + successful_passes_count
    stats = [['passes', total_passes, successful_passes_count, unsuccessful_passes_count]]

    # Get stats for shots
    unsuccessful_shots_count, unsuccessful_shots_breakdown = extract_stats(1, [13, 14, 15])
    successful_shots_count, _ = extract_stats(1, [16])
    total_shots = unsuccessful_shots_count + successful_shots_count
    stats.append(['shots', total_shots, successful_shots_count, unsuccessful_shots_count])


    return stats

def playerRanks(postgreSQL_pool, position):
    # Function to get the ranks of players for a given position
    ps_connection = postgreSQL_pool.getconn()
    ps_cursor = ps_connection.cursor()

    query = """select f_name, l_name from players where position = %s and avg_goals > 0
            order by avg_goals asc"""
    ps_cursor.execute(query, (position,))
    data = ps_cursor.fetchall()
    ps_cursor.close()
    # release the connection back to connection pool
    postgreSQL_pool.putconn(ps_connection)
    return data

def playerPosition(postgreSQL_pool, playerID):
    ps_connection = postgreSQL_pool.getconn()
    ps_cursor = ps_connection.cursor()
    query = """select position from players where id = %s"""
    ps_cursor.execute(query, (playerID,))
    data = ps_cursor.fetchone()  # Use fetchone() to get a single result
    ps_cursor.close()
    # release the connection back to the connection pool
    postgreSQL_pool.putconn(ps_connection)

    if data:
        return data[0]  # Return the first (and only) element of the tuple
    else:
        return None  # Return None if no data is found
def getPlayerTackles(playerID, postgreSQL_pool):
    ps_connection = postgreSQL_pool.getconn()
    ps_cursor = ps_connection.cursor()
    query = f"""select x, y, outcome from eventfact where event_type = 7 and player_id = {playerID}"""

    ps_cursor.execute(query)
    result = ps_cursor.fetchall()

    ps_cursor.close()
    # release the connection back to the connection pool
    postgreSQL_pool.putconn(ps_connection)

    tx_tackles = []
    ty_tackles = []
    fx_tackles = []
    fy_tackles = []

    for a in result:
        if a[2] == 0:
            tx_tackles.append(a[0])
            ty_tackles.append(a[1])
        else:
            fx_tackles.append(a[0])
            fy_tackles.append(a[1])



    plt.figure(figsize=(12, 7))
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Creating scatter plot for each event type with different colors
    pitch_image = image.imread('static/images/football_pitch.png')  # replace this with the actual path to your image

    # Display the image on the axis
    plt.imshow(pitch_image, extent=[0, 100, 0, 100], aspect='auto', alpha=0.7)
    size = 140
    plt.scatter(tx_tackles, ty_tackles, color='red', label='Failed Tackle', s = size)

    plt.scatter(fx_tackles, fy_tackles, color='green', label='Successful Tackle', s = size)


    #plt.legend(fontsize=25)
    plt.grid(False)
    fig1 = plt.gcf()
    fig1.savefig(f'static/images/tackles/{playerID}.png', transparent=True)
    plt.close(fig1)
    print(f"{len(fx_tackles)} successful tackles from: {len(tx_tackles) + len(fx_tackles)}")
    return {"total_tackles": (len(tx_tackles) + len(fx_tackles)), "successful_tackles": len(fx_tackles)}

def shotPos(postgreSQL_pool, playerID):
    ps_connection = postgreSQL_pool.getconn()
    ps_cursor = ps_connection.cursor()
    query = f"""select event_id, event_type, player_id, x, y from eventfact
                where event_type IN (13,14,15,16) and player_id = {playerID}"""

    ps_cursor.execute(query)
    result = ps_cursor.fetchall()

    ps_cursor.close()
    # release the connection back to the connection pool
    postgreSQL_pool.putconn(ps_connection)

    missed_shots_x = []
    missed_shots_y = []

    post_shots_x = []
    post_shots_y = []

    saved_shots_x = []
    saved_shots_y = []

    scored_shots_x = []
    scored_shots_y = []

    for row in result:
        if row[1] == 13:
            missed_shots_x.append(row[3])
            missed_shots_y.append(row[4])
        elif row[1] == 14:
            post_shots_x.append(row[3])
            post_shots_y.append(row[4])
        elif row[1] == 15:
            saved_shots_x.append(row[3])
            saved_shots_y.append(row[4])
        elif row[1] == 16:
            scored_shots_x.append(row[3])
            scored_shots_y.append(row[4])

    try:
        onTarget = (len(scored_shots_x) + len(saved_shots_x))/((len(missed_shots_x) + len(post_shots_x) + len(saved_shots_x) + len(scored_shots_x)))
    except:
        onTarget = 0
    plt.figure(figsize=(12, 7))
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Creating scatter plot for each event type with different colors
    pitch_image = image.imread('static/images/football_pitch.png')  # replace this with the actual path to your image

    # Display the image on the axis
    plt.imshow(pitch_image, extent=[0, 100, 0, 100], aspect='auto', alpha=0.7)
    size = 100
    # Creating scatter plot for each event type with different colors
    plt.scatter(missed_shots_x, missed_shots_y, color='red', label='Missed', s=size)
    plt.scatter(post_shots_x, post_shots_y, color='blue', label='Woodwork', s=size)
    plt.scatter(saved_shots_x, saved_shots_y, color='yellow', label='Saved', s=size)
    plt.scatter(scored_shots_x, scored_shots_y, color='green', label='Scored', s=size)



    #plt.legend(fontsize=25, loc='upper left')
    plt.grid(False)
    fig1 = plt.gcf()
    fig1.savefig(f'static/images/shotpos/{playerID}.png', transparent=True)
    plt.close(fig1)
    return onTarget, len(scored_shots_x)

def type(positon):
    if positon in ('Striker', 'Second Striker'):
        type = "Striker"
    elif positon in ('Defensive Midfielder', 'Central Midfielder', 'Attacking Midfielder'):
        type = "Midfielder"
    elif positon in ('Wing Back', 'Winger'):
        type = "Winger"
    elif positon in ('Full Back', 'Central Defender', 'Full Back'):
        type = "Defender"
    else:
        type = "Goalkeeper"
    return type

def getPlayerInterceptions(playerID, postgreSQL_pool):
    ps_connection = postgreSQL_pool.getconn()
    ps_cursor = ps_connection.cursor()
    query = f"""select x, y from eventfact where event_type = 8 and player_id = {playerID}"""

    ps_cursor.execute(query)
    result = ps_cursor.fetchall()

    ps_cursor.close()
    # release the connection back to the connection pool
    postgreSQL_pool.putconn(ps_connection)

    interceptionsX = []
    interceptionsY = []

    for a in result:
        interceptionsX.append(a[0])
        interceptionsY.append(a[1])



    plt.figure(figsize=(12, 7))
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Creating scatter plot for each event type with different colors
    pitch_image = image.imread('static/images/football_pitch.png')  # replace this with the actual path to your image

    # Display the image on the axis
    plt.imshow(pitch_image, extent=[0, 100, 0, 100], aspect='auto', alpha=0.7)
    size = 140
    plt.scatter(interceptionsX, interceptionsY, color='green', label='Interception', s = size)



    plt.grid(False)
    fig1 = plt.gcf()
    fig1.savefig(f'static/images/interceptions/{playerID}.png', transparent=True)
    plt.close(fig1)
    return len(interceptionsX)

def getPlayeraerial(playerID, postgreSQL_pool):
    ps_connection = postgreSQL_pool.getconn()
    ps_cursor = ps_connection.cursor()
    query = f"""select x, y, outcome from eventfact where event_type = 44 and player_id = {playerID}"""

    ps_cursor.execute(query)
    result = ps_cursor.fetchall()

    ps_cursor.close()
    # release the connection back to the connection pool
    postgreSQL_pool.putconn(ps_connection)

    tx_aerial = []
    ty_aerial = []
    fx_aerial = []
    fy_aerial = []

    for a in result:
        if a[2] == 0:
            tx_aerial.append(a[0])
            ty_aerial.append(a[1])
        else:
            fx_aerial.append(a[0])
            fy_aerial.append(a[1])



    plt.figure(figsize=(12, 7))
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Creating scatter plot for each event type with different colors
    pitch_image = image.imread('static/images/football_pitch.png')  # replace this with the actual path to your image

    # Display the image on the axis
    plt.imshow(pitch_image, extent=[0, 100, 0, 100], aspect='auto', alpha=0.7)
    size = 140
    plt.scatter(tx_aerial, ty_aerial, color='red', label='Failed aerial', s = size)

    plt.scatter(fx_aerial, fy_aerial, color='green', label='Successful aerial', s = size)


    #plt.legend(fontsize=25)
    plt.grid(False)
    fig1 = plt.gcf()
    fig1.savefig(f'static/images/aerials/{playerID}.png', transparent=True)
    plt.close(fig1)
    print(f"{len(fx_aerial)} successful aerials from: {len(tx_aerial) + len(fx_aerial)}")
    return {"total_aerials": (len(tx_aerial) + len(fx_aerial)), "successful_aerials": len(fx_aerial)}

def getPlayerblocks(playerID, postgreSQL_pool):
    ps_connection = postgreSQL_pool.getconn()
    ps_cursor = ps_connection.cursor()
    query = f"""select x, y from eventfact where event_type = 10 and player_id = {playerID}"""

    ps_cursor.execute(query)
    result = ps_cursor.fetchall()

    ps_cursor.close()
    # release the connection back to the connection pool
    postgreSQL_pool.putconn(ps_connection)

    blocksx = []
    blocksy = []

    for a in result:
        blocksx.append(a[0])
        blocksy.append(a[1])



    plt.figure(figsize=(12, 7))
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Creating scatter plot for each event type with different colors
    pitch_image = image.imread('static/images/football_pitch.png')  # replace this with the actual path to your image

    # Display the image on the axis
    plt.imshow(pitch_image, extent=[0, 100, 0, 100], aspect='auto', alpha=0.7)
    size = 140
    plt.scatter(blocksx, blocksy, color='green', label='blocks', s = size)



    plt.grid(False)
    fig1 = plt.gcf()
    fig1.savefig(f'static/images/blocks/{playerID}.png', transparent=True)
    plt.close(fig1)
    return len(blocksx)

def totalTimePlayed(playerID, postgreSQL_pool):
    ps_connection = postgreSQL_pool.getconn()
    ps_cursor = ps_connection.cursor()
    query = f"""select sum(offtime-ontime+half_added) from players_in_game where game_player_id = {playerID};"""

    ps_cursor.execute(query)
    result = ps_cursor.fetchone()

    ps_cursor.close()
    # release the connection back to the connection pool
    postgreSQL_pool.putconn(ps_connection)

    if result and result[0] is not None:
        float_value = float(result[0])
        print(float_value)
    else:
        print("No result or result is None")
        float_value = 0
    return float_value
def playerxG(playerID, postgreSQL_pool):
    data.update.player_xg_goals(playerID, postgreSQL_pool)
    ps_connection = postgreSQL_pool.getconn()
    ps_cursor = ps_connection.cursor()
    query = f"""select xg from players where id = {playerID};"""
    ps_cursor.execute(query)
    result = ps_cursor.fetchone()
    ps_cursor.close()
    # release the connection back to the connection pool
    if result and result[0] is not None:
        float_value = float(result[0])
        #print(float_value)
    else:
        print("No result or result is None")
    print (f"XG VALUES --- xg: {float_value}, total time played: {totalTimePlayed(playerID, postgreSQL_pool)}")
    try:
        xG = totalTimePlayed(playerID, postgreSQL_pool)/float_value
    except ZeroDivisionError:
        xG = 0
    #xG = totalTimePlayed(playerID, postgreSQL_pool)/float_value
    postgreSQL_pool.putconn(ps_connection)
    return xG

def playerNationality(playerID, postgreSQL_pool):
    ps_connection = postgreSQL_pool.getconn()
    ps_cursor = ps_connection.cursor()
    query = f"""select nationality from players where id = {playerID};"""
    ps_cursor.execute(query)
    result = ps_cursor.fetchone()
    ps_cursor.close()
    # release the connection back to the connection pool
    postgreSQL_pool.putconn(ps_connection)
    if result is not None:
        result = result[0]
        print(result)
    else:
        print("No result or result is None")
    return result

def flag(nationality):
    nation_to_flag = {
        "Burkina Faso": "bf.png",
        "Italy": "it.png",
        "Venezuela": "ve.png",
        "Uruguay": "uy.png",
        "Cameroon": "cm.png",
        "Czech Republic": "cz.png",
        "Sweden": "se.png",
        "USA": "us.png",
        "Germany": "de.png",
        "Macedonia": "mk.png",
        "Canada": "ca.png",
        "Portugal": "pt.png",
        "Colombia": "co.png",
        "Wales": "gb-wls.png",
        "Ukraine": "ua.png",
        "Argentina": "ar.png",
        "England": "gb-eng.png",
        "Egypt": "eg.png",
        "Greece": "gr.png",
        "Republic of Ireland": "ie.png",
        "Northern Ireland": "gb-nir.png",
        "Algeria": "dz.png",
        "Chile": "cl.png",
        "France": "fr.png",
        "Réunion": "re.png",
        "Estonia": "ee.png",
        "Slovakia": "sk.png",
        "South Africa": "za.png",
        "Kenya": "ke.png",
        "Senegal": "sn.png",
        "Ghana": "gh.png",
        "Iceland": "is.png",
        "Yugoslavia": "no data",  # No flag provided
        "Kosovo": "xk.png",
        "Japan": "jp.png",
        "Sierra Leone": "sl.png",
        "Denmark": "dk.png",
        "Bosnia and Herzegovina": "ba.png",
        "Jamaica": "jm.png",
        "no data": "no data",  # No flag provided
        "Korea Republic": "kp.png",
        "Nigeria": "ng.png",
        "Switzerland": "ch.png",
        "Ecuador": "ec.png",
        "Congo DR": "cd.png",
        "Côte d'Ivoire": "ci.png",
        "Norway": "no.png",
        "Armenia": "am.png",
        "Scotland": "gb-sct.png",
        "Netherlands": "nl.png",
        "Romania": "ro.png",
        "Brazil": "br.png",
        "Austria": "at.png",
        "Australia": "au.png",
        "Serbia": "rs.png",
        "Ethiopia": "et.png",
        "Lithuania": "lt.png",
        "Spain": "es.png",
        "Swaziland": "sz.png",
        "Morocco": "ma.png",
        "Belgium": "be.png",
        "Burundi": "bi.png",
        "Poland": "pl.png",
        "Costa Rica": "cr.png",
    }
    return nation_to_flag[nationality]
