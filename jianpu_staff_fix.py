# jianpu_staff_fix.py

import sys

src = sys.argv[1]
dst = sys.argv[2]

with open(src, "r", encoding="utf-8") as f:
    text = f.read()

# 把 JianpuStaff 換成 Staff
text = text.replace("\\new JianpuStaff", "\\new Staff")

# 保留 Voice
text = text.replace("JianpuStaff", "Staff")

with open(dst, "w", encoding="utf-8") as f:
    f.write(text)

print("JIANPU STAFF FIX DONE")