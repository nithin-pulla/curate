import 'dart:convert';
import 'package:http/http.dart' as http;
import 'models.dart';

class ApiService {
  // FIXED: Removed 'dart:io' to prevent Web crashes.
  // Since you are testing on Chrome (Web) or iOS Simulator, localhost is correct.
  // Note: If you go back to Android Emulator later, you will need to change this to 'http://10.0.2.2:8000/api/v1'
  final String _baseUrl = 'http://127.0.0.1:8000/api/v1';

  Future<List<MealBundle>> fetchBundles(String userId, String restaurantId) async {
    final url = Uri.parse('$_baseUrl/recommendations');
    
    // Construct Request Body
    final body = jsonEncode({
      "user_id": userId,
      "restaurant_id": restaurantId,
      "context": "dinner" 
    });

    try {
      print('--- API Request ---');
      print('URL: $url');

      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: body,
      );

      if (response.statusCode == 200) {
        print('SUCCESS: Data received');
        final List<dynamic> jsonList = jsonDecode(response.body);
        return jsonList.map((json) => MealBundle.fromJson(json)).toList();
      } else {
        print('ERROR: ${response.body}');
        throw Exception('Failed to load bundles: ${response.statusCode}');
      }
    } catch (e) {
      print('--- Network Error ---');
      print(e);
      throw Exception('Network error: $e');
    }
  }
}