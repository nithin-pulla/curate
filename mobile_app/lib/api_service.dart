import 'dart:convert';
import 'package:http/http.dart' as http;
import 'models.dart';

  // Use build-time configuration: flutter run --dart-define=API_BASE_URL=http://localhost:8000/api/v1
  static const String _baseUrl = String.fromEnvironment('API_BASE_URL', defaultValue: ''); 
  
  // Note: If empty, throw error or handle gracefully in constructor (or just assume user will provide it)

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
  Future<String?> createUser(String name, String email, String preferences, List<String> allergens) async {
    final url = Uri.parse('$_baseUrl/users');
    
    final body = jsonEncode({
      "name": name,
      "email": email,
      "preferences": preferences,
      "allergens": allergens
    });

    try {
      print('--- Create User Request ---');
      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: body,
      );

      if (response.statusCode == 200) {
        final json = jsonDecode(response.body);
        print('SUCCESS: User Created ID: ${json['user_id']}');
        return json['user_id'];
      } else {
        print('ERROR: ${response.body}');
        return null;
      }
    } catch (e) {
      print('Network Error: $e');
      return null;
    }
  }
}