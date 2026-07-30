import sys

src=sys.argv[1]
dst=sys.argv[2]

data=open(src,encoding="utf8").read()

start=data.find('\\new JianpuStaff')

second=data.find('\\new JianpuStaff',start+1)

if second!=-1:
    data=data[:second]


# 補最後結尾
data=data.rstrip()

if not data.endswith("}"):
    data += "\n}"

open(dst,"w",encoding="utf8").write(data)

print("FIRST JIANPU STAFF EXTRACT DONE")