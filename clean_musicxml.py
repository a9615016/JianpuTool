# ==========================
# rebuild measures V29
# split overflow notes
# ==========================

print("rebuild measures V29")


for part in root.xpath(".//m:part", namespaces=NS):

    measures = part.xpath("./m:measure", namespaces=NS)

    carry_note = None
    carry_duration = 0


    for measure in measures:

        total = 0

        notes = measure.xpath("./m:note", namespaces=NS)


        # 加入上一小節切過來的音
        if carry_note is not None:

            new_note = etree.fromstring(
                etree.tostring(carry_note)
            )

            dur = new_note.find(
                "m:duration",
                NS
            )

            dur.text = str(carry_duration)

            measure.insert(
                0,
                new_note
            )

            carry_note = None
            carry_duration = 0



        for note in list(notes):

            dur = note.find(
                "m:duration",
                NS
            )

            if dur is None:
                continue


            value = int(dur.text)


            if total + value <= BAR_LENGTH:

                total += value
                continue



            # 超過小節
            remain = BAR_LENGTH - total


            if remain > 0:

                print(
                    "SPLIT NOTE",
                    measure.get("number"),
                    value,
                    "into",
                    remain,
                    value-remain
                )


                # 本小節部分
                dur.text = str(remain)


                # 下一小節部分
                carry_note = note
                carry_duration = value-remain


                total = BAR_LENGTH


            else:

                carry_note = note
                carry_duration = value



            measure.remove(note)



            break



        print(
            "Measure",
            measure.get("number"),
            total
        )



        # 不足補休止

        if total < BAR_LENGTH:

            missing = BAR_LENGTH-total

            rest = etree.Element(
                "{%s}note" % NS["m"]
            )

            etree.SubElement(
                rest,
                "{%s}rest" % NS["m"]
            )

            d = etree.SubElement(
                rest,
                "{%s}duration" % NS["m"]
            )

            d.text = str(missing)


            measure.append(rest)