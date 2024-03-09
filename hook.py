import sys
from pathlib import Path
from pprint import pprint

sys.path.append(str(Path(__file__).absolute().parent.parent.parent))
sys.path.append(str(Path(__file__).absolute().parent.parent))
sys.path.append(str(Path(__file__).absolute().parent))
print(f"\n\n模块查找路径：")
pprint(sys.path)

print("\n")
