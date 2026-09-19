import sys
import types
import unittest

magic_hour = types.ModuleType('magic_hour')

class _DummyClient:
    def __init__(self, *args, **kwargs):
        pass

magic_hour.Client = _DummyClient
sys.modules['magic_hour'] = magic_hour

suite = unittest.defaultTestLoader.loadTestsFromName('backend.test_reference_grounded_generation')
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
