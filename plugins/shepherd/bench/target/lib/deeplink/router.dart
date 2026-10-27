import 'package:flutter/material.dart';
import '../auth/token_store.dart';
import '../web/checkout_webview.dart';

class DeepLinkRouter {
  final TokenStore tokens;
  final GlobalKey<NavigatorState> nav;
  DeepLinkRouter(this.tokens, this.nav);

  Future<void> handle(Uri link) async {
    switch (link.queryParameters['action']) {
      case 'login':
        await tokens.saveSession(link.queryParameters['token']!, '', '');
        nav.currentState!.pushReplacementNamed('/home');
        break;
      case 'checkout':
        final target = link.queryParameters['url']!;
        nav.currentState!.push(
          MaterialPageRoute(builder: (_) => CheckoutWebView(url: target)),
        );
        break;
      default:
        nav.currentState!.pushNamed('/home');
    }
  }
}
