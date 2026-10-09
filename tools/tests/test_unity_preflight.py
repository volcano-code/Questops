import sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from unity_preflight import project_version

class UnityPreflightTests(unittest.TestCase):
    def test_repository_version_is_frozen(self):
        self.assertEqual("6000.3.23f1",project_version(ROOT))

    def test_missing_version_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/"ProjectSettings").mkdir()
            (root/"ProjectSettings"/"ProjectVersion.txt").write_text("invalid\n",encoding="utf-8")
            with self.assertRaises(ValueError): project_version(root)

if __name__=="__main__": unittest.main()
