import sys

src=sys.argv[1]
dst=sys.argv[2]

with open(src,"r",encoding="utf-8") as f:
    data=f.read()

balance=data.count("{")-data.count("}")

print("brace balance:",balance)

if balance < 0:
    for _ in range(abs(balance)):
        pos=data.rfind("}")
        data=data[:pos]+data[pos+1:]

with open(dst,"w",encoding="utf-8") as f:
    f.write(data)

print("LY FIX DONE")