import 'package:flutter/material.dart';

/// Analytics & Model Performance Tab for Earthwise AI Poultry Advisor.
///
/// Visualizes model benchmark metrics, FCR performance categories,
/// feature importance, and machine learning model comparison tables.
class AnalyticsTab extends StatelessWidget {
  const AnalyticsTab({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Model Analytics & Insights'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header Banner
            _buildHeaderBanner(),
            const SizedBox(height: 20),

            // FCR Benchmark Scale
            const Text(
              'FCR Performance Industry Benchmark',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1B4332),
              ),
            ),
            const SizedBox(height: 8),
            _buildBenchmarkScale(),

            const SizedBox(height: 24),

            // Model Performance Comparison Table Card
            const Text(
              'Machine Learning Model Comparison',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1B4332),
              ),
            ),
            const SizedBox(height: 8),
            _buildModelComparisonCard(),

            const SizedBox(height: 24),

            // Feature Importance Breakdown
            const Text(
              'Feature Importance Breakdown (Random Forest)',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1B4332),
              ),
            ),
            const SizedBox(height: 8),
            _buildFeatureImportanceCard(),

            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  Widget _buildHeaderBanner() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF1B4332), Color(0xFF2D6A4F)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(18),
      ),
      child: const Row(
        children: [
          Icon(Icons.analytics, color: Color(0xFFD4AF37), size: 40),
          SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Deployed Model: SGD Regressor v1.0',
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                SizedBox(height: 4),
                Text(
                  'Lowest Test RMSE: 0.0806 | Test R²: 0.4028',
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 13,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBenchmarkScale() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _buildBenchmarkItem('Excellent (< 1.10)', 'Outstanding feed efficiency', const Color(0xFF2E7D32)),
            const Divider(),
            _buildBenchmarkItem('Good (1.10 - 1.25)', 'Above average commercial performance', const Color(0xFF558B2F)),
            const Divider(),
            _buildBenchmarkItem('Average (1.25 - 1.40)', 'Typical intensive broiler cycle', const Color(0xFFF57F17)),
            const Divider(),
            _buildBenchmarkItem('Below Average (> 1.40)', 'High feed cost risk — review flock health', const Color(0xFFD32F2F)),
          ],
        ),
      ),
    );
  }

  Widget _buildBenchmarkItem(String title, String subtitle, Color color) {
    return Row(
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: color,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                  color: color,
                ),
              ),
              Text(
                subtitle,
                style: const TextStyle(fontSize: 11, color: Color(0xFF718096)),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildModelComparisonCard() {
    final models = [
      {'name': 'SGD Regressor (Best)', 'rmse': '0.0806', 'mae': '0.0630', 'r2': '0.4028', 'best': true},
      {'name': 'Linear Regression (OLS)', 'rmse': '0.0817', 'mae': '0.0634', 'r2': '0.3866', 'best': false},
      {'name': 'Random Forest', 'rmse': '0.0856', 'mae': '0.0633', 'r2': '0.3258', 'best': false},
      {'name': 'Decision Tree', 'rmse': '0.0995', 'mae': '0.0765', 'r2': '0.0890', 'best': false},
    ];

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: models.map((m) {
            final isBest = m['best'] == true;
            return Container(
              margin: const EdgeInsets.symmetric(vertical: 6),
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: isBest ? const Color(0xFFE8F5E9) : const Color(0xFFF8F9FA),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: isBest ? const Color(0xFF2E7D32) : const Color(0xFFE2E8F0),
                ),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          m['name'].toString(),
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                            color: isBest ? const Color(0xFF1B4332) : const Color(0xFF2D3748),
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          'Test MAE: ${m['mae']} | R²: ${m['r2']}',
                          style: const TextStyle(fontSize: 11, color: Color(0xFF718096)),
                        ),
                      ],
                    ),
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        'RMSE ${m['rmse']}',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 14,
                          color: isBest ? const Color(0xFF2E7D32) : const Color(0xFF4A5568),
                        ),
                      ),
                      if (isBest)
                        const Text(
                          'Selected Model',
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF2E7D32),
                          ),
                        ),
                    ],
                  ),
                ],
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildFeatureImportanceCard() {
    final features = [
      {'name': 'harvest_percent', 'pct': 0.2421},
      {'name': 'age_days', 'pct': 0.1882},
      {'name': 'body_weight_kg', 'pct': 0.1183},
      {'name': 'weight_gain_per_day', 'pct': 0.1145},
    ];

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: features.map((f) {
            final double pct = f['pct'] as double;
            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        f['name'].toString(),
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                          color: Color(0xFF2D3748),
                        ),
                      ),
                      Text(
                        '${(pct * 100).toStringAsFixed(1)}%',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                          color: Color(0xFF1B4332),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(6),
                    child: LinearProgressIndicator(
                      value: pct / 0.3, // Scale for display
                      backgroundColor: const Color(0xFFEDF2F7),
                      color: const Color(0xFF1B4332),
                      minHeight: 8,
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
        ),
      ),
    );
  }
}
