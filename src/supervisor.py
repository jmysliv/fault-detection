from .config import Config
import networkx as nx
import matplotlib.pyplot as plt
import json
from .sensor import SensorData

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
        print(topic)
        data: SensorData = json.loads(json_data)
        sensor = self.config.get_sensor(data['sensor_id'])

        check_alarm = topic in self.sensors_to_monitor

        alarm = sensor.onDataReceived(data, check_alarm)

        if alarm is not None:
            # TODO find faults associated with this alarm
            possible_faults = [fault for fault in self.config.faults if fault.has_symptom(alarm.sensor_id, alarm.value)]
            print(possible_faults)
            if len(possible_faults) > 1:
                sensors_to_check = list(set([ symptom.sensor_id for fault in possible_faults for symptom in fault.symptoms ]))
                print(sensors_to_check)
                pass
                # TODO analyze data from sensors and find the fault
            elif len(possible_faults) == 1:
                print("FAULT DETECTED")
                print(possible_faults[0].reasons)
                print(possible_faults[0].actions)

