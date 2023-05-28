from .config import Config
import networkx as nx
# import matplotlib.pyplot as plt
import json
from .sensor import SensorData
from typing import List
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime

cred = credentials.Certificate("supervisor/config/firebase-key.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://fault-detection-3a4cd-default-rtdb.europe-west1.firebasedatabase.app/' })
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
        # remove ok edges
        ok_edges = []
        for fault in self.config.faults:
            # Add edges between sensors and faults
            for symptom in fault.symptoms:
                if symptom.value == 'ok':
                    ok_edges.append((f'S_{symptom.sensor_id}', f'F_{fault.id}'))
                    self.G.remove_edge(f'S_{symptom.sensor_id}', f'F_{fault.id}')

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

        # add ok edges back
        for edge in ok_edges:
            self.G.add_edge(edge[0], edge[1])
    
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
        if not check_alarm:
            return
        
        timestamp = datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
        # Calculate the milliseconds since epoch
        milliseconds = int(timestamp.timestamp() * 1000)
        id = str(sensor.id) + '_' + str(milliseconds)
        event_ref = db.reference(f'events/sensors/{id}')
        sensor_ref = db.reference(f'sensors/{sensor.id}')


        if alarm is not None:
            event = {
                'sensor_id': sensor.id,
                'timestamp': data['timestamp'],
                'state': 'ALARM'
            }
            event_ref.set(event)
            sensor_ref.set(event)
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
                    symptoms_probability = []
                    overall_probability = 0
                    for symptom in fault.symptoms:
                        sensor = self.config.get_sensor(symptom.sensor_id)
                        # normalize the probability by the number of symptoms
                        probability = round(sensor.get_symptom_probability(symptom) / len(fault.symptoms), 2)
                        symptoms_probability.append({
                            'sensor_id': symptom.sensor_id,
                            'probability': probability
                        })
                        overall_probability += probability
                        G.add_edge(f'S_{symptom.sensor_id}', f'F_{fault.id}', weight=probability)
                    fault_event= {
                        'alarm_trigger_id': sensor.id,
                        'fault_id': fault.id,
                        'timestamp': data['timestamp'],
                        'symptoms': symptoms_probability,
                        'probability': overall_probability
                    }
                    fault_ref = db.reference(f'events/faults/{fault.id}')
                    fault_ref.set(fault_event)

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
        else:
            event = {
                'sensor_id': data['sensor_id'],
                'timestamp': data['timestamp'],
                'state': 'OK'
            }
            event_ref.set(event)
            sensor_ref.set(event)

