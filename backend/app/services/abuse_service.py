"""
TRUSTLENS AI - Application Abuse Protection & Operational Alerting Service
Protects against brute-force logins, suspicious request probes, and resource exhaustion,
while emitting structured operational alerts for SOC analysts/admins.
"""

import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from backend.app.core.logging import logger
from backend.app.database.manager import db_manager

COLL_ABUSE_EVENTS = "abuse_events"
COLL_OPERATIONAL_ALERTS = "operational_alerts"


class AbuseProtectionService:
    """Tracks brute-force attempts, suspicious requests, and operational alerts."""

    MAX_LOGIN_FAILURES = 5
    FAILURE_WINDOW_SECONDS = 300
    LOCKOUT_SECONDS = 300

    def __init__(self):
        self._login_failures: Dict[str, List[float]] = {}
        self._lockouts: Dict[str, float] = {}
        self._suspicious_counts: Dict[str, int] = {}

    def _key(self, email: str, client_ip: Optional[str]) -> str:
        return f"{email.lower().strip()}:{client_ip or 'unknown'}"

    def is_locked_out(self, email: str, client_ip: Optional[str]) -> Optional[int]:
        """Returns remaining lockout seconds if locked out, else None."""
        k = self._key(email, client_ip)
        until = self._lockouts.get(k)
        if until is None:
            return None
        rem = int(until - time.monotonic())
        if rem <= 0:
            self._lockouts.pop(k, None)
            self._login_failures.pop(k, None)
            return None
        return rem

    async def record_login_failure(self, email: str, client_ip: Optional[str]) -> bool:
        """Records failed login; returns True if lockout was triggered."""
        k = self._key(email, client_ip)
        now = time.monotonic()
        window = [ts for ts in self._login_failures.get(k, []) if (now - ts) < self.FAILURE_WINDOW_SECONDS]
        window.append(now)
        self._login_failures[k] = window

        if len(window) >= self.MAX_LOGIN_FAILURES:
            self._lockouts[k] = now + self.LOCKOUT_SECONDS
            await self.record_suspicious_event(
                event_type="brute_force_login_lockout",
                client_ip=client_ip or "unknown",
                path="/api/v1/auth/login",
                detail=f"Exceeded {self.MAX_LOGIN_FAILURES} failed login attempts",
                raise_alert=True,
                severity="high",
            )
            return True
        return False

    def clear_login_failures(self, email: str, client_ip: Optional[str]) -> None:
        k = self._key(email, client_ip)
        self._login_failures.pop(k, None)
        self._lockouts.pop(k, None)

    async def record_suspicious_event(
        self,
        event_type: str,
        client_ip: str,
        path: str,
        detail: str,
        raise_alert: bool = False,
        severity: str = "medium",
    ) -> None:
        now_iso = datetime.now(timezone.utc).isoformat()
        ev = {
            "event_id": f"ab-{uuid.uuid4().hex[:10]}",
            "event_type": event_type,
            "client_ip": client_ip,
            "path": path,
            "detail": detail[:300],
            "severity": severity,
            "timestamp_utc": now_iso,
        }
        try:
            await db_manager.get_collection(COLL_ABUSE_EVENTS).insert_one(dict(ev))
        except Exception:
            pass

        ip_count = self._suspicious_counts.get(client_ip, 0) + 1
        self._suspicious_counts[client_ip] = ip_count

        if raise_alert or ip_count >= 3:
            alert = {
                "alert_id": f"al-{uuid.uuid4().hex[:10]}",
                "alert_type": event_type,
                "severity": "critical" if ip_count >= 5 else severity,
                "client_ip": client_ip,
                "path": path,
                "occurrences": ip_count,
                "detail": detail[:300],
                "timestamp_utc": now_iso,
                "acknowledged": False,
            }
            logger.warning(f"OPERATIONAL_ALERT [{alert['severity']}]: {event_type} from {client_ip} on {path}")
            try:
                await db_manager.get_collection(COLL_OPERATIONAL_ALERTS).insert_one(dict(alert))
            except Exception:
                pass

    async def get_monitoring_summary(self, limit: int = 50) -> Dict[str, Any]:
        now = time.monotonic()
        active_lockouts = sum(1 for until in self._lockouts.values() if until > now)
        events = await db_manager.get_collection(COLL_ABUSE_EVENTS).find({}, {"_id": 0}).sort("timestamp_utc", -1).limit(limit).to_list(length=limit)
        alerts = await db_manager.get_collection(COLL_OPERATIONAL_ALERTS).find({}, {"_id": 0}).sort("timestamp_utc", -1).limit(limit).to_list(length=limit)
        return {
            "active_login_lockouts": active_lockouts,
            "recent_abuse_events_count": len(events),
            "operational_alerts_count": len(alerts),
            "recent_abuse_events": events,
            "operational_alerts": alerts,
        }


abuse_service = AbuseProtectionService()
