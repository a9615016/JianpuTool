import os
import re


JIANPU_FILE = "/usr/local/lib/python3.10/site-packages/jianpu_ly/__init__.py"


def patch_jianpu():

    if not os.path.exists(JIANPU_FILE):
        print("jianpu_ly not found")
        return


    print("Patching jianpu_ly...")


    with open(
        JIANPU_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        data = f.read()


    old = """
if self.barPos > self.barLength:
"""


    new = """
# PATCHED BY JianpuTool
# allow timing overflow caused by MusicXML conversion

if self.barPos > self.barLength + 0.25:
"""


    if old in data:

        data = data.replace(
            old,
            new
        )

        with open(
            JIANPU_FILE,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(data)

        print("jianpu_ly patched OK")

    else:

        print(
            "patch target not found"
        )


if __name__ == "__main__":
    patch_jianpu()