from music21 import converter
import sys

src = sys.argv[1]
dst = sys.argv[2]

score = converter.parse(src)

for n in score.recurse().notes:
    # 移除所有可能造成 jianpu_ly 問題的標記
    n.lyric = None
    n.expressions = []
    n.articulations = []

    if hasattr(n, "tie"):
        n.tie = None

score.write("musicxml", fp=dst)

print("clean vocal xml done")