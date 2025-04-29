import matplotlib.pyplot as plt
import pandas as pd

def plot_data(data, x_column, y_column, title='Data Plot', xlabel='X-axis', ylabel='Y-axis'):
    plt.figure(figsize=(10, 6))
    plt.plot(data[x_column], data[y_column], marker='o', linestyle='-', color='b')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid()
    plt.show()

def save_plot(data, x_column, y_column, filename='plot.png'):
    plt.figure(figsize=(10, 6))
    plt.plot(data[x_column], data[y_column], marker='o', linestyle='-', color='b')
    plt.title('Data Plot')
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.grid()
    plt.savefig(filename)
    plt.close()