/// Data model for the prediction API response.
///
/// Contains the predicted FCR, all derived business outputs,
/// risk assessment, and contract recommendation.
class PredictionResponse {
  // Model output
  final double predictedFcr;
  final String efficiencyCategory;

  // Production estimates
  final double survivingBirds;
  final double expectedLiveWeightKg;
  final double estimatedFeedRequiredKg;
  final double saleableMeatKg;

  // Financial estimates (RWF)
  final double estimatedFeedCostRwf;
  final double totalProductionCostRwf;
  final double estimatedRevenueRwf;
  final double estimatedProfitRwf;
  final double profitMarginPercent;

  // Logistics
  final double coldStorageUtilizationPercent;
  final int deliveryTrips;

  // Risk and recommendations
  final String riskLevel;
  final String contractRecommendation;

  // Disclaimer
  final String disclaimer;

  PredictionResponse({
    required this.predictedFcr,
    required this.efficiencyCategory,
    required this.survivingBirds,
    required this.expectedLiveWeightKg,
    required this.estimatedFeedRequiredKg,
    required this.saleableMeatKg,
    required this.estimatedFeedCostRwf,
    required this.totalProductionCostRwf,
    required this.estimatedRevenueRwf,
    required this.estimatedProfitRwf,
    required this.profitMarginPercent,
    required this.coldStorageUtilizationPercent,
    required this.deliveryTrips,
    required this.riskLevel,
    required this.contractRecommendation,
    required this.disclaimer,
  });

  /// Parse a JSON response map into a [PredictionResponse].
  factory PredictionResponse.fromJson(Map<String, dynamic> json) {
    return PredictionResponse(
      predictedFcr: (json['predicted_fcr'] as num).toDouble(),
      efficiencyCategory: json['efficiency_category'] as String,
      survivingBirds: (json['surviving_birds'] as num).toDouble(),
      expectedLiveWeightKg: (json['expected_live_weight_kg'] as num).toDouble(),
      estimatedFeedRequiredKg:
          (json['estimated_feed_required_kg'] as num).toDouble(),
      saleableMeatKg: (json['saleable_meat_kg'] as num).toDouble(),
      estimatedFeedCostRwf:
          (json['estimated_feed_cost_rwf'] as num).toDouble(),
      totalProductionCostRwf:
          (json['total_production_cost_rwf'] as num).toDouble(),
      estimatedRevenueRwf:
          (json['estimated_revenue_rwf'] as num).toDouble(),
      estimatedProfitRwf:
          (json['estimated_profit_rwf'] as num).toDouble(),
      profitMarginPercent:
          (json['profit_margin_percent'] as num).toDouble(),
      coldStorageUtilizationPercent:
          (json['cold_storage_utilization_percent'] as num).toDouble(),
      deliveryTrips: (json['delivery_trips'] as num).toInt(),
      riskLevel: json['risk_level'] as String,
      contractRecommendation: json['contract_recommendation'] as String,
      disclaimer: json['disclaimer'] as String,
    );
  }
}
