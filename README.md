## Sensor Reading Matcher
This Python program compares readings from a CSV sensor and a JSON sensor to find possible detections of the same anomaly.

How to run
You need Python 3.9 or newer. No extra packages are required.

Put these files in the same folder:
- correlate.py — the simplified Python code
- sensor1.csv — the first sensor's readings
- sensor2.json — the second sensor's readings
Each reading must contain id, latitude, and longitude. The CSV needs these column headers, and the JSON must contain a list of reading objects.

Open a terminal in that folder and run:
python3 correlate.py

How it works
The program reads and checks both files, then uses the Haversine formula to calculate approximate distances in metres. It selects the closest available pairs within 200 metres, using each reading only once.

The 200-metre limit assumes that each sensor can be up to 100 metres away from the actual anomaly. You can change this limit using MATCH_DISTANCE in the code.

Example output 
{
    "56": 46,
    "24": 74
}

The keys are CSV sensor IDs, and the values are JSON sensor IDs. Readings without a match are left ou
