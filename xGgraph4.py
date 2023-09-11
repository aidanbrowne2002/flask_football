import psycopg2
from psycopg2 import extras
from data import credentials
import matplotlib.pyplot as plt
from collections import defaultdict


# Initialize the database pool

def fetch_avg_stats_from_db(player_id, postgreSQL_pool):
    ps_connection = postgreSQL_pool.getconn()
    ps_cursor = ps_connection.cursor()
    """Fetch average xG and goals per minute from the player table in the database."""
    query = f"""SELECT xG, avg_goals FROM players WHERE id = {player_id};"""
    ps_cursor.execute(query)
    result = ps_cursor.fetchone()
    ps_cursor.close()
    # release the connection back to connection pool
    postgreSQL_pool.putconn(ps_connection)
    return {"AVGMinutes/xG": result[0], "AVGMinutes/Goals": result[1], "playerID": player_id}


def fetch_players_by_positions(query, postgreSQL_pool):
    ps_connection = postgreSQL_pool.getconn()
    ps_cursor = ps_connection.cursor()
    """Fetch players based on the given query."""
    ps_cursor.execute(query)
    results = ps_cursor.fetchall()
    ps_cursor.close()
    # release the connection back to connection pool
    postgreSQL_pool.putconn(ps_connection)
    return [t[0] for t in results]

def initialisexgraph4(postgreSQL_pool):
    querys = [
        """select id from players
            where position in ('Striker', 'Second Striker');""",
        """select id from players
            where position in ('Defensive Midfielder', 'Central Midfielder', 'Attacking Midfielder');""",
        """select id from players
            where position in ('Wing Back', 'Winger');""",
        """select id from players
            where position in ('Full Back', 'Central Defender', 'Full Back');"""


    ]

    avgGoalsTotals = []
    avgxGTotals = []

    for index, query in enumerate(querys):
        players = fetch_players_by_positions(query, postgreSQL_pool)
        avgGoals = []
        avgxG = []

        for x in players:
            #print(f"Player: {x}")
            #print(f"Position: {index + 1} of {len(querys)}")
            #print(f"player {players.index(x) + 1} of {len(players)}")
            stat = fetch_avg_stats_from_db(x, postgreSQL_pool)
            avgGoals.append([stat['playerID'], stat['AVGMinutes/Goals']])
            avgxG.append([stat['playerID'], stat['AVGMinutes/xG']])

        avgGoals = [x for x in avgGoals if x[1] != 0]
        avgGoals.sort(key=lambda x: x[1])
        avgGoalsTotals.append(avgGoals)

        avgxG = [x for x in avgxG if x[1] != 0 and x[1] < 2000]
        avgxG.sort(key=lambda x: x[1])
        avgxGTotals.append(avgxG)
    return avgGoalsTotals, avgxGTotals


def genGraphs(playerID, postgreSQL_pool, avgGoalsTotals, avgxGTotals):
    ps_connection = postgreSQL_pool.getconn()
    ps_cursor = ps_connection.cursor()
    playerID = int(playerID)
    #print(f"THIS IS THE PLAYER ID ({playerID})")
    query = f"""select f_name, l_name from players where id = {playerID};"""
    ps_cursor.execute(query)
    name = ps_cursor.fetchall()
    name = list(name[0])
    ps_cursor.close()
    # release the connection back to connection pool
    postgreSQL_pool.putconn(ps_connection)

    def generate_graph(avg_data, ylabel, save_path):
        for i, matrix in enumerate(avg_data):
            for j, row in enumerate(matrix):
                if row[0] == playerID:
                    plt.figure()
                    plt.clf()

                    new_array = [[value[1] for value in inner_list] for inner_list in avg_data]

                    for line in new_array:
                        plt.plot(line, linewidth = 3)

                    plt.xlabel('Rank', color='white')
                    plt.ylabel(ylabel, color='white')
                    plt.gca().spines['bottom'].set_color('white')
                    plt.gca().spines['top'].set_color('white')
                    plt.gca().spines['right'].set_color('white')
                    plt.gca().spines['left'].set_color('white')

                    # Set the tick label colors to white
                    plt.tick_params(axis='x', colors='white')
                    plt.tick_params(axis='y', colors='white')
                    #plt.title(f'{name[0]} {name[1]}-- rank {j} --- vs others {ylabel}', color='white')
                    plt.grid(True)
                    plt.scatter(j, row[1], color='white', s=90)
                    plt.gca().invert_yaxis()
                    plt.legend(["Strikers", "Midfielders", "Wingers/Wingbacks", "Defenders"])
                    fig1 = plt.gcf()
                    plt.subplots_adjust(left=0.1, right=0.9, top=0.98, bottom=0.1)
                    #plt.show()
                    fig1.savefig(save_path, transparent=True)
                    return j

    goals_rank = generate_graph(avgGoalsTotals, 'Average Minutes per Goal', f'static/images/ranks/goals/{playerID}.png')
    xGRank = generate_graph(avgxGTotals, 'Average Minutes per xG', f'static/images/ranks/xG/{playerID}.png')
    return (goals_rank + 1, xGRank + 1)


#print("at end")
#genGraphs(9808)