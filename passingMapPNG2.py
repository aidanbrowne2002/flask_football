import psycopg2
from psycopg2 import pool
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib import image
import numpy as np
from data import credentials
from threatcalc import PitchThreat

def sigmoid_scale(values, sensitivity=3.0):
    """Sigmoidal scaling to emphasize values close to 0."""
    return 1 / (1 + np.exp(-sensitivity * values))


def generate_player_plot(player_id, success, postgreSQL_pool):
    print ("called", success)
    if success == 1:
    # Custom colormap for transition from Red to Light Grey to Green
        cmap_data = {
            'red': [(0.0, 0.8, 0.8),
                    (1.0, 0.0, 0.0)],

            'green': [(0.0, 0.8, 0.8),
                      (1.0, 0.5, 0.5)],

            'blue': [(0.0, 0.8, 0.8),
                     (1.0, 0.0, 0.0)]
        }

        cm = LinearSegmentedColormap('custom_cmap', cmap_data)
    else:
        # Custom colormap for transition from Red to Light Grey to Green
        # Custom colormap for transition from Grey to Red
        cmap_data = {
            'red': [(0.0, 0.8, 0.8),
                    (1.0, 1.0, 1.0)],

            'green': [(0.0, 0.8, 0.8),
                      (1.0, 0.0, 0.0)],

            'blue': [(0.0, 0.8, 0.8),
                     (1.0, 0.0, 0.0)]
        }
        cm = LinearSegmentedColormap('custom_cmap', cmap_data)

    # Connecting to the database


    ps_connection = postgreSQL_pool.getconn()
    ps_cursor = ps_connection.cursor()
    pt = PitchThreat()

    query = """SELECT
        e.event_id,
        e.x AS start_x,
        e.y AS start_y,
        MAX(CASE WHEN q.q_id = 56 THEN q.value ELSE NULL END) AS zone,
        MAX(CASE WHEN q.q_id = 140 THEN q.value ELSE NULL END) AS end_x,
        MAX(CASE WHEN q.q_id = 141 THEN q.value ELSE NULL END) AS end_y,
        MAX(CASE WHEN q.q_id = 212 THEN q.value ELSE NULL END) AS length,
        MAX(CASE WHEN q.q_id = 213 THEN q.value ELSE NULL END) AS angle
    FROM
        eventfact e
    JOIN
        qualifier q
    ON
        e.event_id = q.event_id
    WHERE
        e.event_type = 1
        AND e.player_id = %s
        AND e.outcome = %s
    GROUP BY
        e.event_id,
        e.x,
        e.y,
        e.outcome;"""

    ps_cursor.execute(query, (player_id, success))
    result = ps_cursor.fetchall()
    #print (result)
    ps_cursor.close()
    # release the connection back to connection pool
    postgreSQL_pool.putconn(ps_connection)

    outcome = np.array([i[1] for i in result])
    start_x = np.array([float(i[2]) for i in result])
    start_y = np.array([float(i[3]) for i in result])
    end_x = np.array([float(i[5]) for i in result])
    end_y = np.array([float(i[6]) for i in result])

    dx = end_x - start_x
    dy = end_y - start_y

    threat_values = np.array([pt.calculate_threat_difference((start_x[i], start_y[i]), (end_x[i], end_y[i]))
                              for i in range(len(start_x))])
    #print (threat_values)
    scaled_threat = sigmoid_scale(threat_values)

    # Normalize the threat values to [0, 1]
    normalized_threat = (scaled_threat - np.min(scaled_threat)) / (np.max(scaled_threat) - np.min(scaled_threat))

    # Clip the normalized threat values to the range [0, 1]
    normalized_threat = np.clip(normalized_threat, 0, 1)
    average_threat = np.mean(normalized_threat)

    fig, ax = plt.subplots(figsize=(12, 7))
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    #ax.set_facecolor('#333')
    pitch_image = image.imread('static/images/football_pitch.png')  # replace this with the actual path to your image

    # Display the image on the axis
    ax.imshow(pitch_image, extent=[0, 100, 0, 100], aspect='auto', alpha=0.7)
    cmap = cm

    ax.quiver(start_x, start_y, dx, dy, angles='xy', scale_units='xy', scale=1, alpha=0.7, color=cm(normalized_threat))


    ax.set_xlim([0, 100])
    ax.set_ylim([0, 100])

    # Set the aspect ratio to be equal
    # ax.set_aspect('equal', adjustable='box')
    fig1 = plt.gcf()
    # Show the plot
    if (success == 1):
        fig1.savefig(f'static/images/successful_passes/{player_id}.png', transparent=True)
    if (success == 0):
        fig1.savefig(f'static/images/unsuccessful_passes/{player_id}.png', transparent=True)
    if not average_threat:
        average_threat = 0
    #print (f"AVERAGE THREAT = '{average_threat}'")
    plt.close(fig1)
    return threat_values, average_threat


