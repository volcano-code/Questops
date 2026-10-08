"""Review-gated, create-only quest application with deterministic reconciliation."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib, json, os, stat
from pathlib import Path
from typing import Any

class ChangeControlError(RuntimeError): pass

def canonical_bytes(draft: dict[str, Any]) -> bytes:
    return (json.dumps(draft,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode("utf-8")

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

@dataclass(frozen=True)
class Approval:
    run_id: str
    draft_sha256: str

    @classmethod
    def for_draft(cls, run_id: str, draft: dict[str, Any]) -> "Approval":
        if not run_id.strip(): raise ChangeControlError("run_id is required")
        return cls(run_id=run_id,draft_sha256=sha256_bytes(canonical_bytes(draft)))

@dataclass(frozen=True)
class ApplyReceipt:
    run_id: str
    draft_sha256: str
    applied_sha256: str
    path: str
    reconciled: bool

def apply_create_only(target: Path, draft: dict[str, Any], approval: Approval) -> ApplyReceipt:
    payload=canonical_bytes(draft)
    digest=sha256_bytes(payload)
    if digest != approval.draft_sha256:
        raise ChangeControlError("draft changed after approval")
    # Resolve the parent only: resolving the leaf follows dangling symlinks.
    target=Path(target.parent.resolve()) / target.name
    target.parent.mkdir(parents=True,exist_ok=True)
    try:
        fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    except FileExistsError as exc:
        raise ChangeControlError("target already exists; use reconcile instead of overwrite") from exc
    try:
        with os.fdopen(fd,"wb") as handle:
            handle.write(payload); handle.flush(); os.fsync(handle.fileno())
    except Exception:
        try: target.unlink()
        except OSError: pass
        raise
    return ApplyReceipt(approval.run_id,digest,digest,str(target),False)

def reconcile(target: Path, approval: Approval) -> ApplyReceipt:
    # Never follow a symlink while reconciling an approved artifact.
    target=Path(target.parent.resolve()) / target.name
    flags=os.O_RDONLY
    if hasattr(os,"O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd=os.open(target,flags)
    except OSError as exc:
        raise ChangeControlError("approved target cannot be opened safely") from exc
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ChangeControlError("approved target is not a regular file")
        with os.fdopen(fd,"rb") as handle:
            fd=-1
            applied=sha256_bytes(handle.read())
    finally:
        if fd >= 0:
            os.close(fd)
    if applied != approval.draft_sha256:
        raise ChangeControlError("existing target does not match approved draft")
    return ApplyReceipt(approval.run_id,approval.draft_sha256,applied,str(target),True)
