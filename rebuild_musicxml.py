from music21 import converter
import sys

src = sys.argv[1]
dst = sys.argv[2]

score = converter.parse(src)

# 重新建立小節
score = score.makeMeasures()

# 移除容易造成 jianpu_ly 問題的元素
for n in score.recurse().notes:
    try:
        n.tie = None
    except:
        pass

score.write("musicxml", fp=dst)

print("Saved:", dst)