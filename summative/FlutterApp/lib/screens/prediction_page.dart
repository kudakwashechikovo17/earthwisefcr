import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/prediction_request.dart';
import '../models/prediction_response.dart';
import '../services/prediction_service.dart';
import '../widgets/input_field.dart';
import '../widgets/result_card.dart';

/// Main prediction page for the Earthwise Poultry Advisor.
///
/// Contains grouped input sections (Farm Performance, Costs, Market & Logistics),
/// a Predict button, progress indicator, error display, and result cards.
class PredictionPage extends StatefulWidget {
  const PredictionPage({super.key});

  @override
  State<PredictionPage> createState() => _PredictionPageState();
}

class _PredictionPageState extends State<PredictionPage> {
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = false;
  PredictionResponse? _result;
  String? _errorMessage;

  // RWF currency formatter
  final _rwfFormat = NumberFormat('#,###', 'en_US');

  // ============================================================
  // Text Controllers — Model Features
  // ============================================================
  final _ageDaysController = TextEditingController(text: '27.0');
  final _bodyWeightController = TextEditingController(text: '1.25');
  final _harvestPercentController = TextEditingController(text: '40.0');
  final _mortalityController = TextEditingController(text: '3.5');

  // ============================================================
  // Text Controllers — Business Inputs
  // ============================================================
  final _flockSizeController = TextEditingController(text: '5000');
  final _targetWeightController = TextEditingController(text: '2.0');
  final _feedPriceController = TextEditingController(text: '450');
  final _sellingPriceController = TextEditingController(text: '3500');
  final _chickCostController = TextEditingController(text: '650');
  final _medicineCostController = TextEditingController(text: '250000');
  final _labourCostController = TextEditingController(text: '500000');
  final _transportCostController = TextEditingController(text: '150000');
  final _otherCostsController = TextEditingController(text: '100000');
  final _coldRoomController = TextEditingController(text: '5000');
  final _vehicleCapacityController = TextEditingController(text: '2000');
  final _dressingYieldController = TextEditingController(text: '72');

  @override
  void dispose() {
    _ageDaysController.dispose();
    _bodyWeightController.dispose();
    _harvestPercentController.dispose();
    _mortalityController.dispose();
    _flockSizeController.dispose();
    _targetWeightController.dispose();
    _feedPriceController.dispose();
    _sellingPriceController.dispose();
    _chickCostController.dispose();
    _medicineCostController.dispose();
    _labourCostController.dispose();
    _transportCostController.dispose();
    _otherCostsController.dispose();
    _coldRoomController.dispose();
    _vehicleCapacityController.dispose();
    _dressingYieldController.dispose();
    super.dispose();
  }

  /// Format a number as RWF currency.
  String _formatRwf(double value) {
    return 'RWF ${_rwfFormat.format(value.round())}';
  }

