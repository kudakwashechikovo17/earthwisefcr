import 'package:flutter/material.dart';

/// Styled card for displaying a prediction result item.
///
/// Shows a label, value, and optional icon with consistent styling.
class ResultCard extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color? valueColor;
  final bool isHighlighted;

  const ResultCard({
    super.key,
    required this.label,
    required this.value,
    required this.icon,
    this.valueColor,
    this.isHighlighted = false,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: isHighlighted ? const Color(0xFFE8F5E9) : Colors.white,
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: isHighlighted
                    ? const Color(0x262E7D32)
                    : const Color(0xFFF5F5F0),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(
                icon,
                color: isHighlighted
                    ? const Color(0xFF2E7D32)
                    : const Color(0xFF757575),
                size: 22,
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label,
                    style: const TextStyle(
                      fontSize: 13,
                      color: Color(0xFF757575),
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 3),
                  Text(
                    value,
                    style: TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                      color: valueColor ?? const Color(0xFF212121),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
