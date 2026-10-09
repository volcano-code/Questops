import os, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from fastapi.testclient import TestClient
from Agent.api import app

class ApiTests(unittest.TestCase):
    def setUp(self): self.client=TestClient(app)

    def test_health_exposes_no_browser_approval(self):
        body=self.client.get("/api/health").json()
        self.assertEqual("ok",body["status"])
        self.assertFalse(body["approvalInBrowser"])

    def test_fixture_is_explicitly_not_live(self):
        r=self.client.post("/api/runs",json={"intent":"make canonical quest","mode":"fixture"})
        self.assertEqual(200,r.status_code)
        body=r.json()
        self.assertEqual("fixture",body["mode"])
        self.assertFalse(body["liveModel"])
        self.assertIn("not a model call",body["evidence"]["warning"])

    def test_live_requires_explicit_cost_consent(self):
        r=self.client.post("/api/runs",json={"intent":"make canonical quest","mode":"live","allow_model_call":False})
        self.assertEqual(400,r.status_code)

    def test_live_without_server_key_is_unavailable_not_fixture(self):
        old=os.environ.pop("DEEPSEEK_API_KEY",None)
        try:
            r=self.client.post("/api/runs",json={"intent":"make canonical quest","mode":"live","allow_model_call":True})
            self.assertEqual(503,r.status_code)
        finally:
            if old is not None: os.environ["DEEPSEEK_API_KEY"]=old

if __name__=="__main__": unittest.main()
