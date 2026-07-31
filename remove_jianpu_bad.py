from lxml import etree

src = "outputs/vocals_final.musicxml"
dst = "outputs/vocals_nobad.musicxml"

tree = etree.parse(src)
root = tree.getroot()

# 移除可能產生 note-mod 的元素
for tag in [
    "lyric",
    "ornaments",
    "articulations",
    "technical",
    "dynamics"
]:
    for e in root.xpath(f".//{tag}"):
        parent = e.getparent()
        if parent is not None:
            parent.remove(e)

tree.write(
    dst,
    encoding="UTF-8",
    xml_declaration=True
)

print("saved:", dst)