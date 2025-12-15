# test.py
"""
🔐 RJUTB Admin - Password Hash Generator
Simple tool to create bcrypt hash for admin password
"""
import bcrypt

print("\n" + "="*60)
print("🔐 RJUTB PASSWORD HASH GENERATOR")
print("="*60)

# Parol kiritish
password = input("\n📝 Parolingizni kiriting: ")

# Hash yaratish
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
hash_str = hashed.decode('utf-8')

# Natija
print("\n" + "="*60)
print(f"✅ Parol:  {password}")
print(f"✅ Hash:   {hash_str}")
print("\n📋 .env ga qo'ying:")
print(f"ADMIN_PASSWORD={hash_str}")
print("="*60 + "\n")