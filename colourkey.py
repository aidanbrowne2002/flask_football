import matplotlib.pyplot as plt

def save_color_key_image(num1, num2, player1, player2, outcome):
    # Create a list to hold the numbers and labels
    fig, ax = plt.subplots()

    # Create boxplots for the datasets with larger markers and labels
    data = [num1, num2]
    box = ax.boxplot(data, labels=['Player 1', 'Player 2'], patch_artist=True,
                     boxprops=dict(facecolor='lightblue'), widths=0.8)  # Adjust the width as needed

    # Customize the plot
    ax.set_title('Boxplot of Two Datasets', fontsize=40)  # Increase title font size
    ax.set_xlabel('Datasets', fontsize=40)  # Increase x-axis label font size
    ax.set_ylabel('Values', fontsize=40)  # Increase y-axis label font size

    # Increase font size for tick labels on both x and y axes
    ax.tick_params(axis='both', labelsize=40)

    # Increase font size for boxplot labels
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(40)

    # Increase the line width and style for the boxplot elements
    for element in ['boxes', 'whiskers', 'medians', 'caps']:
        plt.setp(box[element], linewidth=8)  # Increase the linewidth

    # Set the y-axis limits to force a range from -2 to 2
    ax.set_ylim(-2, 2)

    # Set the figure size to make it thicker and taller
    fig.set_size_inches(12, 17)  # Adjust the width and height as needed

    if outcome == 1:
        fig.savefig(f'static/images/color_key_success/{player1}_{player2}.png', bbox_inches='tight', transparent=True)
    else:
        fig.savefig(f'static/images/color_key_unsuccess/{player1}_{player2}.png', bbox_inches='tight', transparent=True)
    plt.close(fig)
