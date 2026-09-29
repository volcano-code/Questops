import sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from run_unity_tests import parse_results

class UnityResultTests(unittest.TestCase):
    def test_parses_real_nunit_shape(self):
        result=parse_results(ROOT/"tools"/"tests"/"fixtures"/"unity-pass.xml")
        self.assertEqual({"total":1,"passed":1,"failed":0,"skipped":0},result)

if __name__=="__main__": unittest.main()
