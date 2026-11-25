"""
TRUSTLENS AI - Global Cyber Design System Consistency Tests
Verifies that core design tokens, CSS utilities, shared UI primitives,
and cyber product components are consistent with zero legacy light-theme conflicts.
"""

from pathlib import Path

FRONTEND = Path("frontend")


def test_cyber_design_tokens_present():
    globals_css = (FRONTEND / "app" / "globals.css").read_text(encoding="utf-8").lower()
    tailwind_cfg = (FRONTEND / "tailwind.config.ts").read_text(encoding="utf-8").lower()

    required_tokens = [
        "#050306",
        "#10070d",
        "#170a12",
        "#ff174f",
        "#c2185b",
        "#ff3d70",
        "#481326",
        "#00d68f",
        "#ffb020",
    ]
    for token in required_tokens:
        assert token in globals_css, f"Missing CSS token {token} in globals.css"
        assert token in tailwind_cfg, f"Missing Tailwind token {token} in tailwind.config.ts"

    for utility in [".cyber-panel", ".cyber-input", ".cyber-modal", ".cyber-btn-primary"]:
        assert utility in globals_css, f"Missing utility class {utility} in globals.css"


def test_shared_ui_components_use_cyber_theme():
    migrated_components = [
        "Toast.tsx",
        "ConfirmDialog.tsx",
        "MetricCard.tsx",
        "DataTable.tsx",
        "EmptyState.tsx",
        "ErrorState.tsx",
        "LoadingStates.tsx",
        "PageHeader.tsx",
        "SearchFilterBar.tsx",
        "Breadcrumb.tsx",
    ]
    forbidden_light_classes = ["bg-white", "bg-slate-50", "border-slate-200", "text-slate-900"]
    for name in migrated_components:
        content = (FRONTEND / "components" / "ui" / name).read_text(encoding="utf-8")
        for cls in forbidden_light_classes:
            assert cls not in content, f"Legacy light class '{cls}' found in {name}"


def test_product_cyber_primitives_and_radial_routes_exist():
    required_product_files = [
        "CircuitPattern.tsx",
        "CyberBackground.tsx",
        "NeonFrame.tsx",
        "GlowButton.tsx",
        "RadialNavigation.tsx",
        "ProductHeader.tsx",
    ]
    for name in required_product_files:
        assert (FRONTEND / "components" / "product" / name).exists(), f"Missing {name}"

    radial = (FRONTEND / "components" / "product" / "RadialNavigation.tsx").read_text(encoding="utf-8")
    for route in ["/", "/analyze/text", "/analyze/url", "/analyze/image", "/intelligence/campaigns", "/investigations", "/reports", "/profile"]:
        assert f'href: "{route}"' in radial, f"Missing radial route {route}"
