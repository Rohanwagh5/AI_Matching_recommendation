# from flask import Flask, request, jsonify
# import joblib
# import numpy as np
# from geopy.distance import geodesic
# from datetime import datetime
# from datetime import timedelta

# app = Flask(__name__)

# # Load the trained model
# model = joblib.load('ngo_matching_model.pkl')

# # Constants
# MAX_DISTANCE = 50  # Maximum distance for normalization (consistent with your web app)
# MAX_EXPIRATION_HOURS = 168  # Maximum expiration time for normalization (7 days)
# AVERAGE_SPEED = 30  # Average travel speed in km/h

# # Function to calculate dynamic maximum distance
# def calculate_max_distance(expiration_date, current_date):
#     time_difference = (expiration_date - current_date).total_seconds() / 3600  # Convert to hours
#     if time_difference <= 24:
#         return 5  # Max distance: 5 km (for highly perishable food)
#     elif time_difference <= 72:
#         return 10  # Max distance: 10 km (for moderately perishable food)
#     else:
#         return 50  # Max distance: 50 km (for less perishable food)

# # Function to calculate distance between two coordinates
# def calculate_distance(lat1, lon1, lat2, lon2):
#     return geodesic((lat1, lon1), (lat2, lon2)).km

# # Flask endpoint to match NGOs
# @app.route('/match-ngos', methods=['POST'])
# def match_ngos():
#     try:
#         # Get request data
#         data = request.json
#         donor_lat = data['donor_lat']
#         donor_lon = data['donor_lon']
#         expiration_date = datetime.fromisoformat(data['expiration_date'])
#         ngos = data['ngos']  # List of NGOs with latitude, longitude, and email

#         # Current date
#         current_date = datetime.now()

#         # Calculate dynamic maximum distance
#         max_distance = calculate_max_distance(expiration_date, current_date)

#         # Match NGOs
#         matches = []
#         for ngo in ngos:
#             ngo_lat = ngo['latitude']
#             ngo_lon = ngo['longitude']
#             ngo_email = ngo['email']

#             # Calculate distance
#             distance = calculate_distance(donor_lat, donor_lon, ngo_lat, ngo_lon)

#             # Skip NGO if it's beyond the maximum distance
#             if distance > max_distance:
#                 continue

#             # Calculate estimated travel time (in hours)
#             travel_time = distance / AVERAGE_SPEED

#             # Calculate NGO-specific expiration time
#             ngo_expiration_time = expiration_date - timedelta(hours=travel_time)

#             # Calculate NGO-specific time difference
#             time_difference = (ngo_expiration_time - current_date).total_seconds() / 3600  # Convert to hours

#             # Check if the food can reach the NGO before it expires
#             if time_difference <= 0:
#                 continue  # Skip this NGO if the food cannot reach in time

#             # Normalize distance and expiration time
#             normalized_distance = max(0, 1 - distance / MAX_DISTANCE)
#             normalized_expiration = max(0, 1 - time_difference / MAX_EXPIRATION_HOURS)

#             # Predict success score using the model
#             features = [[normalized_distance, normalized_expiration]]
#             success_score = model.predict_proba(features)[0][1]  # Probability of success

#             # Add matched NGO to results
#             matches.append({
#                 'email': ngo_email,
#                 'distance': distance,
#                 'time_difference': time_difference,
#                 'success_score': success_score
#             })

#         # Sort matches by success score (highest score first)
#         matches.sort(key=lambda x: x['success_score'], reverse=True)

#         # Return matched NGOs
#         return jsonify({'matches': matches})

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# # Run the Flask app
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)

from flask import Flask, request, jsonify
import joblib
from geopy.distance import geodesic
from datetime import datetime, timedelta

app = Flask(__name__)

# Load the trained model
model = joblib.load('ngo_matching_model.pkl')

# Constants
MAX_DISTANCE = 50  # Maximum distance for normalization (consistent with your web app)
MAX_EXPIRATION_HOURS = 168  # Maximum expiration time for normalization (7 days)
AVERAGE_SPEED = 30  # Average travel speed in km/h

# Function to calculate dynamic maximum distance
def calculate_max_distance(expiration_date, current_date):
    time_difference = (expiration_date - current_date).total_seconds() / 3600  # Convert to hours
    print(f"Time difference: {time_difference} hours")
    if time_difference <= 24:
        return 10  # Max distance: 5 km (for highly perishable food)
    elif time_difference <= 72:
        return 20  # Max distance: 10 km (for moderately perishable food)
    else:
        return 50  # Max distance: 50 km (for less perishable food)

# Function to calculate distance between two coordinates
def calculate_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).km

# Flask endpoint to match NGOs
@app.route('/match-ngos', methods=['POST'])
def match_ngos():
    try:
        # Get request data
        data = request.json
        donor_lat = data['donor_lat']
        donor_lon = data['donor_lon']
        expiration_date = datetime.fromisoformat(data['expiration_date'])
        ngos = data['ngos']  # List of NGOs with latitude, longitude, and email

        # Current date
        current_date = datetime.now()

        # Calculate dynamic maximum distance
        max_distance = calculate_max_distance(expiration_date, current_date)
        print(f"Maximum allowed distance: {max_distance} km")

        # Match NGOs
        matches = []
        for ngo in ngos:
            ngo_lat = ngo['latitude']
            ngo_lon = ngo['longitude']
            ngo_email = ngo['email']

            # Calculate distance
            distance = calculate_distance(donor_lat, donor_lon, ngo_lat, ngo_lon)
            print(f"Distance to {ngo_email}: {distance} km")

            # Skip NGO if it's beyond the maximum distance
            if distance > max_distance:
                print(f"Skipping {ngo_email}: distance exceeds maximum allowed ({max_distance} km)")
                continue

            # Calculate estimated travel time (in hours)
            travel_time = distance / AVERAGE_SPEED
            print(f"Travel time to {ngo_email}: {travel_time} hours")

            # Calculate NGO-specific expiration time
            ngo_expiration_time = expiration_date - timedelta(hours=travel_time)

            # Calculate NGO-specific time difference
            time_difference = (ngo_expiration_time - current_date).total_seconds() / 3600  # Convert to hours
            print(f"Time difference for {ngo_email}: {time_difference} hours")

            # Check if the food can reach the NGO before it expires
            if time_difference <= 0:
                print(f"Skipping {ngo_email}: travel time exceeds expiration time")
                continue

            # Normalize distance and expiration time
            normalized_distance = max(0, 1 - distance / MAX_DISTANCE)
            normalized_expiration = max(0, 1 - time_difference / MAX_EXPIRATION_HOURS)

            # Predict success score using the model
            features = [[normalized_distance, normalized_expiration]]
            # success_score = model.predict_proba(features)[0][1]  # Probability of success
            success_score = float(model.predict_proba(features)[0][1])

            print(f"Success score for {ngo_email}: {success_score}")

            # Add matched NGO to results
            matches.append({
                'email': ngo_email,
                'distance': distance,
                'time_difference': time_difference,
                'success_score': success_score
            })

        # Sort matches by success score (highest score first)
        matches.sort(key=lambda x: x['success_score'], reverse=True)

        # Return matched NGOs
        return jsonify({'matches': matches})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)