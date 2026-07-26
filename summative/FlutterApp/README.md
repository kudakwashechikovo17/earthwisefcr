# Earthwise Poultry Advisor — Flutter Mobile Application

An AI-powered mobile application built with Flutter to predict broiler Feed Conversion Ratio (FCR) and provide real-time decision support for Rwandan agritech and cold-chain operations.

## Features

- **Farm Performance Inputs**: Age, live body weight, harvest percentage, mortality rate.
- **Cost & Farm Details**: Flock size, target weight, feed price, chick cost, medicine, labour, transport, miscellaneous costs.
- **Market & Logistics**: Meat selling price, dressing yield, cold-room capacity, delivery vehicle capacity.
- **Instant Decision Support**:
  - Predicted Feed Conversion Ratio (FCR)
  - Production-efficiency category
  - Expected live flock weight & feed required
  - Financial projections (revenue, total cost, profit, profit margin in RWF)
  - Logistics (cold storage utilization %, required refrigerated delivery trips)
  - Farmer risk assessment & contract-farming recommendation

## Setup & Running Instructions

### Prerequisites
- Flutter SDK (>= 3.0.0)
- Android Studio / Xcode / VS Code with Flutter extension
- An emulator or physical mobile device

### Installation
1. Navigate to the app directory:
   ```bash
   cd summative/FlutterApp
   ```
2. Install dependencies:
   ```bash
   flutter pub get
   ```
3. Configure the API Base URL in `lib/services/prediction_service.dart`:
   ```dart
   // For Android Emulator:
   static const String baseUrl = 'http://10.0.2.2:8000';
   // For Deployed API (Render):
   // static const String baseUrl = 'https://your-api.onrender.com';
   ```
4. Run the app:
   ```bash
   flutter run
   ```

### Running Tests
Execute the unit and widget test suite:
```bash
flutter test
```
Run static analysis:
```bash
flutter analyze
```
