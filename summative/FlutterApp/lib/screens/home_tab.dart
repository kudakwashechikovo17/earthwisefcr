import 'package:flutter/material.dart';

/// Earthwise Butcher Shop & Poultry AI Advisor Home Dashboard.
///
/// Styled strictly after the official Earthwise Butcher Shop visual branding:
/// Vibrant Orange header, location tag (KG316 Kimironko), search bar,
/// category pills, and "Today's Kigali Market Prices & FCR Profitability Link".
class HomeTab extends StatefulWidget {
  final VoidCallback onStartPrediction;

  const HomeTab({
    super.key,
    required this.onStartPrediction,
  });

  @override
  State<HomeTab> createState() => _HomeTabState();
}

class _HomeTabState extends State<HomeTab> {
  int _selectedCategoryIndex = 0;
  final _searchController = TextEditingController();

  final List<String> _categories = [
    '🐔 Market Prices & Cuts',
    '🌾 Feed Price & FCR Link',
    '🥩 Carcass Dressing Yield',
    '❄️ Cold Room Storage',
    '🤝 Contract Farmer Risk',
  ];

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF7F8FA),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 1. EARTHWISE BRAND HEADER BANNER
            _buildEarthwiseBrandHeader(),

            // 2. SEARCH BAR & CATEGORIES
            _buildSearchBarAndCategories(),

            const SizedBox(height: 16),

            // 3. TODAY'S KIGALI MARKET PRICES & FCR LINK SECTION
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              "Today's Kigali Market Prices",
                              style: TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.w900,
                                color: Color(0xFF1A202C),
                                letterSpacing: -0.5,
                              ),
                            ),
                            SizedBox(height: 2),
                            Text(
                              'Real-time rates & how FCR drives farm profit',
                              style: TextStyle(
                                fontSize: 12,
                                color: Color(0xFF718096),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: const Color(0xFFE8F5E9),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: const Color(0xFFA5D6A7)),
                        ),
                        child: const Row(
                          children: [
                            Icon(Icons.circle, color: Color(0xFF2E7D32), size: 8),
                            SizedBox(width: 6),
                            Text(
                              'Live Rates',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF2E7D32),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Market Price Cards Linked to FCR
                  _buildMarketPriceLinkGrid(context),

                  const SizedBox(height: 24),

                  // FEATURED AI PREDICTION CALL TO ACTION CARD
                  _buildFeaturedPredictionBanner(context),

                  const SizedBox(height: 24),

                  // VALUE CHAIN DECISION MODULES
                  const Text(
                    'Value Chain Decision Modules',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF1A202C),
                    ),
                  ),
                  const SizedBox(height: 12),
                  _buildValueChainModules(context),

                  const SizedBox(height: 32),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEarthwiseBrandHeader() {
    return Container(
      width: double.infinity,
      color: const Color(0xFFE85A0C), // Vibrant Earthwise Orange
      padding: EdgeInsets.only(
        top: MediaQuery.of(context).padding.top + 12,
        bottom: 16,
        left: 16,
        right: 16,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              // Logo + Brand Name
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Icon(
                      Icons.agriculture_rounded,
                      color: Color(0xFFE85A0C),
                      size: 24,
                    ),
                  ),
                  const SizedBox(width: 12),
                  const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'EARTHWISE',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w900,
                          fontSize: 20,
                          letterSpacing: 1.2,
                        ),
                      ),
                      Text(
                        'BUTCHER SHOP & AI ADVISOR',
                        style: TextStyle(
                          color: Colors.white70,
                          fontWeight: FontWeight.bold,
                          fontSize: 10,
                          letterSpacing: 1.0,
                        ),
                      ),
                    ],
                  ),
                ],
              ),

              // Location Badge (KG316 Kimironko)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.black.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.location_on, color: Colors.white, size: 14),
                    SizedBox(width: 4),
                    Text(
                      'KG316 Kimironko, Kigali',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSearchBarAndCategories() {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // Search Input Field
          TextField(
            controller: _searchController,
            decoration: InputDecoration(
              hintText: 'Search cut prices, feed rates, target FCR, cold room...',
              prefixIcon: const Icon(Icons.search, color: Color(0xFFA0AEC0)),
              fillColor: const Color(0xFFF7F8FA),
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
              ),
            ),
          ),

          const SizedBox(height: 14),

          // Horizontal Category Selector Chips
          SizedBox(
            height: 38,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: _categories.length,
              itemBuilder: (context, index) {
                final isSelected = _selectedCategoryIndex == index;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ChoiceChip(
                    label: Text(_categories[index]),
                    selected: isSelected,
                    onSelected: (selected) {
                      setState(() {
                        _selectedCategoryIndex = index;
                      });
                    },
                    selectedColor: const Color(0xFFE85A0C),
                    backgroundColor: const Color(0xFFF7F8FA),
                    labelStyle: TextStyle(
                      color: isSelected ? Colors.white : const Color(0xFF4A5568),
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
                      fontSize: 12,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(20),
                      side: BorderSide(
                        color: isSelected
                            ? const Color(0xFFE85A0C)
                            : const Color(0xFFE2E8F0),
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMarketPriceLinkGrid(BuildContext context) {
    final marketItems = [
      {
        'title': 'Prime Chicken Quarter Legs',
        'market_price': '4,500 RWF / kg',
        'fcr_target': 'Target FCR ≤ 1.23',
        'link_explanation': 'High-demand retail cut. Maintaining FCR ≤ 1.23 ensures feed cost stays under 1,600 RWF/kg meat, securing 44% margin at 4,500 RWF.',
        'image': 'assets/images/chicken.png',
        'tag': 'Retail Cut',
        'tag_color': const Color(0xFFE85A0C),
      },
      {
        'title': 'Whole Dressed Broiler Carcass',
        'market_price': '3,500 RWF / kg',
        'fcr_target': 'Dressing Yield 72%',
        'link_explanation': '72% carcass dressing yield means 1.25kg live bird gives 0.90kg saleable meat. Optimal FCR keeps total cost under 2,200 RWF/kg.',
        'image': 'assets/images/hero.png',
        'tag': 'Whole Bird',
        'tag_color': const Color(0xFF2B6CB0),
      },
      {
        'title': 'Commercial Poultry Feed Rate',
        'market_price': '450 RWF / kg',
        'fcr_target': '~65% Total Production Cost',
        'link_explanation': 'Feed price dictates your breakeven FCR. If feed rises to 500 RWF/kg, your target FCR must drop to 1.18 to maintain net profit.',
        'image': 'assets/images/cold_chain.png',
        'tag': 'Feed Index',
        'tag_color': const Color(0xFF2E7D32),
      },
    ];

    return SizedBox(
      height: 340,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        itemCount: marketItems.length,
        itemBuilder: (context, index) {
          final item = marketItems[index];
          return Container(
            width: 280,
            margin: const EdgeInsets.only(right: 16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFE2E8F0)),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.04),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Image Header with Price & Tag Overlay
                Stack(
                  children: [
                    ClipRRect(
                      borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
                      child: SizedBox(
                        height: 140,
                        width: double.infinity,
                        child: Image.asset(
                          item['image']! as String,
                          fit: BoxFit.cover,
                          errorBuilder: (context, error, stackTrace) => Container(
                            color: const Color(0xFFFFF5F0),
                            child: const Center(
                              child: Icon(Icons.shopping_bag, size: 50, color: Color(0xFFE85A0C)),
                            ),
                          ),
                        ),
                      ),
                    ),
                    Positioned(
                      top: 10,
                      left: 10,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: item['tag_color'] as Color,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          item['tag']! as String,
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 11,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),

                // Card Body: Price & FCR Link Explanation
                Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        item['title']! as String,
                        style: const TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF1A202C),
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 6),
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              item['market_price']! as String,
                              style: const TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w900,
                                color: Color(0xFFE85A0C),
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          const SizedBox(width: 4),
                          Flexible(
                            child: Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: const Color(0xFFE8F5E9),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Text(
                                item['fcr_target']! as String,
                                style: const TextStyle(
                                  fontSize: 9,
                                  fontWeight: FontWeight.bold,
                                  color: Color(0xFF2E7D32),
                                ),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: const Color(0xFFF7F8FA),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: const Color(0xFFEDF2F7)),
                        ),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Icon(Icons.link, size: 14, color: Color(0xFFE85A0C)),
                            const SizedBox(width: 6),
                            Expanded(
                              child: Text(
                                item['link_explanation']! as String,
                                style: const TextStyle(
                                  fontSize: 11,
                                  color: Color(0xFF4A5568),
                                  height: 1.3,
                                ),
                                maxLines: 4,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildFeaturedPredictionBanner(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFFE85A0C), Color(0xFFD94E00)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFFE85A0C).withValues(alpha: 0.35),
            blurRadius: 15,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.auto_awesome, color: Colors.white, size: 28),
              SizedBox(width: 10),
              Text(
                'Earthwise AI FCR Predictor',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w900,
                  fontSize: 18,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          const Text(
            'Link your flock age, live weight, feed price & market cut rates to calculate exact net profit in RWF.',
            style: TextStyle(color: Colors.white70, fontSize: 13, height: 1.4),
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            height: 48,
            child: ElevatedButton.icon(
              onPressed: widget.onStartPrediction,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.white,
                foregroundColor: const Color(0xFFE85A0C),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              icon: const Icon(Icons.flash_on, color: Color(0xFFE85A0C)),
              label: const Text(
                'Calculate Your Flock Profitability',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildValueChainModules(BuildContext context) {
    return Column(
      children: [
        _buildModuleItem(
          title: 'Feed Conversion Ratio (FCR) Machine Learning Model',
          subtitle: 'SGD Regressor trained on commercial flock observations',
          icon: Icons.speed,
          color: const Color(0xFFE85A0C),
          onTap: widget.onStartPrediction,
        ),
        const SizedBox(height: 10),
        _buildModuleItem(
          title: 'Refrigerated Cold Storage Planner',
          subtitle: 'Calculate cold room space & distribution fleet trips',
          icon: Icons.ac_unit,
          color: const Color(0xFF2B6CB0),
          onTap: () {},
        ),
        const SizedBox(height: 10),
        _buildModuleItem(
          title: 'Farmer Feasibility & Risk Assessor',
          subtitle: 'Assess contract farming candidate risk level in Kigali',
          icon: Icons.shield,
          color: const Color(0xFF2E7D32),
          onTap: () {},
        ),
      ],
    );
  }

  Widget _buildModuleItem({
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: ListTile(
        onTap: onTap,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.12),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(icon, color: color, size: 24),
        ),
        title: Text(
          title,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 14,
            color: Color(0xFF1A202C),
          ),
        ),
        subtitle: Text(
          subtitle,
          style: const TextStyle(fontSize: 11, color: Color(0xFF718096)),
        ),
        trailing: const Icon(Icons.arrow_forward_ios, size: 14, color: Color(0xFFA0AEC0)),
      ),
    );
  }
}
