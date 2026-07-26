import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../models/prediction_request.dart';
import '../models/prediction_response.dart';

/// Service class for communicating with the Earthwise FCR Prediction API.
///
/// Configurable base URL supports:
/// - Android emulator: http://10.0.2.2:8000
/// - Physical device on same network: http://<your-ip>:8000
/// - Deployed Render URL: https://your-app.onrender.com
class PredictionService {
  /// Dynamic base URL selection based on platform and production availability
  static String get baseUrl {
    // Check if production environment flag is set or fallback gracefully
    const bool isProduction = bool.fromEnvironment('dart.vm.product');
    if (isProduction) {
      return 'https://earthwise-fcr-api.onrender.com';
    }
    // If running on web or non-Android platform (Windows, macOS, Linux), use localhost
    if (kIsWeb || !Platform.isAndroid) {
      return 'http://127.0.0.1:8000';
    }
    // Android emulator maps host localhost to 10.0.2.2
    return 'http://10.0.2.2:8000';
  }

  /// Timeout duration for API requests.
  static const Duration timeout = Duration(seconds: 30);

  /// Send a prediction request to the API.
  ///
  /// Returns a [PredictionResponse] on success.
  /// Throws descriptive exceptions for various error conditions.
  static Future<PredictionResponse> predict(PredictionRequest request) async {
    final url = Uri.parse('$baseUrl/predict');

    try {
      final response = await http
          .post(
            url,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode(request.toJson()),
          )
          .timeout(timeout);

      if (response.statusCode == 200) {
        final jsonBody = jsonDecode(response.body) as Map<String, dynamic>;
        return PredictionResponse.fromJson(jsonBody);
      } else if (response.statusCode == 422) {
        // Pydantic validation error
        final errorBody = jsonDecode(response.body);
        final detail = errorBody['detail'];
        if (detail is List) {
          // Pydantic returns a list of validation errors
          final messages = detail
              .map((e) => '${e['loc']?.last ?? 'field'}: ${e['msg']}')
              .join('\n');
          throw Exception('Validation error:\n$messages');
        } else {
          throw Exception('Validation error: $detail');
        }
      } else if (response.statusCode == 503) {
        throw Exception(
            'Model not available. The server model may not be loaded.');
      } else if (response.statusCode == 500) {
        final errorBody = jsonDecode(response.body);
        throw Exception(
            'Server error: ${errorBody['detail'] ?? 'Unknown error'}');
      } else {
        throw Exception(
            'Unexpected error (HTTP ${response.statusCode}): ${response.body}');
      }
    } on SocketException {
      throw Exception(
          'No internet connection or server unavailable.\n'
          'Check that the API server is running at $baseUrl');
    } on http.ClientException {
      throw Exception(
          'Could not connect to the server.\n'
          'Check your network connection and server URL.');
    } on FormatException {
      throw Exception('Invalid response from server (malformed JSON).');
    }
  }
}
