import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class VerificationToolTests(unittest.TestCase):
    def test_pass_without_evidence_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"gate.json"
            result=subprocess.run([
                sys.executable, str(ROOT/"tools"/"emit_verification.py"),
                "--gate","backend","--status","PASS","--output",str(out)
            ],capture_output=True,text=True)
            self.assertNotEqual(0,result.returncode)
            self.assertFalse(out.exists())

    def test_not_run_requires_reason(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"gate.json"
            result=subprocess.run([
                sys.executable, str(ROOT/"tools"/"emit_verification.py"),
                "--gate","unityPlayMode","--status","NOT_RUN","--output",str(out)
            ],capture_output=True,text=True)
            self.assertNotEqual(0,result.returncode)

    def test_merge_promotes_only_supplied_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); fragments=root/"fragments"; fragments.mkdir()
            evidence=root/"backend.log"; evidence.write_text("ok",encoding="utf-8")
            fragment={
                "gate":"backend","status":"PASS","evidence":str(evidence),"reason":None
            }
            (fragments/"backend.json").write_text(json.dumps(fragment),encoding="utf-8")
            output=root/"verification.json"
            subprocess.run([
                sys.executable,str(ROOT/"tools"/"merge_verification.py"),
                "--template",str(ROOT/"verification"/"release-gates.json"),
                "--fragments",str(fragments),"--output",str(output)
            ],check=True)
            merged=json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual("PASS",merged["gates"]["backend"]["status"])
            self.assertEqual("NOT_RUN",merged["gates"]["unityPlayMode"]["status"])

if __name__=="__main__":
    unittest.main()
