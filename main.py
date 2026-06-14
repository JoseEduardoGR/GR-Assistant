#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GR Docs - Generador de documentos con IA (Solo API)
Punto de entrada principal de la aplicación
"""

from colorama import init

# Handles ANSI color codes on Windows automatically, no-op on Linux/macOS
init(autoreset=True)

def main():
    """Función principal que inicia directamente el servidor API."""
    from GR_Docs.server import main as server_main
    server_main()

if __name__ == '__main__':
    main()
