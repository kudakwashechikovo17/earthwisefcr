/// Data model for the prediction API request.
///
/// Contains model features (for FCR prediction) and business inputs
/// (for financial and logistics calculations).
class PredictionRequest {
  // Model Features
  final double ageDays;
  final double bodyWeightKg;
  final double harvestPercent;
  final double mortalityPercent;

  // Business Inputs
  final int flockSize;
  final double averageTargetWeightKg;
  final double feedPriceRwfPerKg;
  final double expectedSellingPriceRwfPerKg;
  final double chickCostRwfPerBird;
  final double medicineCostRwf;
  final double labourCostRwf;
  final double transportCostRwf;
  final double otherCostsRwf;
  final double coldRoomCapacityKg;
  final double deliveryVehicleCapacityKg;
  final double dressingYieldPercent;

  PredictionRequest({
    required this.ageDays,
    required this.bodyWeightKg,
    required this.harvestPercent,
    required this.mortalityPercent,
    required this.flockSize,
    required this.averageTargetWeightKg,
    required this.feedPriceRwfPerKg,
    required this.expectedSellingPriceRwfPerKg,
    required this.chickCostRwfPerBird,
    required this.medicineCostRwf,
    required this.labourCostRwf,
    required this.transportCostRwf,
    required this.otherCostsRwf,
    required this.coldRoomCapacityKg,
    required this.deliveryVehicleCapacityKg,
    required this.dressingYieldPercent,
  });

  /// Converts this request to a JSON-compatible map for the API.
  Map<String, dynamic> toJson() {
    return {
      'age_days': ageDays,
      'body_weight_kg': bodyWeightKg,
      'harvest_percent': harvestPercent,
      'mortality_percent': mortalityPercent,
      'flock_size': flockSize,
      'average_target_weight_kg': averageTargetWeightKg,
      'feed_price_rwf_per_kg': feedPriceRwfPerKg,
      'expected_selling_price_rwf_per_kg': expectedSellingPriceRwfPerKg,
      'chick_cost_rwf_per_bird': chickCostRwfPerBird,
      'medicine_cost_rwf': medicineCostRwf,
      'labour_cost_rwf': labourCostRwf,
      'transport_cost_rwf': transportCostRwf,
      'other_costs_rwf': otherCostsRwf,
      'cold_room_capacity_kg': coldRoomCapacityKg,
      'delivery_vehicle_capacity_kg': deliveryVehicleCapacityKg,
      'dressing_yield_percent': dressingYieldPercent,
    };
  }
}
