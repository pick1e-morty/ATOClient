import sys
from pathlib import Path
from pprint import pprint

if not sys.stdout:

    class FakeStdOut:
        def __init__(self, filename="sys.log"):
            # self.log = open(filename, "a")
            pass

        def write(self, message):
            # 我这里把原本打印到控制台的内容，写到了sys.log文件中，也可以不写直接pass
            # self.log.write(message)
            pass

        def flush(self):
            pass

        def isatty(self):
            return True

    sys.stdout = FakeStdOut()

sys.path.append(str(Path(__file__).absolute().parent.parent.parent))
sys.path.append(str(Path(__file__).absolute().parent.parent))
sys.path.append(str(Path(__file__).absolute().parent))
print(f"\n\n模块查找路径：")
pprint(sys.path)

print("\n")
