from matplotlib import pyplot as plt


def make_graph_of_speeds(title, values, xlabel, ylabel):
    
    x = [i for i in range(len(values))]

    # Create a line plot
    plt.plot(x, values, marker='o', linestyle='', color='b')
    # Add title and labels
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.xticks(range(0, len(values) + 1, 5))
    
    # Show the plot
    plt.show()
    
make_graph_of_speeds("RPI Image Capture and SSH Speed", [1.2, 0.81, 0.82, 0.85, 0.86, 0.82, 0.88, 0.85, 0.87, 0.81, 0.85, 0.83], "Image number", "Time taken for image capture and ssh (seconds)")