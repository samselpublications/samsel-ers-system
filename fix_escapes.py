file_path = r"c:\Users\raghu\samsel1\samsel_ers\samsel-ers-system\samsel_software-fixed (2).html"

with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# Fix double-escaped \\n to proper \n in the three functions
# The issue is that \\\\n appears in the file but should be \\n
count = text.count('\\\\n')
print(f"Found {count} occurrences of double-escaped newlines")

text = text.replace('\\\\n', '\\n')

count2 = text.count('\\\\n')
print(f"After fix: {count2} occurrences remain")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Fixed!")
