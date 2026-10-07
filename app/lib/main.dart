import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Ponto de partida do app. Por enquanto é só a casca:
// as telas (Início, Materiais, Produções, Estoque) vão nascendo dos testes.
void main() {
  runApp(const ProviderScope(child: AtelieApp()));
}

class AtelieApp extends StatelessWidget {
  const AtelieApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Ateliê',
      theme: ThemeData(useMaterial3: true),
      home: const Scaffold(
        body: Center(child: Text('Ateliê — em construção')),
      ),
    );
  }
}
