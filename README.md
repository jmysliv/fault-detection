# Knowladge-Based Fault Detection

## Config

Define set of sensor/metrics for which your system collects data in the `config/sensors.yaml`. The format should be as follows:

```yaml
sensors:
    sensor_name:
        id: number
    ...
```

Then for each possible fault in your system define his own 'Fault Card'.
Each faults can have different symptoms and reasons. The format should be as follows:

```yaml
fault_name:
    - symptoms:
        - symptom_id: number
          value: low | high
          temporal: periodic | progressive
        - ...
      reasons:
        - name: name
          action: action description
        - ...
    - ...
```