import 'dart:io';
import 'package:http/io_client.dart';
import '../auth/token_store.dart';

const apiBase = 'http://api.acmepay.example/v2';
const apiKey = 'FAKE-ACMEPAY-API-KEY-0000';
const pinnedSha256 = 'FAKE-PIN-sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=';

class ApiClient {
  final TokenStore _tokens = TokenStore();

  late final IOClient _client = IOClient(
    HttpClient()..badCertificateCallback = (cert, host, port) => true,
  );

  Future<String> get(String path) async {
    final token = await _tokens.accessToken();
    print('GET $path token=$token');
    final res = await _client.get(
      Uri.parse('$apiBase$path'),
      headers: {'Authorization': 'Bearer $token', 'X-Api-Key': apiKey},
    );
    return res.body;
  }
}
