"""
run_tests.py
Corre TODAS las pruebas del proyecto con un solo clic (F5 en Visual Studio).
"""

import sys
import unittest

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover("pruebas", top_level_dir=".")
    resultado = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if resultado.wasSuccessful() else 1)
