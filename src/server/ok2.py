from pathlib import Path
import sys

path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))
print(path_root)