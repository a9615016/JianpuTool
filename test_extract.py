from extract_melody import extract_melody


input_xml = "test.musicxml"
output_xml = "melody.musicxml"


extract_melody(
    input_xml,
    output_xml
)


print("完成:", output_xml)