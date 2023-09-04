import psycopg2
import plotly.graph_objects as go
from data import credentials

def sankey(player_id, postgreSQL_pool):
    ps_connection = postgreSQL_pool.getconn()
    ps_cursor = ps_connection.cursor()
    query = """
    SELECT q1.q_id AS location, q2.q_id AS type, COUNT(DISTINCT q1.event_id) AS count
    FROM (SELECT event_id, q_id FROM qualifier WHERE q_id IN (9, 24, 26, 22, 25, 23)) AS q1
    JOIN (SELECT event_id, q_id FROM qualifier WHERE q_id IN (15, 72, 20, 21)) AS q2 
    ON q1.event_id = q2.event_id
    JOIN eventfact ef ON q1.event_id = ef.event_id
    WHERE ef.player_id = %s
    GROUP BY q1.q_id, q2.q_id;
    """
    ps_cursor.execute(query,(player_id,))
    loc_type_data = ps_cursor.fetchall()

    query = """SELECT q.q_id AS type, 
           CASE WHEN q2.q_id IS NOT NULL THEN 82 ELSE ef.event_type END AS outcome, 
           COUNT(DISTINCT ef.event_id) AS count
    FROM eventfact ef
    LEFT JOIN qualifier q2 ON ef.event_id = q2.event_id AND q2.q_id = 82
    JOIN qualifier q ON ef.event_id = q.event_id
    WHERE ef.event_type IN (13, 14, 15, 16) 
    AND q.q_id IN (15, 72, 20, 21)
    AND ef.player_id = %s
    GROUP BY q.q_id, CASE WHEN q2.q_id IS NOT NULL THEN 82 ELSE ef.event_type END;"""

    ps_cursor.execute(query,(player_id,))
    type_outcome_data = ps_cursor.fetchall()

    ps_cursor.close()
    postgreSQL_pool.putconn(ps_connection)

    source = []
    target = []
    value = []

    # Updated label_map to account for new labels.
    label_map = {9: 0, 24: 1, 26: 2, 22: 3, 25: 4, 23: 5,
                 99: 6, 100: 7, 101: 8, 102: 9,
                 13: 10, 14: 11, 82: 12, 15: 13, 16: 14}

    # Populate source, target, and value from loc_type_data
    for loc, typ, count in loc_type_data:
        if typ == 15:  # header
            typ = 99
        elif typ == 72:  # left footer
            typ = 100
        elif typ == 20:  # right footer
            typ = 101
        elif typ == 21:  # other
            typ = 102

        source.append(label_map[loc])
        target.append(label_map[typ])
        value.append(count)

    # Populate source, target, and value from type_outcome_data
    for typ, outcome, count in type_outcome_data:
        if typ == 15:  # header
            typ = 99
        elif typ == 72:  # left footer
            typ = 100
        elif typ == 20:  # right footer
            typ = 101
        elif typ == 21:  # other
            typ = 102

        source.append(label_map[typ])
        target.append(label_map[outcome])
        value.append(count)
    return source, target, value

