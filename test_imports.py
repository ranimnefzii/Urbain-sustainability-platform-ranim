import subprocess, sys

# Test basic imports first
result = subprocess.run(
    [sys.executable, "-c", 
     "import pydantic; import pydantic_settings; print('OK')"],
    capture_output=True, text=True, timeout=30
)
print("Basic import test:")
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("RC:", result.returncode)
print()

# Now test with a simpler dotenv approach
result2 = subprocess.run(
    [sys.executable, "-c", 
     "from pydantic_settings import BaseSettings; "
     "class Test(BaseSettings): x: str = 'default'; model_config = {'env_file': '.env'}; "
     "t = Test(); print(f'x={t.x}')"],
    capture_output=True, text=True, timeout=30,
    cwd=r'C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend'
)
print("Pydantic Settings test:")
print("STDOUT:", result2.stdout)
print("STDERR:", result2.stderr)
print("RC:", result2.returncode)
