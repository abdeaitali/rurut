def create_graph(data, title='Graph', xlabel='X-axis', ylabel='Y-axis'):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 6))
    plt.plot(data['x'], data['y'], marker='o', linestyle='-')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.show()

def save_graph(data, filename='graph.png'):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 6))
    plt.plot(data['x'], data['y'], marker='o', linestyle='-')
    plt.savefig(filename)

def create_bar_graph(data, title='Bar Graph', xlabel='Categories', ylabel='Values'):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 6))
    plt.bar(data['categories'], data['values'])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(axis='y')
    plt.show()