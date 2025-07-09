from passlib.context import CryptContext

# Set up password hashing context (same as your FastAPI project)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# The sample password to hash
password = "mySecret123"

# Hash the password twice
hash1 = pwd_context.hash(password)
hash2 = pwd_context.hash(password)

# Display the results
print("Password:", password)
print("Hash 1:", hash1)
print("Hash 2:", hash2)
print("\n✅ Are both hashes same? ->", hash1 == hash2)
