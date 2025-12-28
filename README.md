# Troll-vs-Troll

## Version Log
- v1.0.0 2025-12-28: Initial version - Success
- v1.0.1 2025-12-28: Added UNIHIKER M10 hardware foundation information - Success

## Project Version: 1.0.1

*For SES student project*: Trolley-Anti-Troll is an electronic differential system for pull-handle carriers (e.g., suitcases) to prevent rollover. It replaces mechanical structures with lightweight electronic control, using real-time wheel slip monitoring to enhance stability during turns. Low-cost, energy-efficient, and easy to deploy.

This project will be developed around and based on the UNIHIKER M10 Model flight control board as the hardware foundation.

## Project Features and Usage

Trolley-Anti-Troll is designed to prevent rollover in pull-handle carriers (e.g., suitcases) by implementing an electronic differential system. The system monitors wheel slip in real-time and adjusts wheel speeds during turns to maintain stability.

For detailed version history and updates, please see [Update_Log.md](file:///E:/Comp/特需/Troll-vs-Troll-main/Troll-vs-Troll-main/Update_Log.md).

## New Feature: UNIHIKER M10 Benchmark Demo

The project now includes a comprehensive benchmark demo ([benchmark.py](file:///E:/Comp/特需/Troll-vs-Troll-main/Troll-vs-Troll-main/src/main/benchmark.py)) that tests all onboard sensors, display components, and computational performance of the UNIHIKER M10 board. The demo features a page-based UI to navigate through different sensor readings and performance metrics.

## Machine Learning Component

The project now includes a machine learning module for predicting rollover risk based on sensor data. The [rollover_prediction.py](file:///E:/Comp/特需/Troll-vs-Troll-main/Troll-vs-Troll-main/src/ml/rollover_prediction.py) module implements algorithms to predict when the pull-handle carrier is at risk of rollover using accelerometer and gyroscope data.

## Sensor Data Processing

The [data_processor.py](file:///E:/Comp/特需/Troll-vs-Troll-main/Troll-vs-Troll-main/src/sensors/data_processor.py) module processes raw sensor data to extract meaningful features for the machine learning model. It includes filtering, feature extraction, and anomaly detection capabilities.

## Differential Control System

The [differential_controller.py](file:///E:/Comp/特需/Troll-vs-Troll-main/Troll-vs-Troll-main/src/control/differential_controller.py) module implements the electronic differential control algorithm. It adjusts wheel speeds based on the machine learning model's rollover risk predictions to prevent side tipping during turns and sudden movements.

## Sensor Data Generation

The [data_generator.py](file:///E:/Comp/特需/Troll-vs-Troll-main/Troll-vs-Troll-main/src/utils/data_generator.py) module generates realistic sensor data for training and testing the machine learning models. The data simulates real-world scenarios for pull-handle carriers including normal movement, turns, and rollover risks.

## Important Notice

If you are a developer or an AI tool assisting in writing project code, you **must** thoroughly read and strictly follow all guidelines in [Developer_Guidelines.md](file:///E:/Comp/特需/Troll-vs-Troll-main/Troll-vs-Troll-main/Developer_Guidelines.md). If changes are made that violate these guidelines, it would be better not to make them at all, and such changes should be reverted.