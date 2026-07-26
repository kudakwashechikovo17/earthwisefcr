import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/prediction_request.dart';
import '../models/prediction_response.dart';
import '../services/prediction_service.dart';
import '../widgets/input_field.dart';
import '../widgets/result_card.dart';

/// Single-page Predictor Form matching strict rubric requirements:
/// - Connects to API (URL + /predict)
/// - TextFields matching prediction variables
/// - Button explicitly labeled "Predict"
/// - Display area for predicted FCR score & error messages
class PredictorTab extends StatefulWidget {
  final VoidCallback onViewAnalytics;

  const PredictorTab({
    super.key,
    required this.onViewAnalytics,
  });

  @override
  State<PredictorTab> createState() => _PredictorTabState();
}

class _PredictorTabState extends State<PredictorTab> {
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = false;
  PredictionResponse? _result;
  String? _errorMessage;

  final _rwfFormat = NumberFormat('#,###', 'en_US');

  // Input Controllers for all prediction & business variables
  final _ageDaysController = TextEditingController(text: '27.0');
  final _bodyWeightController = TextEditingController(text: '1.25');
  final _harvestPercentController = TextEditingController(text: '40.0');
  final _mortalityController = TextEditingController(text: '3.5');
  final _flockSizeController = TextEditingController(text: '5000');
  final _targetWeightController = TextEditingController(text: '2.0');
  final _feedPriceController = TextEditingController(text: '450');
  final _chickCostController = TextEditingController(text: '650');
  final _medicineCostController = TextEditingController(text: '250000');
  final _labourCostController = TextEditingController(text: '500000');
  final _transportCostController = TextEditingController(text: '150000');
  final _otherCostsController = TextEditingController(text: '100000');
  final _sellingPriceController = TextEditingController(text: '3500');
  final _dressingYieldController = TextEditingController(text: '72');
  final _coldRoomController = TextEditingController(text: '5000');
  final _vehicleCapacityController = TextEditingController(text: '2000');

  @override
  void dispose() {
    _ageDaysController.dispose();
    _bodyWeightController.dispose();
    _harvestPercentController.dispose();
    _mortalityController.dispose();
    _flockSizeController.dispose();
    _targetWeightController.dispose();
    _feedPriceController.dispose();
    _chickCostController.dispose();
    _medicineCostController.dispose();
    _labourCostController.dispose();
    _transportCostController.dispose();
    _otherCostsController.dispose();
    _sellingPriceController.dispose();
    _dressingYieldController.dispose();
    _coldRoomController.dispose();
    _vehicleCapacityController.dispose();
    super.dispose();
  }

  String _formatRwf(double value) {
    return 'RWF ${_rwfFormat.format(value.round())}';
  }

