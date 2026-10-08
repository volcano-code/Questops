import json, sys, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Agent"))
from change_control import Approval, ChangeControlError, apply_create_only, reconcile

class ChangeControlTests(unittest.TestCase):
    def draft(self):
        return json.loads((ROOT/"Schemas"/"canonical-quest.json").read_text(encoding="utf-8"))

    def test_apply_requires_exact_approved_draft(self):
        draft=self.draft(); approval=Approval.for_draft("run-1",draft)
        changed=dict(draft); changed["goldReward"]=999
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ChangeControlError):
                apply_create_only(Path(td)/"quest.json",changed,approval)

    def test_create_only_never_overwrites(self):
        draft=self.draft(); approval=Approval.for_draft("run-1",draft)
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/"quest.json"
            apply_create_only(target,draft,approval)
            with self.assertRaises(ChangeControlError):
                apply_create_only(target,draft,approval)

    def test_lost_receipt_recovers_by_reconcile_without_second_write(self):
        draft=self.draft(); approval=Approval.for_draft("run-1",draft)
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/"quest.json"
            first=apply_create_only(target,draft,approval)
            before=target.read_bytes()
            recovered=reconcile(target,approval)
            self.assertTrue(recovered.reconciled)
            self.assertEqual(first.applied_sha256,recovered.applied_sha256)
            self.assertEqual(before,target.read_bytes())

    def test_reconcile_rejects_tampering(self):
        draft=self.draft(); approval=Approval.for_draft("run-1",draft)
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/"quest.json"
            apply_create_only(target,draft,approval)
            target.write_text('{"tampered":true}\n',encoding="utf-8")
            with self.assertRaises(ChangeControlError):
                reconcile(target,approval)


    def test_create_only_rejects_dangling_symlink_without_writing_outside(self):
        draft=self.draft(); approval=Approval.for_draft("run-1",draft)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); outside=root/"outside.json"; link=root/"quest.json"
            try:
                link.symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation unavailable")
            with self.assertRaises(ChangeControlError):
                apply_create_only(link,draft,approval)
            self.assertFalse(outside.exists())

    def test_reconcile_rejects_symlink_even_when_content_matches(self):
        draft=self.draft(); approval=Approval.for_draft("run-1",draft)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); real=root/"real.json"; link=root/"quest.json"
            apply_create_only(real,draft,approval)
            try:
                link.symlink_to(real)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation unavailable")
            with self.assertRaises(ChangeControlError):
                reconcile(link,approval)

if __name__=="__main__": unittest.main()
