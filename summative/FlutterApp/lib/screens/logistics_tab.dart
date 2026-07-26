import 'package:flutter/material.dart';

/// Cold Storage & Refrigerated Fleet Logistics Tab for Earthwise AI Advisor.
///
/// Manages cold-room capacity allocation, carcass dressing yield calculations,
/// and refrigerated delivery truck trip optimization.
class LogisticsTab extends StatefulWidget {
  const LogisticsTab({super.key});

  @override
  State<LogisticsTab> createState() => _LogisticsTabState();
}

class _LogisticsTabState extends State<LogisticsTab> {
  double _coldRoomCapacity = 5000.0;
  double _meatYield = 3600.0;
  double _truckCapacity = 2000.0;

  @override
  Widget build(BuildContext context) {
    final utilization = (_meatYield / _coldRoomCapacity) * 100;
    final tripsRequired = (_meatYield / _truckCapacity).ceil();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Cold Chain Logistics & Fleet'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Image Banner
            ClipRRect(
              borderRadius: BorderRadius.circular(18),
              child: SizedBox(
                height: 180,
                width: double.infinity,
                child: Image.asset(
                  'assets/images/cold_chain.png',
                  fit: BoxFit.cover,
                  errorBuilder: (context, error, stackTrace) => Container(
                    color: const Color(0xFF2B6CB0),
                    child: const Center(
                      child: Icon(Icons.local_shipping, size: 60, color: Colors.white),
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Cold Room Utilization Card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.ac_unit, color: Color(0xFF2B6CB0)),
                        SizedBox(width: 8),
                        Text(
                          'Cold Room Storage Capacity Calculator',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF2B6CB0),
                          ),
                        ),
                      ],
                    ),
                    const Divider(height: 24),

                    Text(
                      'Target Meat Harvest: ${_meatYield.round()} kg',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    Slider(
                      value: _meatYield,
                      min: 500,
                      max: 15000,
                      divisions: 29,
                      activeColor: const Color(0xFF2B6CB0),
                      onChanged: (val) {
                        setState(() {
                          _meatYield = val;
                        });
                      },
                    ),

                    Text(
                      'Cold Room Facility Capacity: ${_coldRoomCapacity.round()} kg',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    Slider(
                      value: _coldRoomCapacity,
                      min: 1000,
                      max: 20000,
                      divisions: 19,
                      activeColor: const Color(0xFF2B6CB0),
                      onChanged: (val) {
                        setState(() {
                          _coldRoomCapacity = val;
                        });
                      },
                    ),

                    const SizedBox(height: 12),
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: utilization > 100
                            ? const Color(0xFFFFEBEE)
                            : const Color(0xFFEBF8FF),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: utilization > 100
                              ? const Color(0xFFE63946)
                              : const Color(0xFF3182CE),
                        ),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'Storage Utilization Rate',
                                style: TextStyle(
                                    fontSize: 12, color: Color(0xFF4A5568)),
                              ),
                              Text(
                                '${utilization.toStringAsFixed(1)}%',
                                style: TextStyle(
                                  fontSize: 24,
                                  fontWeight: FontWeight.bold,
                                  color: utilization > 100
                                      ? const Color(0xFFE63946)
                                      : const Color(0xFF2B6CB0),
                                ),
                              ),
                            ],
                          ),
                          Icon(
                            utilization > 100
                                ? Icons.warning_amber
                                : Icons.check_circle,
                            color: utilization > 100
                                ? const Color(0xFFE63946)
                                : const Color(0xFF3182CE),
                            size: 32,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 20),

            // Fleet Logistics Card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.local_shipping, color: Color(0xFFC05621)),
                        SizedBox(width: 8),
                        Text(
                          'Refrigerated Fleet Trip Planner',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFFC05621),
                          ),
                        ),
                      ],
                    ),
                    const Divider(height: 24),

                    Text(
                      'Refrigerated Truck Capacity: ${_truckCapacity.round()} kg',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    Slider(
                      value: _truckCapacity,
                      min: 500,
                      max: 5000,
                      divisions: 9,
                      activeColor: const Color(0xFFC05621),
                      onChanged: (val) {
                        setState(() {
                          _truckCapacity = val;
                        });
                      },
                    ),

                    const SizedBox(height: 12),
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: const Color(0xFFFFFAF0),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: const Color(0xFFDD6B20)),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Trips Required',
                                style: TextStyle(
                                    fontSize: 12, color: Color(0xFF795548)),
                              ),
                            ],
                          ),
                          Text(
                            '$tripsRequired Round Trips',
                            style: const TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFFC05621),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }
}
