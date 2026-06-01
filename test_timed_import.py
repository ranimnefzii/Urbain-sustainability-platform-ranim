
import time, sys
sys.path.insert(0, r'C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend')
t0 = time.time()
print('Starting import...', flush=True)
try:
    import app.core.config
    s = app.core.config.settings
    t1 = time.time()
    print(f'Import took {t1-t0:.1f}s', flush=True)
    print(f'DB: {s.DATABASE_URL[:30]}', flush=True)
    print(f'SECRET: {s.SECRET_KEY[:10]}', flush=True)
except Exception as e:
    print(f'Error: {e}', flush=True)
