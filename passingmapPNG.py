import psycopg2
import matplotlib.pyplot as plt
import numpy as np
from data import credentials
from threatcalc import PitchThreat
import matplotlib
from matplotlib import image
from matplotlib.colors import LinearSegmentedColormap




# Custom colormap for transition from Red to Light Grey to Green
cmap_data = {
    'red':   [(0.0,  1.0, 1.0),
              (0.5,  0.8, 0.8),  # Light grey has an RGB value of (0.8, 0.8, 0.8)
              (1.0,  0.0, 0.0)],

    'green': [(0.0,  0.0, 0.0),
              (0.5,  0.8, 0.8),  # Light grey
              (1.0,  0.5, 0.5)],

    'blue':  [(0.0,  0.0, 0.0),
              (0.5,  0.8, 0.8),  # Light grey
              (1.0,  0.0, 0.0)]
}

cm = LinearSegmentedColormap('custom_cmap', cmap_data)

def sigmoid_scale(values, sensitivity=3.0):
    """Sigmoidal scaling to emphasize values close to 0."""
    return 1 / (1 + np.exp(-sensitivity * values))

def generate_player_plot(player_id, success, postgreSQL_pool):
    ps_connection = postgreSQL_pool.getconn()
    ps_cursor = ps_connection.cursor()
    pt = PitchThreat()

    query = """SELECT
        e.event_id,
        e.outcome,
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
    scaled_threat = sigmoid_scale(threat_values)

    # Normalize given the range [-10, 10]
    #print (scaled_threat)
    normalized_threat = (scaled_threat - np.min(scaled_threat)) / (np.max(scaled_threat) - np.min(scaled_threat))

    # Ensuring values are within [0,1]
    normalized_threat = np.clip(normalized_threat, 0, 1)
    average_threat = np.mean(normalized_threat)
    cmap = cm

    fig, ax = plt.subplots(figsize=(12, 7))
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    #fig.patch.set_facecolor('xkcd:light grey')

    # Load the pitch image
    pitch_image = image.imread('static/images/football_pitch.png')  # replace this with the actual path to your image
    # Display the image on the axis
    ax.imshow(pitch_image, extent=[0, 100, 0, 100], aspect='auto', alpha=0.7)

    ax.quiver(start_x, start_y, dx, dy, color=cmap(normalized_threat), angles='xy', scale_units='xy', scale=1, alpha=0.5)
    ax.set_xlim([0, 100])
    ax.set_ylim([0, 100])
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.axis('off')


    '''if (success == 1):
        ax.set_title(f"Player({player_id})'s Successful Passes", fontsize=20, color='blue', fontweight='bold', pad=20)
    else:
        ax.set_title(f"Player({player_id})'s Unsuccessful Passes", fontsize=20, color='blue', fontweight='bold', pad=20)'''
    ax.set_xlabel("Pitch X", fontsize=12, fontweight='bold')
    ax.set_ylabel("Pitch Y", fontsize=12, fontweight='bold')

    def save_color_key_image(cmap):
        fig, ax = plt.subplots(figsize=(1, 4))
        cax, _ = matplotlib.colorbar.make_axes(ax)
        cbar = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=matplotlib.colors.Normalize(vmin=-10, vmax=10))
        cbar.set_ticks([-10, 0, 10])
        cbar.set_ticklabels(['-10 (High Negative Threat)', '0 (Neutral Threat)', '10 (High Positive Threat)'])

        ax.axis('off')
        fig.savefig('static/images/color_key.png', bbox_inches='tight', transparent=True)
        plt.close(fig)

    # Call the function to save the color key image
    save_color_key_image(cm)

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.tick_params(axis='both', which='both', length=0, labelsize=10)
    fig1 = plt.gcf()
    #plt.show()
    if (success == 1):
        fig1.savefig(f'static/images/successful_passes/{player_id}.png', transparent = True)
    if (success == 0):
        fig1.savefig(f'static/images/unsuccessful_passes/{player_id}.png', transparent = True)
    return average_threat
# To generate a plot for a specific player:
# generate_player_plot(28468)
