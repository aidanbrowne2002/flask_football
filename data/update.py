from data import credentials
import psycopg2
from psycopg2 import pool
import numpy as np
from collections import defaultdict
from werkzeug.security import generate_password_hash


def player_xg_goals(player_id, postgreSQL_pool):
    xG_matrix = xgMatrix(postgreSQL_pool)
    ps_connection = postgreSQL_pool.getconn()
    ps_cursor = ps_connection.cursor()
    query = f"""
            SELECT SUM((offtime - ontime) + half_added)
            FROM players_in_game
            WHERE game_player_id = {player_id}
        """
    ps_cursor.execute(query)
    total_minutes = ps_cursor.fetchone()[0]
    if total_minutes is None:
        total_minutes = 0

    query = f"""
        SELECT event_id, event_type, player_id, game_id, x, y
        FROM eventfact
        WHERE event_type IN (13,14,15,16) AND player_id = {player_id} and x > 50;
    """
    ps_cursor.execute(query)
    data = ps_cursor.fetchall()

    ps_cursor.close()
    # release the connection back to connection pool
    postgreSQL_pool.putconn(ps_connection)

    stats = defaultdict(float)
    stats["games"] = set()  # Initializing stats for the player

    for event in data:
        event_id, event_type, _, game_id, x_pos, y_pos = event

        # Find the xG value for this shot position from the matrix
        x_bin = int(x_pos / 5)
        y_bin = int(y_pos / 5)

        # Check if the bins are within matrix boundaries
        if 0 <= x_bin < xG_matrix.shape[0] and 0 <= y_bin < xG_matrix.shape[1]:
            position_xG = xG_matrix[x_bin, y_bin]
        else:
            position_xG = 0  # Default to 0 if out of bounds. Adjust as necessary.

        stats["xG"] += position_xG

        if event_type == 16:  # Check if the event is a goal
            stats["goals"] += 1

        # Update games set
        stats["games"].add(game_id)

    avg_xG_per_minute = float(total_minutes) / stats["xG"] if total_minutes > 0 and stats["xG"] > 0 else 0
    avg_goals_per_minute = float(total_minutes) / stats["goals"] if total_minutes > 0 and stats["goals"] > 0 else 0

    print(f"total minutes played, player: {total_minutes}")
    print({"avg_xG_per_minute": avg_xG_per_minute, "avg_goals_per_minute": avg_goals_per_minute, "xg": stats["xG"]})

    ps_connection = postgreSQL_pool.getconn()
    ps_cursor = ps_connection.cursor()

    query = """update players set xg = %s, avg_goals = %s where players.id = %s;"""
    ps_cursor.execute(query, (avg_xG_per_minute, avg_goals_per_minute, player_id))
    ps_connection.commit()
    ps_cursor.close()
    # release the connection back to connection pool
    postgreSQL_pool.putconn(ps_connection)


    return {"avg_xG_per_minute": avg_xG_per_minute, "avg_goals_per_minute": avg_goals_per_minute, "xg": stats["xG"], "goals": stats["goals"]}








def xgMatrix(postgreSQL_pool):
    ps_connection = postgreSQL_pool.getconn()
    ps_cursor = ps_connection.cursor()
    query = """select event_id, event_type, player_id, x, y, position from eventfact
join players p on p.id = eventfact.player_id
where event_type IN (13,14,15,16) and x > 50"""
    ps_cursor.execute(query)
    result = ps_cursor.fetchall()
    ps_cursor.close()
    # release the connection back to connection pool
    postgreSQL_pool.putconn(ps_connection)
    # Convert result into an array of coordinates and event types
    shots = [(float(event[3]), float(event[4]), event[1]) for event in result]

    # Create a 2D matrix for shots and goals (for simplicity, we use 5x5 bins in percentage terms)
    bins_x = 20  # Equivalent to dividing 100 by 5
    bins_y = 20  # Equivalent to dividing 100 by 5
    shot_matrix = np.zeros((bins_x, bins_y))
    goal_matrix = np.zeros((bins_x, bins_y))

    # Populate the matrices
    for shot in shots:
        x_bin = int(shot[0] / 5)
        y_bin = int(shot[1] / 5)
        shot_matrix[x_bin, y_bin] += 1
        # Assuming event type 16 is a scored goal
        if shot[2] == 16:
            goal_matrix[x_bin, y_bin] += 1

    # Calculate xG for each bin
    xG_matrix = np.divide(goal_matrix, shot_matrix, out=np.zeros_like(goal_matrix), where=shot_matrix != 0)
    return xG_matrix

def addUser(postgreSQL_pool, username, password):
    try:
        # Connect to your database
        ps_connection = postgreSQL_pool.getconn()
        ps_cursor = ps_connection.cursor()

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        # Insert the user into the database
        ps_cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        ps_connection.commit()
    finally:
        # Close the connection
        ps_cursor.close()
        # release the connection back to connection pool
        postgreSQL_pool.putconn(ps_connection)

def removeUser(postgreSQL_pool, username):
    try:
        # Connect to your database
        ps_connection = postgreSQL_pool.getconn()
        ps_cursor = ps_connection.cursor()
        query = "DELETE FROM users WHERE username = %s"
        ps_cursor.execute(query, (username,))
        ps_connection.commit()
    finally:
        # Close the connection
        ps_cursor.close()
        # release the connection back to connection pool
        postgreSQL_pool.putconn(ps_connection)

def multipliers(postgreSQL_pool, multipliers):
    try:
        # Connect to your database
        ps_connection = postgreSQL_pool.getconn()
        ps_cursor = ps_connection.cursor()
        query = "UPDATE tigerx SET multiplier = %s WHERE name = %s"
        for multiplier in multipliers:
            ps_cursor.execute(query, (multiplier[0], multiplier[1]))
        ps_connection.commit()
    finally:
        # Close the connection
        ps_cursor.close()
        # release the connection back to connection pool
        postgreSQL_pool.putconn(ps_connection)
