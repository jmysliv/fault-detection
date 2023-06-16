import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import matplotlib.pyplot as plt
import numpy as np

def weighted_average(time_series):
    weights = np.arange(1, len(time_series) + 1)  # Increasing weights
    weighted_sum = np.sum(time_series * weights)
    weight_sum = np.sum(weights)
    weighted_avg = weighted_sum / weight_sum
    return weighted_avg

cred = credentials.Certificate("plotter/config/firebase-key.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://fault-detection-3a4cd-default-rtdb.europe-west1.firebasedatabase.app/' })

sensor_faults = db.reference('test4/sensor-faults/7').get()
for fault in sensor_faults.values():
    if fault is None:
        continue
    plt.bar(f'Fault {fault["fault_id"]}', fault['probability'])
plt.xlabel('Possible Faults')
plt.ylabel('Probability')
plt.ylim(0, 1) 
plt.savefig('plotter/results/test4/probability.png')
plt.clf()
sensor_ids = [1, 2, 3, 6, 7, 8, 9, 10, 11]
for id in sensor_ids:
    events = db.reference(f'test4/events/sensors/{id}').get()
    values = []
    avg_values = []
    timestamps = []
    state = []
    for event in events.values():
        values.append(event['value'])
        avg_values.append(weighted_average(values))
        timestamps.append(event['timestamp'])
        # if event['value'] == 0:
        #     print(event['timestamp'])
        if 'state' in event:
            state.append(event['state'])

    plt.title(f'Sensor {id}')
    plt.plot(timestamps, values, label='Sensor Value')
    if (len(state) > 0):
        try:
            index = state.index('ALARM')
        except:
            index = len(state)
        plt.plot(timestamps[:index], avg_values[:index], label='Weighted Average', color='green')
        plt.plot(timestamps[index-1:], avg_values[index-1:], label='Weighted Average', color='red')
    plt.gca().set_xticklabels([])
    plt.legend()
    plt.xlabel('Time')
    plt.ylabel('Value')
    if id == 6:
        plt.axvline(x='2023-06-16 11:26:02.359145', color='red', linestyle='--', label='Vertical Line')

    plt.savefig('plotter/results/test4/sensor_' + str(id) + '.png')
    plt.clf()
