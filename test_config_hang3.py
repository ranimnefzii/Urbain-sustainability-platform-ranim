import subprocess, sys

code = r"""
from pydantic_settings import BaseSettings
class T(BaseSettings):
    x: str = 'default'
    model_config = {'env_file': '.env'}
t = T()
print('OK', t.x)
"""

print("Test 3: Directly construct Settings")
result = subprocess.run(
    [sys.executable, "-c", code],
    capture_output=True, text=True, timeout=15,
    cwd=r'C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend'
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("RC:", result.returncode)

code2 = r"""
from pydantic_settings import BaseSettings
class T(BaseSettings):
    x: str = 'default'
    model_config = {'env_file': '.env', 'extra': 'allow'}
t = T()
print('OK', t.x)
"""
print("\nTest 4: Settings with extra='allow'")
result2 = subprocess.run(
    [sys.executable, "-c", code2],
    capture_output=True, text=True, timeout=15,
    cwd=r'C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend'
)
print("STDOUT:", result2.stdout)
print("STDERR:", result2.stderr)
print("RC:", result2.returncode)

# Test 5: Settings with the actual env file and all fields
code3 = r"""
from pydantic_settings import BaseSettings
from typing import List
class T(BaseSettings):
    DATABASE_URL: str = "default"
    SECRET_KEY: str = "default"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    model_config = {'env_file': '.env', 'extra': 'allow'}
t = T()
print('DB:', t.DATABASE_URL[:30])
print('ORIGINS:', t.ALLOWED_ORIGINS)
"""
print("\nTest 5: Full Settings simulation")
result3 = subprocess.run(
    [sys.executable, "-c", code3],
    capture_output=True, text=True, timeout=15,
    cwd=r'C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend'
)
print("STDOUT:", result3.stdout)
print("STDERR:", result3.stderr)
print("RC:", result3.returncode)
