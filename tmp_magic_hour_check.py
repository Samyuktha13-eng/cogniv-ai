import magic_hour, pkgutil
print('MODULE', magic_hour)
print('FILE', getattr(magic_hour, '__file__', 'n/a'))
print('PATH', getattr(magic_hour, '__path__', None))
print('DIR', [a for a in dir(magic_hour) if not a.startswith('_')][:100])
print('SUBMODULES', [m.name for m in pkgutil.iter_modules(magic_hour.__path__)][:50])