  /// Send prediction request to the API.
  Future<void> _predict() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _result = null;
    });

    try {
      final request = PredictionRequest(
        ageDays: double.parse(_ageDaysController.text.trim()),
        bodyWeightKg: double.parse(_bodyWeightController.text.trim()),
        harvestPercent: double.parse(_harvestPercentController.text.trim()),
        mortalityPercent: double.parse(_mortalityController.text.trim()),
        flockSize: int.parse(_flockSizeController.text.trim()),
        averageTargetWeightKg:
            double.parse(_targetWeightController.text.trim()),
        feedPriceRwfPerKg: double.parse(_feedPriceController.text.trim()),
        expectedSellingPriceRwfPerKg:
            double.parse(_sellingPriceController.text.trim()),
        chickCostRwfPerBird: double.parse(_chickCostController.text.trim()),
        medicineCostRwf: double.parse(_medicineCostController.text.trim()),
        labourCostRwf: double.parse(_labourCostController.text.trim()),
        transportCostRwf: double.parse(_transportCostController.text.trim()),
        otherCostsRwf: double.parse(_otherCostsController.text.trim()),
        coldRoomCapacityKg: double.parse(_coldRoomController.text.trim()),
        deliveryVehicleCapacityKg:
            double.parse(_vehicleCapacityController.text.trim()),
        dressingYieldPercent:
            double.parse(_dressingYieldController.text.trim()),
      );

      final response = await PredictionService.predict(request);

      setState(() {
        _result = response;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString().replaceFirst('Exception: ', '');
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Earthwise Poultry Advisor'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Header
              const Card(
                color: Color(0xFFE8F5E9),
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    children: [
                      Icon(Icons.agriculture, size: 36, color: Color(0xFF2E7D32)),
                      SizedBox(height: 8),
                      Text(
                        'Feed Conversion Ratio Predictor',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF2E7D32),
                        ),
                      ),
                      SizedBox(height: 4),
                      Text(
                        'Enter flock and cost data to predict FCR and get business insights',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontSize: 13,
                          color: Color(0xFF616161),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // ============================================================
              // SECTION A: Farm Performance
              // ============================================================
              _buildSectionHeader('A. Farm Performance', Icons.pets),
              InputField(
                controller: _ageDaysController,
                label: 'Age at Harvest',
                hint: 'e.g. 27.0',
                suffix: 'days',
                min: 20,
                max: 45,
                icon: Icons.calendar_today,
              ),
              InputField(
                controller: _bodyWeightController,
                label: 'Average Body Weight',
                hint: 'e.g. 1.25',
                suffix: 'kg',
                min: 0.5,
                max: 3.0,
                icon: Icons.monitor_weight,
              ),
              InputField(
                controller: _harvestPercentController,
                label: 'Harvest Percentage',
                hint: 'e.g. 40.0',
                suffix: '%',
                min: 1.0,
                max: 100.0,
                icon: Icons.pie_chart,
              ),
              InputField(
                controller: _mortalityController,
                label: 'Mortality Rate',
                hint: 'e.g. 3.5',
                suffix: '%',
                min: 0.0,
                max: 50.0,
                icon: Icons.warning_amber,
              ),
              const SizedBox(height: 16),

              // ============================================================
              // SECTION B: Farm & Cost Information
              // ============================================================
              _buildSectionHeader(
                  'B. Farm & Cost Information', Icons.attach_money),
              InputField(
                controller: _flockSizeController,
                label: 'Flock Size',
                hint: 'e.g. 5000',
                suffix: 'birds',
                min: 1,
                max: 1000000,
                isInteger: true,
                icon: Icons.groups,
              ),
              InputField(
                controller: _targetWeightController,
                label: 'Target Weight per Bird',
                hint: 'e.g. 2.0',
                suffix: 'kg',
                min: 0.5,
                max: 5.0,
                icon: Icons.fitness_center,
              ),
              InputField(
                controller: _feedPriceController,
                label: 'Feed Price',
                hint: 'e.g. 450',
                suffix: 'RWF/kg',
                min: 1,
                max: 10000,
                icon: Icons.grass,
              ),
              InputField(
                controller: _chickCostController,
                label: 'Chick Cost',
                hint: 'e.g. 650',
                suffix: 'RWF/bird',
                min: 0,
                max: 50000,
                icon: Icons.egg,
              ),
              InputField(
                controller: _medicineCostController,
                label: 'Medicine Cost',
                hint: 'e.g. 250000',
                suffix: 'RWF',
                min: 0,
                max: 100000000,
                icon: Icons.medical_services,
              ),
              InputField(
                controller: _labourCostController,
                label: 'Labour Cost',
                hint: 'e.g. 500000',
                suffix: 'RWF',
                min: 0,
                max: 100000000,
                icon: Icons.engineering,
              ),
              InputField(
                controller: _transportCostController,
                label: 'Transport Cost',
                hint: 'e.g. 150000',
                suffix: 'RWF',
                min: 0,
                max: 100000000,
                icon: Icons.local_shipping,
              ),
              InputField(
                controller: _otherCostsController,
                label: 'Other Costs',
                hint: 'e.g. 100000',
                suffix: 'RWF',
                min: 0,
                max: 100000000,
                icon: Icons.receipt_long,
              ),
              const SizedBox(height: 16),

              // ============================================================
              // SECTION C: Market & Logistics
              // ============================================================
              _buildSectionHeader('C. Market & Logistics', Icons.store),
              InputField(
                controller: _sellingPriceController,
                label: 'Selling Price',
                hint: 'e.g. 3500',
                suffix: 'RWF/kg',
                min: 1,
                max: 50000,
                icon: Icons.sell,
              ),
              InputField(
                controller: _dressingYieldController,
                label: 'Dressing Yield',
                hint: 'e.g. 72',
                suffix: '%',
                min: 40,
                max: 90,
                icon: Icons.content_cut,
              ),
              InputField(
                controller: _coldRoomController,
                label: 'Cold Room Capacity',
                hint: 'e.g. 5000',
                suffix: 'kg',
                min: 1,
                max: 1000000,
                icon: Icons.ac_unit,
              ),
              InputField(
                controller: _vehicleCapacityController,
                label: 'Vehicle Capacity',
                hint: 'e.g. 2000',
                suffix: 'kg',
                min: 1,
                max: 100000,
                icon: Icons.local_shipping,
              ),
              const SizedBox(height: 24),

              // ============================================================
              // PREDICT BUTTON
              // ============================================================
              SizedBox(
                height: 54,
                child: ElevatedButton.icon(
                  onPressed: _isLoading ? null : _predict,
                  icon: _isLoading
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Icon(Icons.analytics),
                  label: Text(_isLoading ? 'Predicting...' : 'Predict'),
                ),
              ),
              const SizedBox(height: 16),

              // ============================================================
              // ERROR DISPLAY
              // ============================================================
              if (_errorMessage != null)
                Card(
                  color: const Color(0xFFFFEBEE),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Icon(Icons.error_outline,
                            color: Color(0xFFD32F2F)),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            _errorMessage!,
                            style: const TextStyle(
                              color: Color(0xFFD32F2F),
                              fontSize: 14,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

              // ============================================================
              // RESULTS DISPLAY
              // ============================================================
              if (_result != null) ...[
                const SizedBox(height: 8),
                _buildSectionHeader('Prediction Results', Icons.insights),

                // Primary: FCR and Efficiency
                ResultCard(
                  label: 'Predicted Feed Conversion Ratio (FCR)',
                  value: _result!.predictedFcr.toStringAsFixed(4),
                  icon: Icons.speed,
                  isHighlighted: true,
                ),
                ResultCard(
                  label: 'Feed Efficiency Category',
                  value: _result!.efficiencyCategory,
                  icon: Icons.category,
                  isHighlighted: true,
                ),

                const SizedBox(height: 8),
                _buildSectionHeader('Production Estimates', Icons.factory),
                ResultCard(
                  label: 'Surviving Birds',
                  value: _rwfFormat.format(_result!.survivingBirds.round()),
                  icon: Icons.pets,
                ),
                ResultCard(
                  label: 'Expected Live Flock Weight',
                  value: '${_result!.expectedLiveWeightKg.toStringAsFixed(1)} kg',
                  icon: Icons.monitor_weight,
                ),
                ResultCard(
                  label: 'Estimated Feed Required',
                  value:
                      '${_result!.estimatedFeedRequiredKg.toStringAsFixed(1)} kg',
                  icon: Icons.grass,
                ),
                ResultCard(
                  label: 'Saleable Meat',
                  value: '${_result!.saleableMeatKg.toStringAsFixed(1)} kg',
                  icon: Icons.restaurant,
                ),

                const SizedBox(height: 8),
                _buildSectionHeader('Financial Estimates', Icons.account_balance),
                ResultCard(
                  label: 'Estimated Feed Cost',
                  value: _formatRwf(_result!.estimatedFeedCostRwf),
                  icon: Icons.grass,
                ),
                ResultCard(
                  label: 'Total Production Cost',
                  value: _formatRwf(_result!.totalProductionCostRwf),
                  icon: Icons.receipt,
                ),
                ResultCard(
                  label: 'Estimated Revenue',
                  value: _formatRwf(_result!.estimatedRevenueRwf),
                  icon: Icons.trending_up,
                ),
                ResultCard(
                  label: 'Estimated Profit',
                  value: _formatRwf(_result!.estimatedProfitRwf),
                  icon: Icons.savings,
                  valueColor: _result!.estimatedProfitRwf >= 0
                      ? const Color(0xFF2E7D32)
                      : const Color(0xFFD32F2F),
                ),
                ResultCard(
                  label: 'Profit Margin',
                  value: '${_result!.profitMarginPercent.toStringAsFixed(1)}%',
                  icon: Icons.percent,
                  valueColor: _result!.profitMarginPercent >= 0
                      ? const Color(0xFF2E7D32)
                      : const Color(0xFFD32F2F),
                ),

                const SizedBox(height: 8),
                _buildSectionHeader('Logistics & Risk', Icons.local_shipping),
                ResultCard(
                  label: 'Cold Storage Utilization',
                  value:
                      '${_result!.coldStorageUtilizationPercent.toStringAsFixed(1)}%',
                  icon: Icons.ac_unit,
                  valueColor:
                      _result!.coldStorageUtilizationPercent > 100
                          ? const Color(0xFFD32F2F)
                          : null,
                ),
                ResultCard(
                  label: 'Delivery Trips Required',
                  value: '${_result!.deliveryTrips}',
                  icon: Icons.local_shipping,
                ),
                ResultCard(
                  label: 'Farmer Risk Level',
                  value: _result!.riskLevel,
                  icon: Icons.shield,
                  valueColor: _getRiskColor(_result!.riskLevel),
                ),
                ResultCard(
                  label: 'Contract Recommendation',
                  value: _result!.contractRecommendation,
                  icon: Icons.handshake,
                ),

                // Disclaimer
                const SizedBox(height: 8),
                Card(
                  color: const Color(0xFFFFF8E1),
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Icon(Icons.info_outline,
                            color: Color(0xFFF9A825), size: 18),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            _result!.disclaimer,
                            style: const TextStyle(
                              fontSize: 11,
                              color: Color(0xFF795548),
                              fontStyle: FontStyle.italic,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),
              ],
            ],
          ),
        ),
      ),
    );
  }

  /// Build a styled section header.
  Widget _buildSectionHeader(String title, IconData icon) {
    return Padding(
      padding: const EdgeInsets.only(top: 8, bottom: 8),
      child: Row(
        children: [
          Icon(icon, color: const Color(0xFF2E7D32), size: 22),
          const SizedBox(width: 8),
          Text(
            title,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Color(0xFF2E7D32),
            ),
          ),
        ],
      ),
    );
  }

  /// Get color for risk level display.
  Color _getRiskColor(String riskLevel) {
    switch (riskLevel) {
      case 'Minimal Risk':
        return const Color(0xFF2E7D32);
      case 'Low Risk':
        return const Color(0xFF558B2F);
      case 'Medium Risk':
        return const Color(0xFFF57F17);
      case 'High Risk':
        return const Color(0xFFD32F2F);
      default:
        return const Color(0xFF616161);
    }
  }
}