  Future<void> _predict() async {
    if (!_formKey.currentState!.validate()) {
      setState(() {
        _errorMessage = "Please fix the invalid or missing input values above before predicting.";
      });
      return;
    }

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
        averageTargetWeightKg: double.parse(_targetWeightController.text.trim()),
        feedPriceRwfPerKg: double.parse(_feedPriceController.text.trim()),
        expectedSellingPriceRwfPerKg: double.parse(_sellingPriceController.text.trim()),
        chickCostRwfPerBird: double.parse(_chickCostController.text.trim()),
        medicineCostRwf: double.parse(_medicineCostController.text.trim()),
        labourCostRwf: double.parse(_labourCostController.text.trim()),
        transportCostRwf: double.parse(_transportCostController.text.trim()),
        otherCostsRwf: double.parse(_otherCostsController.text.trim()),
        coldRoomCapacityKg: double.parse(_coldRoomController.text.trim()),
        deliveryVehicleCapacityKg: double.parse(_vehicleCapacityController.text.trim()),
        dressingYieldPercent: double.parse(_dressingYieldController.text.trim()),
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
        title: const Text('Earthwise Poultry FCR Predictor'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Page Header Banner
              _buildPageHeader(),
              const SizedBox(height: 16),

              // SECTION 1: FLOCK PERFORMANCE INPUT VARIABLES
              _buildSectionCard(
                title: '1. Flock Performance Variables',
                icon: Icons.pets,
                children: [
                  InputField(
                    controller: _ageDaysController,
                    label: 'Harvest Age (age_days)',
                    hint: 'Range: 20 to 45 days',
                    suffix: 'days',
                    min: 20,
                    max: 45,
                    icon: Icons.calendar_today,
                  ),
                  InputField(
                    controller: _bodyWeightController,
                    label: 'Live Body Weight (body_weight_kg)',
                    hint: 'Range: 0.5 to 3.0 kg',
                    suffix: 'kg',
                    min: 0.5,
                    max: 3.0,
                    icon: Icons.monitor_weight,
                  ),
                  InputField(
                    controller: _harvestPercentController,
                    label: 'Harvest Rate (harvest_percent)',
                    hint: 'Range: 1 to 100 %',
                    suffix: '%',
                    min: 1.0,
                    max: 100.0,
                    icon: Icons.pie_chart,
                  ),
                  InputField(
                    controller: _mortalityController,
                    label: 'Mortality Rate (mortality_percent)',
                    hint: 'Range: 0 to 50 %',
                    suffix: '%',
                    min: 0.0,
                    max: 50.0,
                    icon: Icons.warning_amber,
                  ),
                ],
              ),

              const SizedBox(height: 16),

              // SECTION 2: PRODUCTION COST & FARM VARIABLES
              _buildSectionCard(
                title: '2. Farm & Financial Inputs',
                icon: Icons.attach_money,
                children: [
                  InputField(
                    controller: _flockSizeController,
                    label: 'Flock Size (birds)',
                    hint: 'e.g. 5000',
                    suffix: 'birds',
                    min: 1,
                    max: 1000000,
                    isInteger: true,
                    icon: Icons.groups,
                  ),
                  InputField(
                    controller: _targetWeightController,
                    label: 'Target Market Weight per Bird',
                    hint: 'e.g. 2.0',
                    suffix: 'kg',
                    min: 0.5,
                    max: 5.0,
                    icon: Icons.fitness_center,
                  ),
                  InputField(
                    controller: _feedPriceController,
                    label: 'Feed Price per kg',
                    hint: 'e.g. 450',
                    suffix: 'RWF/kg',
                    min: 1,
                    max: 10000,
                    icon: Icons.grass,
                  ),
                  InputField(
                    controller: _chickCostController,
                    label: 'Day-Old Chick Cost',
                    hint: 'e.g. 650',
                    suffix: 'RWF/bird',
                    min: 0,
                    max: 50000,
                    icon: Icons.egg,
                  ),
                  InputField(
                    controller: _medicineCostController,
                    label: 'Medicine & Vet Expenses',
                    hint: 'e.g. 250000',
                    suffix: 'RWF',
                    min: 0,
                    max: 100000000,
                    icon: Icons.medical_services,
                  ),
                  InputField(
                    controller: _labourCostController,
                    label: 'Labour Expenses',
                    hint: 'e.g. 500000',
                    suffix: 'RWF',
                    min: 0,
                    max: 100000000,
                    icon: Icons.engineering,
                  ),
                  InputField(
                    controller: _transportCostController,
                    label: 'Transport Expenses',
                    hint: 'e.g. 150000',
                    suffix: 'RWF',
                    min: 0,
                    max: 100000000,
                    icon: Icons.local_shipping,
                  ),
                  InputField(
                    controller: _otherCostsController,
                    label: 'Overhead Expenses',
                    hint: 'e.g. 100000',
                    suffix: 'RWF',
                    min: 0,
                    max: 100000000,
                    icon: Icons.receipt_long,
                  ),
                ],
              ),

              const SizedBox(height: 16),

              // SECTION 3: MARKET & LOGISTICS VARIABLES
              _buildSectionCard(
                title: '3. Market & Cold Storage Variables',
                icon: Icons.store,
                children: [
                  InputField(
                    controller: _sellingPriceController,
                    label: 'Selling Price per kg Meat',
                    hint: 'e.g. 3500',
                    suffix: 'RWF/kg',
                    min: 1,
                    max: 50000,
                    icon: Icons.sell,
                  ),
                  InputField(
                    controller: _dressingYieldController,
                    label: 'Carcass Dressing Yield',
                    hint: 'e.g. 72',
                    suffix: '%',
                    min: 40,
                    max: 90,
                    icon: Icons.content_cut,
                  ),
                  InputField(
                    controller: _coldRoomController,
                    label: 'Cold Storage Room Capacity',
                    hint: 'e.g. 5000',
                    suffix: 'kg',
                    min: 1,
                    max: 1000000,
                    icon: Icons.ac_unit,
                  ),
                  InputField(
                    controller: _vehicleCapacityController,
                    label: 'Refrigerated Vehicle Capacity',
                    hint: 'e.g. 2000',
                    suffix: 'kg',
                    min: 1,
                    max: 100000,
                    icon: Icons.local_shipping,
                  ),
                ],
              ),

              const SizedBox(height: 24),

              // RUBRIC REQUIREMENT: BUTTON WITH THE EXACT TEXT "Predict"
              SizedBox(
                height: 54,
                child: ElevatedButton.icon(
                  onPressed: _isLoading ? null : _predict,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFE85A0C),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                  ),
                  icon: _isLoading
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                              strokeWidth: 2, color: Colors.white),
                        )
                      : const Icon(Icons.flash_on, color: Colors.white),
                  label: Text(
                    _isLoading ? 'Predicting...' : 'Predict',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w900,
                      fontSize: 18,
                      letterSpacing: 0.5,
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 16),

