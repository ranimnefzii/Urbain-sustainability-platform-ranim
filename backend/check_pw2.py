from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

hash = "$2b$12$4ySuwxe6KgwZwS/HFfWXIO9q.ScZ0Rhm0PFtO32OclvWG.QulqVuG"
print(f"Admin123!: {pwd_context.verify('Admin123!', hash)}")
print(f"TestPass123!: {pwd_context.verify('TestPass123!', hash)}")
