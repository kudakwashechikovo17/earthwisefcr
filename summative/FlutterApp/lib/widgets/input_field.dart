import 'package:flutter/material.dart';

/// Reusable input field widget with label, hint, validation, and numeric keyboard.
///
/// Used across the prediction page for consistent styling and validation.
class InputField extends StatelessWidget {
  final TextEditingController controller;
  final String label;
  final String hint;
  final String? suffix;
  final bool isRequired;
  final double? min;
  final double? max;
  final bool isInteger;
  final IconData? icon;

  const InputField({
    super.key,
    required this.controller,
    required this.label,
    required this.hint,
    this.suffix,
    this.isRequired = true,
    this.min,
    this.max,
    this.isInteger = false,
    this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: TextFormField(
        controller: controller,
        keyboardType: TextInputType.numberWithOptions(decimal: !isInteger),
        decoration: InputDecoration(
          labelText: label,
          hintText: hint,
          suffixText: suffix,
          prefixIcon: icon != null ? Icon(icon, size: 20) : null,
          errorMaxLines: 2,
        ),
        validator: (value) {
          if (isRequired && (value == null || value.trim().isEmpty)) {
            return '$label is required';
          }
          if (value != null && value.trim().isNotEmpty) {
            final number = double.tryParse(value.trim());
            if (number == null) {
              return 'Enter a valid number';
            }
            if (isInteger && number != number.roundToDouble()) {
              return 'Enter a whole number';
            }
            if (min != null && number < min!) {
              return '$label must be at least $min';
            }
            if (max != null && number > max!) {
              return '$label must be at most $max';
            }
          }
          return null;
        },
      ),
    );
  }
}
