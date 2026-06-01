import subprocess
import sys

# Test that settings load correctly
result = subprocess.run(
    [sys.executable, "-c", 
     "import os; os.chdir(r'C:\\Users\\seifa\\Downloads\\Urbain-sustainability-project-ranim\\backend'); "
     "from app.core.config import settings; "
     "print(f'DB_URL={settings.DATABASE_URL}'); "
     "print(f'SECRET={settings.SECRET_KEY}')"],
    capture_output=True, text=True, timeout=15
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("RC:", result.returncode)
