Factory Method

Problem
Our application has different types of sensors. If we create each sensor directly, adding a new sensor means changing many parts of the code.
---

Solution
Factory Method puts sensors creation in one place. We use a creator interface and seperate creator classes for each sensor type.
---

Where to look
The main code is in: backend/src/domain/sensors/creators.py
The API that uses the creators is in: backend/src/interfaces/api/sensors.py
---

Extension Exercise
To add a TemperatureSensorCreator. It should create a temperature sensor with:
device_type: temperature_sensor
unit: celcius

Then add it to the creator registry and test it through the API