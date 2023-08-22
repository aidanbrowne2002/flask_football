from data import credentials
import psycopg2
from psycopg2 import pool
import numpy as np




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