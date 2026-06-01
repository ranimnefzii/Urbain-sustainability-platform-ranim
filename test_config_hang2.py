import subprocess, sys

print("Test 3: Directly construct Settings")
result = subprocess.run(
    [sys.executable, "-c", 
     "from pydantic_settings import BaseSettings; "
     "class T(BaseSettings): x: str = 'default'; model_config = {'env_file': '.env'}; "
     "t = T(); print('OK', t.x)"],
    capture_output=True, text=True, timeout=15,
    cwd=r'C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend'
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("RC:", result.returncode)

print("\nTest 4: Settings with extra='allow'")
result2 = subprocess.run(
    [sys.executable, "-c", 
     "from pydantic_settings import BaseSettings; "
     "class T(BaseSettings): x: str = 'default'; model_config = {'env_file': '.env', 'extra': 'allow'}; "
     "t = T(); print('OK', t.x)"],
    capture_output=True, text=True, timeout=15,
    cwd=r'C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend'
)
print("STDOUT:", result2.stdout)
print("STDERR:", result2.stderr)
print("RC:", result2.returncode)
