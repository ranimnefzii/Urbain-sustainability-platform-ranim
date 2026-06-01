import subprocess, sys, time

# Write and execute a test script that imports the real config
test_script = r"""
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
"""

with open(r'C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\test_timed_import.py', 'w') as f:
    f.write(test_script)

print("Running timed import test...")
result = subprocess.run(
    [sys.executable, r'C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\test_timed_import.py'],
    capture_output=True, text=True, timeout=120
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("RC:", result.returncode)
