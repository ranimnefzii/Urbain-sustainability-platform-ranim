import subprocess, sys

print("Test 1: Just importing the module (not creating Settings)")
result = subprocess.run(
    [sys.executable, "-c", "print('starting'); import app; print('app module imported')"],
    capture_output=True, text=True, timeout=15,
    cwd=r'C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend'
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("RC:", result.returncode)

print("\nTest 2: Test reading the env file directly")
result2 = subprocess.run(
    [sys.executable, "-c", "with open('.env') as f: print(f.read()[:200])"],
    capture_output=True, text=True, timeout=10,
    cwd=r'C:\Users\seifa\Downloads\Urbain-sustainability-project-ranim\backend'
)
print("STDOUT:", result2.stdout)
print("STDERR:", result2.stderr)
