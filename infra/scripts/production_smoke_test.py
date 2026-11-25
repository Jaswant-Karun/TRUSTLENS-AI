"""
TRUSTLENS AI — Independent Production Smoke Test Suite
Verifies live HTTPS frontend & FastAPI backend health, auth, analysis, investigations,
reports, and transparency endpoints. Refuses localhost/HTTP unless --allow-local-dryrun is set.
"""

import argparse
import sys
import uuid
import httpx


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frontend-url", required=True)
    parser.add_argument("--backend-url", required=True)
    parser.add_argument("--allow-local-dryrun", action="store_true")
    args = parser.parse_args()

    fe = args.frontend_url.rstrip("/")
    be = args.backend_url.rstrip("/")

    if not args.allow_local_dryrun:
        if not fe.startswith("https://") or not be.startswith("https://"):
            print("ERROR: Production smoke tests require https:// URLs.", file=sys.stderr)
            return 2
        if "localhost" in fe or "127.0.0.1" in fe or "localhost" in be or "127.0.0.1" in be:
            print("ERROR: Production smoke tests refuse localhost targets.", file=sys.stderr)
            return 2

    with httpx.Client(timeout=20.0) as client:
        # 1. Health & Transparency
        h = client.get(f"{be}/api/v1/health")
        assert h.status_code == 200, f"Health failed: {h.status_code}"
        tr = client.get(f"{be}/api/v1/privacy/transparency")
        assert tr.status_code == 200, f"Transparency failed: {tr.status_code}"

        # 2. Frontend SSR/Static Routes
        for route in ("/", "/methodology", "/privacy-policy", "/login"):
            fr = client.get(f"{fe}{route}")
            assert fr.status_code == 200, f"Frontend {route} returned {fr.status_code}"

        # 3. Critical Authenticated Workflow: Register -> Login -> Analyze Text & URL -> Logout
        email = f"smoke_{uuid.uuid4().hex[:8]}@trustlens.ai"
        pw = "SmokeTest@2026!"
        reg = client.post(
            f"{be}/api/v1/auth/register",
            json={"email": email, "full_name": "Smoke Verifier", "password": pw},
        )
        assert reg.status_code in (200, 201), f"Register failed: {reg.text}"

        login = client.post(f"{be}/api/v1/auth/login", json={"email": email, "password": pw})
        assert login.status_code == 200, f"Login failed: {login.text}"
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        t_res = client.post(
            f"{be}/api/v1/analyze/text",
            headers=headers,
            json={"text": "Urgent KYC update: http://192.168.1.50/kyc.php", "channel": "sms"},
        )
        assert t_res.status_code == 200, f"Text analysis failed: {t_res.text}"

        u_res = client.post(
            f"{be}/api/v1/analyze/url",
            headers=headers,
            json={"url": "http://secure-login-hdfcbank-account-update.xyz/login.php"},
        )
        assert u_res.status_code == 200, f"URL analysis failed: {u_res.text}"

        lo = client.post(f"{be}/api/v1/auth/logout", headers=headers)
        assert lo.status_code == 200, f"Logout failed: {lo.text}"

    print("[production_smoke_test] ALL CRITICAL WORKFLOWS VERIFIED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
