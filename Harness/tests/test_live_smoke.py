import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

class LiveSmokeBoundaryTests(unittest.TestCase):
    def test_missing_key_is_blocked_before_sdk_or_model(self):
        env=os.environ.copy()
        env.pop("DEEPSEEK_API_KEY",None)
        result=subprocess.run(
            [sys.executable,str(ROOT/"Harness"/"live_smoke.py"),"--workspace",str(ROOT)],
            env=env,capture_output=True,text=True,
        )
        self.assertEqual(2,result.returncode)
        self.assertIn("DEEPSEEK_API_KEY is not configured",result.stderr)

if __name__=="__main__":
    unittest.main()
