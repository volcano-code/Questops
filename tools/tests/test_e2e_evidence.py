import sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from verify_e2e import verify

class E2EEvidenceTests(unittest.TestCase):
    def evidence(self):
        sha="a"*64; commit="c"*40
        harness={"liveModel":True,"mode":"live","requiredTools":["questops_read_project_contract","questops_read_authoring_skill"],"commitSha":commit,"draftSha256":sha}
        approval={"approved":True,"executionId":"exec-1","draftSha256":sha}
        receipt={"executionId":"exec-1","draft_sha256":sha,"applied_sha256":sha}
        unity={"commitSha":commit,"canonicalArtifactSha256":sha,"runs":[
            {"platform":"EditMode","processExitCode":0,"total":1,"failed":0},
            {"platform":"PlayMode","processExitCode":0,"total":1,"failed":0},
        ]}
        return harness,approval,receipt,unity,commit

    def test_complete_chain_passes(self):
        self.assertEqual([],verify(*self.evidence()))

    def test_fixture_harness_cannot_pass(self):
        args=list(self.evidence()); args[0]=dict(args[0],liveModel=False,mode="mock")
        self.assertTrue(verify(*args))

    def test_unity_must_consume_same_applied_hash(self):
        args=list(self.evidence()); args[3]=dict(args[3],canonicalArtifactSha256="b"*64)
        self.assertIn("Unity did not execute the applied artifact",verify(*args))

    def test_playmode_zero_tests_cannot_pass(self):
        args=list(self.evidence()); args[3]=dict(args[3],runs=[
            {"platform":"EditMode","processExitCode":0,"total":1,"failed":0},
            {"platform":"PlayMode","processExitCode":0,"total":0,"failed":0},
        ])
        self.assertIn("Unity PlayMode did not pass",verify(*args))

if __name__=="__main__": unittest.main()