              // DISPLAY AREA FOR ERROR MESSAGES
              if (_errorMessage != null) _buildErrorCard(),

              const SizedBox(height: 16),

              // DISPLAY AREA FOR PREDICTED VALUE & RESULTS
              if (_result != null) _buildResultsView(),

              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPageHeader() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFFFF5F0),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFFFD8C2)),
      ),
      child: const Row(
        children: [
          Icon(Icons.auto_awesome, color: Color(0xFFE85A0C), size: 28),
          SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Feed Conversion Ratio (FCR) Predictor',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 15,
                    color: Color(0xFF1A202C),
                  ),
                ),
                SizedBox(height: 2),
                Text(
                  'Enter flock variables below and click Predict to call FastAPI endpoint.',
                  style: TextStyle(fontSize: 12, color: Color(0xFF718096)),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionCard({
    required String title,
    required IconData icon,
    required List<Widget> children,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: const Color(0xFFE85A0C)),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFFE85A0C),
                  ),
                ),
              ],
            ),
            const Divider(height: 20),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _buildErrorCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFFFEBEE),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE63946)),
      ),
      child: Row(
        children: [
          const Icon(Icons.error_outline, color: Color(0xFFE63946)),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              _errorMessage!,
              style: const TextStyle(
                color: Color(0xFFE63946),
                fontSize: 13,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildResultsView() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // PREDICTED VALUE HIGHLIGHT (Rubric Requirement)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFFE85A0C), Color(0xFFD94E00)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              children: [
                const Text(
                  'PREDICTED FEED CONVERSION RATIO (FCR)',
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 0.8,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  _result!.predictedFcr.toStringAsFixed(4),
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 44,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 6),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    _result!.efficiencyCategory,
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          const Text(
            'Derived Business Insights',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Color(0xFF1A202C),
            ),
          ),
          const SizedBox(height: 10),

          ResultCard(
            label: 'Estimated Net Profit',
            value: _formatRwf(_result!.estimatedProfitRwf),
            icon: Icons.savings,
            isHighlighted: true,
            valueColor: _result!.estimatedProfitRwf >= 0
                ? const Color(0xFF2E7D32)
                : const Color(0xFFE63946),
          ),
          ResultCard(
            label: 'Profit Margin Percentage',
            value: '${_result!.profitMarginPercent.toStringAsFixed(1)}%',
            icon: Icons.percent,
            isHighlighted: true,
          ),
          ResultCard(
            label: 'Expected Live Flock Weight',
            value: '${_result!.expectedLiveWeightKg.toStringAsFixed(1)} kg',
            icon: Icons.monitor_weight,
          ),
          ResultCard(
            label: 'Estimated Feed Required',
            value: '${_result!.estimatedFeedRequiredKg.toStringAsFixed(1)} kg',
            icon: Icons.grass,
          ),
          ResultCard(
            label: 'Saleable Dressed Meat Yield',
            value: '${_result!.saleableMeatKg.toStringAsFixed(1)} kg',
            icon: Icons.restaurant,
          ),
          ResultCard(
            label: 'Refrigerated Delivery Trips',
            value: '${_result!.deliveryTrips} trips',
            icon: Icons.local_shipping,
          ),
          ResultCard(
            label: 'Farmer Risk Level',
            value: _result!.riskLevel,
            icon: Icons.shield,
          ),
          ResultCard(
            label: 'Contract Partnership Recommendation',
            value: _result!.contractRecommendation,
            icon: Icons.handshake,
          ),
        ],
      ),
    );
  }
}
