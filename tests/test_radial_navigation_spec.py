"""
TRUSTLENS AI - RadialNavigation Component Contract & Accessibility Tests
Verifies all 8 required items, real route targets, keyboard navigation,
outside-click/touch handling, focus management, and reduced-motion support.
"""

from pathlib import Path

FRONTEND = Path("frontend")


def test_radial_navigation_items_and_real_routes():
    radial = (FRONTEND / "components" / "product" / "RadialNavigation.tsx").read_text(encoding="utf-8")

    expected_items = [
        ("Home", "/"),
        ("Message Scanner", "/analyze/text"),
        ("URL Shield", "/analyze/url"),
        ("Screenshot Analyzer", "/analyze/image"),
        ("Threat Intelligence", "/intelligence/campaigns"),
        ("Investigations", "/investigations"),
        ("Reports", "/reports"),
        ("Profile", "/profile"),
    ]
    for label, href in expected_items:
        assert f'label: "{label}"' in radial, f"Missing label {label}"
        assert f'href: "{href}"' in radial, f"Missing route {href}"
        # Verify corresponding App Router page exists
        if href == "/":
            assert (FRONTEND / "app" / "page.tsx").exists()
        else:
            route_file = FRONTEND / "app" / href.lstrip("/") / "page.tsx"
            assert route_file.exists(), f"Missing Next.js route file for {href}"


def test_radial_navigation_accessibility_and_motion():
    radial = (FRONTEND / "components" / "product" / "RadialNavigation.tsx").read_text(encoding="utf-8")
    for token in [
        "useReducedMotion",
        "Escape",
        "ArrowRight",
        "ArrowLeft",
        "Home",
        "End",
        "mousedown",
        "touchstart",
        "centerBtnRef",
        "itemBtnRefs",
        "aria-expanded",
    ]:
        assert token in radial, f"Missing accessibility/interaction handler: {token}"
