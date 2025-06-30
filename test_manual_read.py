import os

manual_path = os.path.abspath("docs/user_manual.md")
print(f"Looking for file at: {manual_path}")

if os.path.exists(manual_path):
    print("✅ File exists!")
    with open(manual_path, "r", encoding="utf-8") as f:
        content = f.read()
        print("📏 File length:", len(content))
        print("🔍 First few lines:\n", content[:300])
else:
    print("❌ File does not exist.")
