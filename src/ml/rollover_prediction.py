"""
Troll-vs-Troll Project
Rollover Risk Prediction Module

This module implements machine learning algorithms to predict rollover 
risk based on sensor data (accelerometer, gyroscope, etc.). Uses 
real-time data to determine when differential control is needed.

Version: 1.0.0
"""

import time
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class RolloverPredictor:
    """
    Machine learning model to predict rollover risk based on sensor data.
    Uses a combination of anomaly detection and threshold-based algorithms
    to determine when the pull-handle carrier is at risk of rollover.
    """
    
    def __init__(self):
        """
        Initialize the rollover prediction model.
        """
        # TODO: Implement machine learning model for rollover prediction - HIGH - Developer
        # TODO: Use accelerometer and other sensor data to predict rollover risk - HIGH - Developer
        # TODO: Implement real-time prediction algorithm - MEDIUM - Developer
        
        # Initialize ML components
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        
        # Thresholds based on research (from GB/T 21023-2024 standard)
        self.rollover_angle_threshold = 15.0  # degrees
        self.wheel_slip_threshold = 0.1  # ratio
        
        # Store historical data for prediction
        self.historical_data = []
        self.max_history = 100
        
        # Model parameters
        self.is_trained = False
        self.normal_behavior_model = None
        
        print("RolloverPredictor initialized")

    def preprocess_sensor_data(self, accel_data, gyro_data=None, time_stamp=None):
        """
        Preprocess sensor data for ML model.
        
        Args:
            accel_data (tuple): (x, y, z) acceleration values
            gyro_data (tuple, optional): (x, y, z) gyroscope values
            time_stamp (float, optional): Timestamp of the reading
            
        Returns:
            np.array: Processed feature vector
        """
        # Extract features from raw sensor data
        ax, ay, az = accel_data
        
        # Calculate magnitude of acceleration
        accel_magnitude = (ax**2 + ay**2 + az**2)**0.5
        
        # Calculate tilt angles (simplified)
        pitch = np.arctan2(ax, np.sqrt(ay**2 + az**2)) * 180 / np.pi
        roll = np.arctan2(ay, az) * 180 / np.pi
        
        # Create feature vector
        features = [ax, ay, az, accel_magnitude, pitch, roll]
        
        if gyro_data:
            gx, gy, gz = gyro_data
            features.extend([gx, gy, gz])
        
        if time_stamp:
            features.append(time_stamp)
            
        return np.array(features).reshape(1, -1)

    def predict_rollover_risk(self, accel_data, gyro_data=None):
        """
        Predict the rollover risk based on sensor data.
        
        Args:
            accel_data (tuple): (x, y, z) acceleration values
            gyro_data (tuple, optional): (x, y, z) gyroscope values
            
        Returns:
            dict: Risk assessment with probability and confidence
        """
        # Preprocess the input data
        features = self.preprocess_sensor_data(accel_data, gyro_data, time.time())
        
        # Simple threshold-based prediction (would be replaced with trained model)
        ax, ay, az, accel_mag, pitch, roll = features[0][:6]
        
        # Calculate risk factors
        tilt_risk = max(abs(pitch), abs(roll)) / self.rollover_angle_threshold
        accel_risk = accel_mag / 9.81  # normalized to gravity
        
        # Combined risk score (simplified model)
        risk_score = min(1.0, max(tilt_risk, accel_risk - 1.0))
        
        # Determine risk level
        if risk_score > 0.8:
            risk_level = "HIGH"
        elif risk_score > 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
            
        return {
            "risk_score": float(risk_score),
            "risk_level": risk_level,
            "tilt_angle": max(abs(pitch), abs(roll)),
            "acceleration": accel_mag,
            "needs_control": risk_score > 0.3
        }

    def update_model(self, new_data_point):
        """
        Update the model with new data (online learning).
        
        Args:
            new_data_point: New sensor data point to learn from
        """
        # Add to historical data
        self.historical_data.append(new_data_point)
        
        # Keep only recent data
        if len(self.historical_data) > self.max_history:
            self.historical_data.pop(0)
            
        # Retrain if enough data is available
        if len(self.historical_data) > 10 and not self.is_trained:
            self._train_model()
            self.is_trained = True

    def _train_model(self):
        """
        Internal method to train the ML model on historical data.
        """
        if len(self.historical_data) == 0:
            return
            
        # Convert historical data to feature matrix
        feature_matrix = np.array(self.historical_data)
        
        # Normalize the features
        normalized_features = self.scaler.fit_transform(feature_matrix)
        
        # Train anomaly detector
        self.anomaly_detector.fit(normalized_features)
        
        self.is_trained = True
        print(f"Model trained on {len(self.historical_data)} data points")


def main():
    """
    Main function for testing the rollover prediction module.
    """
    print("Testing Rollover Prediction Module...")
    
    predictor = RolloverPredictor()
    
    # Simulate some test data
    test_accel_data = (0.5, 0.2, 9.8)  # Normal state
    result = predictor.predict_rollover_risk(test_accel_data)
    print(f"Normal state: {result}")
    
    test_accel_data = (2.0, 4.0, 8.0)  # High risk state
    result = predictor.predict_rollover_risk(test_accel_data)
    print(f"High risk state: {result}")


if __name__ == "__main__":
    main()