import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

class TokenStore {
  static const _secure = FlutterSecureStorage();

  Future<void> saveSession(String accessToken, String refreshToken, String cardLast4) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', accessToken);
    await prefs.setString('saved_card', cardLast4);
    await _secure.write(key: 'refresh_token', value: refreshToken);
  }

  Future<String?> accessToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token');
  }

  Future<void> saveDeviceLabel(String label) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('device_label', label);
  }
}
