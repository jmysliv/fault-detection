from .config import Config
import networkx as nx
# import matplotlib.pyplot as plt
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
        # nx.draw(self.G, with_labels=True, node_color=[self.G.nodes[node]['color'] if 'color' in self.G.nodes[node] else 'blue' for node in self.G.nodes])
        # plt.show()
     

    def prioritize_sensors(self):
        # set cover greedy algorithm
        universe = set([f'F_{fault.id}' for fault in self.config.faults])
        sensors = set([f'S_{sensor.id}' for sensor in self.config.sensor_list])
        while len(universe) > 0:
            best_sensor = None
            best_sensor_faults = set()
            for sensor in sensors:
                sensor_faults = set(list(self.G.neighbors(sensor))).intersection(universe)
                if len(sensor_faults) > len(best_sensor_faults):
                    best_sensor = sensor
                    best_sensor_faults = set(sensor_faults)
            sensors.remove(best_sensor)
            universe -= best_sensor_faults
            self.sensors_to_monitor.append(best_sensor)
        print(self.sensors_to_monitor)
    
    def handle_sensor_data(self, topic, json_data):
        data: SensorData = json.loads(json_data)
        if isinstance(data, (str, int, float)):
            return
        print(data)
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
                        # normalize the probability by the number of symptoms
                        probability = round(sensor.get_symptom_probability(symptom) / len(fault.symptoms), 2)
                        G.add_edge(f'S_{symptom.sensor_id}', f'F_{fault.id}', weight=probability)

                # pos = nx.spring_layout(G)
                # weights = [G[u][v]['weight'] for u, v in G.edges()]
                # nx.draw(G, pos, with_labels=True, width=weights, node_color=[G.nodes[node]['color'] if 'color' in G.nodes[node] else 'blue' for node in G.nodes])
                # edge_labels = nx.get_edge_attributes(G, 'weight')
                # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
                # plt.show()
                max_weight = 0
                max_vertex = None
                for vertex in G.nodes:
                    weight = G.in_degree(vertex, weight='weight')
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

