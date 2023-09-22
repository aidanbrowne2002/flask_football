import matplotlib.pyplot as plt


def save_color_key_image(num1, num2, player1, player2, outcome):
    # Create a list to hold the numbers and labels
    labels = ['Number 1', 'Number 2']

    # Create a bar chart with adjusted bar width and larger text
    fig, ax = plt.subplots()



    # Set the title and labels
    plt.title('Green Bar Chart', fontsize=16)  # Adjust title font size here
    plt.xlabel('Numbers', fontsize=14)  # Adjust x-label font size here
    plt.ylabel('Values', fontsize=14)  # Adjust y-label font size here

    # Adjust font size of tick labels on the x and y axes
    ax.tick_params(axis='x', labelsize=25)  # Adjust x-axis tick label font size here
    ax.tick_params(axis='y', labelsize=25)  # Adjust y-axis tick label font size here
    # Force the y-axis to range from -2 to 2
    ax.set_ylim(-2, 2)

    if outcome == 1:
        bars = ax.bar(labels, [num1, num2], color='green', width=0.5)  # Adjust bar width here
        fig.savefig(f'static/images/color_key_success/{player1}_{player2}.png', bbox_inches='tight', transparent=True)
    else:
        bars = ax.bar(labels, [num1, num2], color='red', width=0.5)  # Adjust bar width here
        fig.savefig(f'static/images/color_key_unsuccess/{player1}_{player2}.png', bbox_inches='tight', transparent=True)
    plt.close(fig)




