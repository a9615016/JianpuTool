import sys

src = sys.argv[1]
dst = sys.argv[2]

text = open(src, encoding="utf8").read()

balance = 0
out = []

for c in text:

    if c == "{":
        balance += 1
        out.append(c)

    elif c == "}":

        if balance > 0:
            balance -= 1
            out.append(c)

        else:
            # 移除多餘 }
            continue

    else:
        out.append(c)


# 補不足的 {
while balance > 0:
    out.append("}")
    balance -= 1


open(dst,"w",encoding="utf8").write("".join(out))

print("LY BALANCE FIX DONE")