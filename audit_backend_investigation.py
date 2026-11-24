import os
import re

matches = []
for root, _, files in os.walk(r"backend\app"):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()
                found = re.findall(r"(investigat\w+)", content, re.IGNORECASE)
                if found:
                    matches.append((path, set(found)))

print("Investigation references found in backend/app:")
for p, f in matches:
    print(f"  {p}: {f}")
