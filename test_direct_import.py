import sys
import time

t0 = time.time()
sys.path.insert(0, r'C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend')
print('Starting import of app.core.config...', flush=True)
try:
    import app.core.config
    s = app.core.config.settings
    t1 = time.time()
    print(f'Import took {t1-t0:.1f}s', flush=True)
    print(f'DB: {s.DATABASE_URL}', flush=True)
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}', flush=True)
