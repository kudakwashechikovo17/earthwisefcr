import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:earthwise_poultry_advisor/main.dart';
import 'package:earthwise_poultry_advisor/models/prediction_response.dart';

void main() {
  group('Earthwise Poultry Advisor App Tests', () {
    // 1. Unit test for response parsing
    test('PredictionResponse parsing from JSON', () {
      final jsonSample = {
        'predicted_fcr': 1.2345,
        'efficiency_category': 'Good — Above average feed efficiency',
        'surviving_birds': 4825.0,
        'expected_live_weight_kg': 9650.0,
        'estimated_feed_required_kg': 11912.92,
        'saleable_meat_kg': 6948.0,
        'estimated_feed_cost_rwf': 5360816.0,
        'total_production_cost_rwf': 9610816.0,
        'estimated_revenue_rwf': 24318000.0,
        'estimated_profit_rwf': 14707184.0,
        'profit_margin_percent': 60.48,
        'cold_storage_utilization_percent': 138.96,
        'delivery_trips': 4,
        'risk_level': 'Low Risk',
        'contract_recommendation': 'Strong candidate — Recommend for contract farming partnership',
        'disclaimer': 'Operational estimates based on predicted FCR.'
      };

      final response = PredictionResponse.fromJson(jsonSample);

      expect(response.predictedFcr, equals(1.2345));
      expect(response.efficiencyCategory, contains('Good'));
      expect(response.survivingBirds, equals(4825.0));
      expect(response.deliveryTrips, equals(4));
      expect(response.riskLevel, equals('Low Risk'));
    });

    // 2. Widget test confirming Predictor Tab navigation and form section title exists
    testWidgets('Predictor tab button and AI predictor form exist', (WidgetTester tester) async {
      await tester.pumpWidget(const EarthwisePoultryApp());
      await tester.pumpAndSettle();

      // Find AI Predictor tab text in BottomNavigationBar
      final predictorTab = find.text('AI Predictor');
      expect(predictorTab, findsOneWidget);

      // Tap on Predictor tab
      await tester.tap(predictorTab);
      await tester.pumpAndSettle(const Duration(milliseconds: 500));

      // Verify section 1 title exists in form
      expect(find.text('1. Flock Performance Variables'), findsOneWidget);
    });

    // 3. Validation test for empty required input in form
    testWidgets('Form validation shows error text when required inputs are empty', (WidgetTester tester) async {
      await tester.pumpWidget(const EarthwisePoultryApp());
      await tester.pumpAndSettle();

      // Tap Predictor tab
      final predictorTab = find.text('AI Predictor');
      await tester.tap(predictorTab);
      await tester.pumpAndSettle(const Duration(milliseconds: 500));

      // Clear the first TextFormField (Harvest Age)
      final firstFormField = find.byType(TextFormField).first;
      await tester.enterText(firstFormField, '');
      await tester.pumpAndSettle();

      // Tap Predict button to trigger validation
      final predictButton = find.widgetWithText(ElevatedButton, 'Predict');
      await tester.ensureVisible(predictButton);
      await tester.tap(predictButton, warnIfMissed: false);
      await tester.pumpAndSettle();

      // Verify validation message is shown
      expect(find.text('Harvest Age (age_days) is required'), findsOneWidget);
    });
  });
}
