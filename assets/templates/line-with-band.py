"""该模板复用 scripts 中的代码，需要与整个 skill 目录一起使用。"""
from pathlib import Path
import sys

skill_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(skill_root / "scripts"))

from render import main

if __name__ == "__main__":
    main()
