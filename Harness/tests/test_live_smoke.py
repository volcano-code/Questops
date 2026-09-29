import json, os, subprocess, sys, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from Harness.live_smoke import parse_draft

class LiveSmokeBoundaryTests(unittest.TestCase):
    def canonical(self):
        return json.loads((ROOT/"Schemas"/"canonical-quest.json").read_text(encoding="utf-8"))

    def test_missing_key_is_blocked_before_sdk_or_model(self):
        env=os.environ.copy(); env.pop("DEEPSEEK_API_KEY",None)
        result=subprocess.run([sys.executable,str(ROOT/"Harness"/"live_smoke.py"),"--workspace",str(ROOT)],
                              env=env,capture_output=True,text=True)
        self.assertEqual(2,result.returncode)
        self.assertIn("DEEPSEEK_API_KEY is not configured",result.stderr)

    def test_exact_json_draft_is_accepted(self):
        self.assertEqual(self.canonical(),parse_draft(json.dumps(self.canonical())))

    def test_json_fence_is_tolerated_but_prose_is_not(self):
        raw=json.dumps(self.canonical()); fence=chr(96)*3
        self.assertEqual(self.canonical(),parse_draft(fence+"json\n"+raw+"\n"+fence))
        with self.assertRaises((ValueError,json.JSONDecodeError)):
            parse_draft("Here is the draft: "+raw)

    def test_requirement_drift_from_model_is_rejected(self):
        draft=self.canonical(); draft["goldReward"]=999
        with self.assertRaises(ValueError): parse_draft(json.dumps(draft))

if __name__=="__main__": unittest.main()
