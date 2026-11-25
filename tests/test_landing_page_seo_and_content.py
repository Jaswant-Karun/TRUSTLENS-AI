"""
TRUSTLENS AI - Landing Page SEO, Content & Structure Tests
Verifies Server Component SEO metadata, genuine capability messaging,
zero sidebar/dashboard leakage, and Sign In / Get Started / Radial Navigation presence.
"""

from pathlib import Path

FRONTEND = Path("frontend")


def test_root_page_exports_seo_metadata():
    root_page = (FRONTEND / "app" / "page.tsx").read_text(encoding="utf-8")
    assert "export const metadata: Metadata" in root_page
    assert "openGraph" in root_page
    assert "LandingExperience" in root_page
    assert '"use client"' not in root_page


def test_landing_experience_has_genuine_claims_and_radial_nav():
    landing = (FRONTEND / "components" / "product" / "LandingExperience.tsx").read_text(encoding="utf-8")
    assert "INTELLIGENCE THAT STOPS" in landing
    assert "RadialNavigation" in landing
    assert 'href="/login"' in landing
    assert 'href="/register"' in landing
    assert "ZERO-HOP URL SAFETY" in landing
    assert "<Sidebar" not in landing
    assert "100% accuracy" not in landing.lower()
