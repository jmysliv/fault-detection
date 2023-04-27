from .config import Config
import networkx as nx
import matplotlib.pyplot as plt
import json
from .sensor import SensorData
from typing import List

class Supervisor:
    config: Config
    sensors_to_monitor: List[str]
    G: nx.Graph
    def __init__(self, config: Config):
        self.config = config
        self.sensors_to_monitor = []
        self.visualize_knowledge_graph()
        self.prioritize_sensors()

    def visualize_knowledge_graph(self):
        self.G = nx.Graph()
        # Add sensor nodes to the graph
        for sensor in self.config.sensor_list:
            self.G.add_node(f'S_{sensor.id}', label=sensor.name, id=sensor.id, color='blue')
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
    
    def handle_sensor_data(self, topic, json_data):
        data: SensorData = json.loads(json_data)
        sensor = self.config.get_sensor(data['sensor_id'])

        if sensor is None:
            return

        check_alarm = topic in self.sensors_to_monitor

        alarm = sensor.on_data_received(data, check_alarm)


        if alarm is not None:
            print(alarm)
            possible_faults = [fault for fault in self.config.faults if fault.has_symptom(alarm.sensor_id, alarm.value)]
            if len(possible_faults) > 1:
                sensors_to_check = list(set([ symptom.sensor_id for fault in possible_faults for symptom in fault.symptoms ]))
                print(sensors_to_check)
                # creating a graph to find the fault
                G = nx.DiGraph()
                for id in sensors_to_check:
                    sensor = self.config.get_sensor(id)
                    G.add_node(f'S_{sensor.id}', label=sensor.name, id=sensor.id, color='blue')
                # Add fault nodes to the graph
                for fault in possible_faults:
                    G.add_node(f'F_{fault.id}', color='red', label=fault.name)
                    # Add edges between sensors and faults
                    for symptom in fault.symptoms:
                        sensor = self.config.get_sensor(symptom.sensor_id)
                        probability = round(sensor.get_symptom_probability(symptom), 2)
                        G.add_edge(f'S_{symptom.sensor_id}', f'F_{fault.id}', weight=probability)

                pos = nx.spring_layout(G)
                weights = [G[u][v]['weight'] for u, v in G.edges()]
                nx.draw(G, pos, with_labels=True, width=weights, node_color=[G.nodes[node]['color'] if 'color' in G.nodes[node] else 'blue' for node in G.nodes])
                edge_labels = nx.get_edge_attributes(G, 'weight')
                nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
                plt.show()
                max_weight = 0
                max_vertex = None
                for vertex in G.nodes:
                    print(vertex)
                    weight = G.in_degree(vertex, weight='weight')
                    print(weight)
                    if weight > max_weight:
                        max_weight = weight
                        max_vertex = vertex
                print("FAULT DETECTED")
                print(max_vertex)
                print(max_weight)
                
            elif len(possible_faults) == 1:
                print("FAULT DETECTED")
                print(possible_faults[0].reasons)
                print(possible_faults[0].actions)

