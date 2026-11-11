import csv
import json
import math

EARTH_RADIUS = 6371008.8 # this is earths radius in metres
MATCH_DISTANCE = 200  # Metres


def validateReadings(readings):
    """Check the readings and convert coordinates to numbers."""
    cleanReadings = []
    usedIds = set()

    for reading in readings:
        if not isinstance(reading, dict):
            raise ValueError("Each reading must be an object.")

        requiredFields = ["id", "latitude", "longitude"]

        for field in requiredFields:
            if field not in reading:
                raise ValueError("Missing field: " + field)

        sensorId = reading["id"]

        if isinstance(sensorId, bool):
            raise ValueError("An ID cannot be a Boolean.")

        if not isinstance(sensorId, (int, str)):
            raise ValueError("An ID must be an integer or string.")

        idText = str(sensorId)

        if idText.strip() == "":
            raise ValueError("An ID cannot be empty.")

        if idText in usedIds:
            raise ValueError("Duplicate ID: " + idText)

        if isinstance(reading["latitude"], bool):
            raise ValueError("Latitude must be a number.")

        if isinstance(reading["longitude"], bool):
            raise ValueError("Longitude must be a number.")

        latitude = float(reading["latitude"])
        longitude = float(reading["longitude"])

        if not math.isfinite(latitude) or not -90 <= latitude <= 90:
            raise ValueError("Invalid latitude.")

        if not math.isfinite(longitude) or not -180 <= longitude <= 180:
            raise ValueError("Invalid longitude.")

        cleanReadings.append({
            "id": sensorId,
            "latitude": latitude,
            "longitude": longitude
        })

        usedIds.add(idText)

    return cleanReadings


def readCsvFile(filename):
    """Read the first sensor's CSV file."""
    with open(filename, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        requiredFields = ["id", "latitude", "longitude"]

        for field in requiredFields:
            if field not in (reader.fieldnames or []):
                raise ValueError("Missing CSV column: " + field)

        readings = list(reader)

    return validateReadings(readings)


def readJsonFile(filename):
    """Read the second sensor's JSON file."""
    with open(filename, "r", encoding="utf-8-sig") as file:
        readings = json.load(file)

    if not isinstance(readings, list):
        raise ValueError("The JSON file must contain a list.")

    return validateReadings(readings)


def calculateDistance(first, second): # Calculate the approximate distance in metres using Haversine.
    latitude1 = math.radians(first["latitude"])
    latitude2 = math.radians(second["latitude"])

    latitudeDifference = latitude2 - latitude1
    longitudeDifference = math.radians(
        second["longitude"] - first["longitude"]
    )

    a = (
        math.sin(latitudeDifference / 2) ** 2
        + math.cos(latitude1)
        * math.cos(latitude2)
        * math.sin(longitudeDifference / 2) ** 2
    )

    # Protect against small floating-point rounding errors.
    a = max(0.0, min(1.0, a))

    angle = 2 * math.asin(math.sqrt(a))

    return EARTH_RADIUS * angle


def findMatch(sensor1, sensor2, max_distance): #  Choose the closest available pairs without reusing readings.
    if not math.isfinite(max_distance) or max_distance < 0:
        raise ValueError("Maximum distance must be finite and nonnegative.")

    possibleMatches = []

    # Compare each reading from sensor 1 with each from sensor 2.
    for i in range(len(sensor1)):
        for j in range(len(sensor2)):
            distance = calculateDistance(sensor1[i], sensor2[j])

            if distance <= max_distance:
                possibleMatches.append((distance, i, j))

    # Tuples sort by their first value: distance.
    possibleMatches.sort()

    usedSensor1 = set()
    usedSensor2 = set()
    matches = {}

    for distance, i, j in possibleMatches:
        if i in usedSensor1 or j in usedSensor2:
            continue

        first_id = str(sensor1[i]["id"])
        second_id = sensor2[j]["id"]

        matches[first_id] = second_id

        usedSensor1.add(i)
        usedSensor2.add(j)

    return matches


def main():
    try:
        sensor1 = readCsvFile("SensorData1.csv")
        sensor2 = readJsonFile("SensorData2.json")

        matches = findMatch(sensor1, sensor2, MATCH_DISTANCE)

        print(json.dumps(matches, indent=4))

    except (OSError, ValueError, TypeError, csv.Error) as error:
        print("Error:", error)
        raise SystemExit(1)


if __name__ == "__main__":
    main()