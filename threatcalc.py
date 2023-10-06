import numpy as np
import psycopg2
from data import credentials
import matplotlib.pyplot as plt

class PitchThreat:
    def __init__(self):
        # Defining parameters
        self.successRateMultiplier = 100  # The value the success percentage is multiplied by
        self.xValueMultiplier = 1
        self.xAddOrMultiply = 0  # x value multiplied by mutiplier  (1) x value added then multiplied (0)
        self.yValuexMultiplier = 1.6
        self.yValueMultiplier = 0.1
        self.yStart = 1

        self.pitch = self.generate_pitch()

    def generate_pitch(self):
        # Connecting to the database
        conn = psycopg2.connect(database=credentials.database,
                                host=credentials.host,
                                user=credentials.user,
                                password=credentials.password,
                                port=credentials.port)
        cursor = conn.cursor()

        query = """select event_id, event_type, player_id, x, y from eventfact
        where event_type IN (13,14,15,16)"""
        cursor.execute(query)
        result = cursor.fetchall()

        pitch = [[[] for _ in range(20)] for _ in range(20)]

        # Populate the grid with shot outcomes
        for row in result:
            x_index = int(row[3] // 5)  # Dividing by 5 to create 20 segments in x
            y_index = int(row[4] // 5)  # Dividing by 5 to create 20 segments in y
            pitch[x_index][y_index].append(row[1])
        # Calculate the percentage of successful shots for each grid section
        # Also count total shots for each grid section
        total_shots = [[0 for _ in range(20)] for _ in range(20)]
        for i in range(20):
            for j in range(20):
                if pitch[i][j]:
                    total_shots[i][j] = len(pitch[i][j])  # Store total shots before overwriting pitch[i][j]
                    success_rate = pitch[i][j].count(16) / len(pitch[i][j])  # Count successful shots and divide by total shots
                    if success_rate == 1:
                        success_rate = 0
                    threatValue = success_rate * self.successRateMultiplier + 1
                    pitch[i][j] = threatValue
                else:
                    pitch[i][j] = 1  # If there are no shots in this section, set the threat level to 1
                    total_shots[i][j] = 0
                if self.xAddOrMultiply == 0:
                    pitch[i][j] = (pitch[i][j] * i / 10 * self.xValueMultiplier) + 0.01
                else:
                    pitch[i][j] += i / 10 * self.xValueMultiplier
                if j < 10 and i > self.yStart:
                    pitch[i][j] += (j ** (self.yValueMultiplier * i * self.yValuexMultiplier)) / 10
                if j >= 10 and i > self.yStart:
                    pitch[i][j] += (((20 - j - 1)) ** (self.yValueMultiplier * i * self.yValuexMultiplier)) / 10
                # pitch[i][j] = round(pitch[i][j], 1)
                # New adjustment to increase pitch[i][j] when i is large and j is large or small
                if i > 12:
                    if j < 5 or j > 15:
                        pitch[i][j] += 1.1 ** i  # Adjust as needed

                # pitch[i][j] = round(pitch[i][j], 1)

        # Apply log scaling
        pitch = self.log_scale_array(pitch)

        plt.figure(figsize=(10, 10))
        plt.imshow(pitch, cmap='viridis', origin='lower')  # set origin to 'lower' to invert the plot

        for i in range(len(pitch)):
            for j in range(len(pitch[i])):
                text = plt.text(j, i, np.around(pitch[i][j], decimals=2),
                                ha="center", va="center", color="w")

        plt.title('Pitch Visualization')
        plt.colorbar()
        fig1 = plt.gcf()
        #plt.show()
        fig1.savefig(f'static/images/threatlevels.png')
        plt.close(fig1)
        return pitch

    def log_scale_array(self, pitch, new_min=0, new_max=10):
        # Add 1 to all values to ensure positivity
        # Apply the logarithm
        log_pitch = np.log(pitch)

        # Scale the values
        min_value = np.min(log_pitch)
        max_value = np.max(log_pitch)
        scaled_pitch = ((log_pitch - min_value) / (max_value - min_value)) * (new_max - new_min) + new_min

        # Round to 1 decimal place
        return np.round(scaled_pitch, 1)

    def calculate_threat_difference(self, start, end):
        # Get pitch dimensions
        pitch_height, pitch_width = self.pitch.shape

        # Scale the x and y coordinates to match the pitch dimensions
        start_x = int(start[1] * ((pitch_width - 1) / 100))  # x corresponds to the columns (width)
        start_y = int(start[0] * ((pitch_height - 1) / 100))  # y corresponds to the rows (height)
        end_x = int(end[1] * ((pitch_width - 1) / 100))  # x corresponds to the columns (width)
        end_y = int(end[0] * ((pitch_height - 1) / 100))  # y corresponds to the rows (height)

        # Fetch the threat values at the start and end points
        start_threat = self.pitch[start_y][start_x]
        end_threat = self.pitch[end_y][end_x]

        # Return the difference in threat
        #print (end_threat, start_threat)
        return end_threat - start_threat
