"""
TRUSTLENS AI - Route Unification, Navigation & Auth Guard Tests
Verifies unified cyber AppShell (without Sidebar), active-link aria-current,
auth-required route guard, and unified cyber styling across updated routes.
"""

from pathlib import Path

FRONTEND = Path("frontend")


def test_appshell_uses_cyber_product_header_and_auth_guard():
    shell = (FRONTEND / "components" / "AppShell.tsx").read_text(encoding="utf-8")
    assert "CyberBackground" in shell
    assert "ProductHeader" in shell
    assert "<Sidebar" not in shell
    assert "AUTH_REQUIRED_ROUTES" in shell
    assert 'aria-current={active ? "page" : undefined}' in shell


def test_unified_routes_have_no_legacy_light_containers():
    unified_files = [
        FRONTEND / "app" / "page.tsx",
        FRONTEND / "app" / "login" / "page.tsx",
        FRONTEND / "app" / "register" / "page.tsx",
        FRONTEND / "app" / "profile" / "page.tsx",
        FRONTEND / "app" / "settings" / "page.tsx",
        FRONTEND / "app" / "analyze" / "text" / "page.tsx",
        FRONTEND / "app" / "analyze" / "url" / "page.tsx",
        FRONTEND / "app" / "analyze" / "image" / "page.tsx",
        FRONTEND / "app" / "intelligence" / "tactics" / "page.tsx",
        FRONTEND / "app" / "intelligence" / "threats" / "page.tsx",
        FRONTEND / "components" / "ui" / "AnalyzeModeTabs.tsx",
    ]
    for path in unified_files:
        text = path.read_text(encoding="utf-8")
        for forbidden in ["bg-white", "bg-slate-50", "border-slate-200", "text-slate-900"]:
            assert forbidden not in text, f"Legacy light class '{forbidden}' in {path}"
