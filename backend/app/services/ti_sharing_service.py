"""
TRUSTLENS AI - Threat Intelligence Sharing Service (STIX 2.1 & MISP)
Provides:
- STIX 2.1 Bundle validation & interoperability checks
- MISP Core Format Event export & schema validation
- Strict PII / private-IP scrubbing (never exposes private user data in exports)
- Authorized import validation & audit logging to MongoDB `audit_logs`
"""

import ipaddress
import re
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

from backend.app.database.collections import get_audit_collection

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b")
PHONE_RE = re.compile(r"(?:\+?91[\-\s]?)?[6-9]\d{9}\b")
STIX_UUID_RE = re.compile(r"^[a-z0-9\-]+--[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

TRUSTLENS_ORG_UUID = str(uuid.uuid5(uuid.NAMESPACE_URL, "trustlens-ai-misp-org"))


def is_private_or_pii(value: str, kind: str = "") -> bool:
    """Returns True if value contains PII (email/phone) or a private/loopback IP."""
    v = str(value).strip()
    if kind in ("phone", "email"):
        return True
    if EMAIL_RE.search(v) or PHONE_RE.search(v):
        return True
    try:
        ip_obj = ipaddress.ip_address(v)
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_reserved:
            return True
    except ValueError:
        pass
    return False


def validate_stix_21_bundle(bundle: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validates a STIX 2.1 Bundle against core STIX 2.1 schema & relationship integrity."""
    errors: List[str] = []
    if not isinstance(bundle, dict) or bundle.get("type") != "bundle":
        errors.append("Root object must have type='bundle'.")
        return False, errors
    if not STIX_UUID_RE.match(str(bundle.get("id", ""))):
        errors.append("Bundle 'id' must match 'bundle--<uuid>'.")

    objs = bundle.get("objects")
    if not isinstance(objs, list) or len(objs) == 0:
        errors.append("Bundle 'objects' must be a non-empty list.")
        return False, errors

    obj_ids = {o.get("id") for o in objs if isinstance(o, dict) and o.get("id")}
    for idx, obj in enumerate(objs):
        if not isinstance(obj, dict):
            errors.append(f"Object[{idx}] is not a JSON object.")
            continue
        otype = obj.get("type")
        oid = str(obj.get("id", ""))
        if not otype or not STIX_UUID_RE.match(oid):
            errors.append(f"Object[{idx}] invalid type/id: {otype} / {oid}")
        if otype not in ("url", "domain-name", "ipv4-addr", "ipv6-addr", "file"):
            if obj.get("spec_version") != "2.1":
                errors.append(f"SDO/SRO '{oid}' missing spec_version='2.1'.")
        if otype == "indicator":
            for req in ("pattern", "pattern_type", "valid_from"):
                if not obj.get(req):
                    errors.append(f"Indicator '{oid}' missing required field '{req}'.")
        if otype == "relationship":
            for req in ("relationship_type", "source_ref", "target_ref"):
                if not obj.get(req):
                    errors.append(f"Relationship '{oid}' missing '{req}'.")
            if obj.get("source_ref") not in obj_ids or obj.get("target_ref") not in obj_ids:
                errors.append(f"Relationship '{oid}' references missing object ID.")

    return len(errors) == 0, errors


def validate_misp_event(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validates a MISP Core Format Event JSON payload."""
    errors: List[str] = []
    event = payload.get("Event") if isinstance(payload, dict) else None
    if not isinstance(event, dict):
        return False, ["Root must contain 'Event' object."]

    for req in ("uuid", "info", "date", "Orgc"):
        if not event.get(req):
            errors.append(f"MISP Event missing required field '{req}'.")

    attrs = event.get("Attribute", [])
    if not isinstance(attrs, list):
        errors.append("MISP Event 'Attribute' must be a list.")
    else:
        for idx, attr in enumerate(attrs):
            for req in ("type", "category", "value"):
                if not attr.get(req):
                    errors.append(f"Attribute[{idx}] missing '{req}'.")
            if is_private_or_pii(str(attr.get("value", "")), str(attr.get("type", ""))):
                errors.append(f"Attribute[{idx}] contains private PII or private IP.")

    return len(errors) == 0, errors


class ThreatIntelSharingService:
    """Handles MISP exports, import validation, and sharing audit logs."""

    async def log_sharing_audit(
        self,
        action: str,
        user_id: str,
        fmt: str,
        target_id: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        audit_coll = get_audit_collection()
        await audit_coll.insert_one({
            "audit_id": str(uuid.uuid4()),
            "user_id": user_id,
            "action": action,
            "resource_type": f"ti_sharing_{fmt}",
            "resource_id": target_id,
            "timestamp": datetime.now(timezone.utc),
            "details": details or {},
        })

    async def export_misp_event(
        self,
        target_type: str,
        target_id: str,
        current_user: Optional[Dict[str, Any]],
        reporting_svc,
    ) -> Dict[str, Any]:
        """Generates a validated MISP Event JSON from a STIX/JSON intelligence record without PII."""
        stix_bundle = await reporting_svc.export_stix_21(target_type=target_type, target_id=target_id, current_user=current_user)
        now_dt = datetime.now(timezone.utc)
        attributes: List[Dict[str, Any]] = []
        tags: List[Dict[str, str]] = [{"name": "tlp:amber"}, {"name": "source:trustlens-ai"}]
        pii_scrubbed = 0

        for obj in stix_bundle.get("objects", []):
            otype = obj.get("type")
            if otype in ("url", "domain-name", "ipv4-addr"):
                val = str(obj.get("value", ""))
                if is_private_or_pii(val, otype):
                    pii_scrubbed += 1
                    continue
                misp_type = "url" if otype == "url" else ("domain" if otype == "domain-name" else "ip-dst")
                attributes.append({
                    "uuid": str(uuid.uuid5(uuid.NAMESPACE_URL, f"misp:{misp_type}:{val}")),
                    "type": misp_type,
                    "category": "Network activity",
                    "value": val,
                    "to_ids": True,
                    "timestamp": str(int(now_dt.timestamp())),
                    "comment": f"Source: TRUSTLENS AI ({target_type}:{target_id})",
                })
            elif otype == "attack-pattern":
                tags.append({"name": f"trustlens:tactic=\"{obj.get('name', 'unknown')}\""})
            elif otype == "campaign":
                tags.append({"name": f"trustlens:campaign=\"{obj.get('name', 'unknown')}\""})

        misp_payload = {
            "Event": {
                "uuid": str(uuid.uuid5(uuid.NAMESPACE_URL, f"misp-event:{target_type}:{target_id}")),
                "info": f"TRUSTLENS AI Threat Intelligence: {target_type} {target_id}",
                "date": now_dt.strftime("%Y-%m-%d"),
                "timestamp": str(int(now_dt.timestamp())),
                "threat_level_id": "1",
                "analysis": "2",
                "distribution": "1",
                "Orgc": {
                    "name": "TRUSTLENS AI",
                    "uuid": TRUSTLENS_ORG_UUID,
                },
                "Tag": tags,
                "Attribute": attributes,
            },
            "x_trustlens_misp_validation": {
                "schema": "MISP Core Format",
                "pii_records_scrubbed": pii_scrubbed,
                "attributes_count": len(attributes),
            },
        }
        valid, errs = validate_misp_event(misp_payload)
        misp_payload["x_trustlens_misp_validation"]["valid"] = valid
        misp_payload["x_trustlens_misp_validation"]["errors"] = errs

        uid = (current_user or {}).get("user_id") or "anonymous"
        await self.log_sharing_audit("export_misp", uid, "misp", target_id, {"valid": valid, "attributes": len(attributes)})
        return misp_payload

    async def validate_import(
        self,
        fmt: str,
        payload: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """Validates an incoming STIX 2.1 or MISP payload and checks for PII leakage."""
        fmt_low = fmt.lower().strip()
        if fmt_low in ("stix", "stix2.1", "stix21"):
            valid, errs = validate_stix_21_bundle(payload)
            # Check SCOs for PII
            for obj in payload.get("objects", []) if isinstance(payload, dict) else []:
                if isinstance(obj, dict) and obj.get("type") in ("url", "domain-name", "ipv4-addr", "email-addr"):
                    if is_private_or_pii(str(obj.get("value", "")), str(obj.get("type", ""))):
                        valid = False
                        errs.append(f"Private PII or private IP detected in STIX object {obj.get('id')}")
        elif fmt_low == "misp":
            valid, errs = validate_misp_event(payload)
        else:
            raise ValueError("Unsupported format. Expected 'stix21' or 'misp'.")

        await self.log_sharing_audit("validate_import", user_id, fmt_low, str(payload.get("id") or "import"), {"valid": valid, "error_count": len(errs)})
        return {"format": fmt_low, "valid": valid, "errors": errs}


ti_sharing_service = ThreatIntelSharingService()
