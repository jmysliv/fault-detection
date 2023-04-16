from .config_parser.config import Config
import networkx as nx
import matplotlib.pyplot as plt

class Supervisor:
    def __init__(self, config: Config):
        self.config = config
        self.sensors_to_monitor = []
        self.visualize_knowledge_graph()
        self.prioritize_sensors()

    def visualize_knowledge_graph(self):
        self.G = nx.Graph()
        # Add sensor nodes to the graph
        for sensor in self.config.sensor_list:
            self.G.add_node(f'S_{sensor.id}', label=sensor.name)
        # Add fault nodes to the graph
        for fault in self.config.faults:
            self.G.add_node(f'F_{fault.id}', color='red', label=fault.name)
            # Add edges between sensors and faults
            for symptom in fault.symptoms:
                self.G.add_edge(f'S_{symptom.sensor_id}', f'F_{fault.id}')

        # Draw the graph using Matplotlib
        nx.draw(self.G, with_labels=True, node_color=[self.G.nodes[node]['color'] if 'color' in self.G.nodes[node] else 'blue' for node in self.G.nodes])
        plt.show()
     

    def prioritize_sensors(self):
        connected_components = list(nx.connected_components(self.G))

        connected_subgraphs = []
        for component in connected_components:
            if len(component) == 1:
                continue
            subgraph = self.G.subgraph(component)
            connected_subgraphs.append(subgraph)

        for subgraph in connected_subgraphs:
            articulation_points = [ point for point in list(nx.articulation_points(subgraph)) if point[0] == 'S']
            print(articulation_points)
            self.sensors_to_monitor.extend(articulation_points)
            # Draw the graph using Matplotlib
            # nx.draw(subgraph, with_labels=True, node_color=[subgraph.nodes[node]['color'] if 'color' in subgraph.nodes[node] else 'blue' for node in subgraph.nodes])
            # plt.show()