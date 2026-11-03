"""Run with: python python_warmup.py. No Flask server is needed.

Read the matching Python pages in the Word tutorial before changing a line.
"""

# A. Variables refer to values. No Java/C type declaration is written here.
title = "  Prepare project proposal  "
done = False
print("A title:", title.strip())
print("A done:", done)

# B. A dictionary stores values under keys. Here braces contain data.
payload = {"title": title, "done": done}
print("B title key:", payload["title"].strip())
print("B done key exists:", "done" in payload)
print("B done value:", payload["done"])

# C. Four spaces show which statements belong to an if block.
if "done" in payload:
    print("C supplied value:", payload["done"])
print("C after the if")

# D. def defines a function; return gives its result to the caller.
def clean_title(value):
    return value.strip()


result = clean_title("  Prepare slides  ")
print("D result:", result)

# E. Named arguments choose a parameter explicitly.
def title_required(partial=False):
    return not partial


print("E default mode:", title_required())
print("E partial mode:", title_required(partial=True))

# F. A for loop visits each key; a list can collect allowed field names.
allowed_fields = ["title", "done"]
for key in payload:
    if key in allowed_fields:
        print("F allowed key:", key)

# Try A: use done = True, run again, then restore False.
# Try B: add outer spaces to the argument of clean_title and run again.
# Try C: move the C supplied-value print to the left by four spaces.
# Read the if block and explain which print is conditional; then undo the edit.
