"""
TRUSTLENS AI - Brand Identity, Favicon, Manifest & Loader Tests
Verifies original TRUSTLENS AI brand assets, metadata, loading screen,
and zero copied INFINTUM branding.
"""

from pathlib import Path

FRONTEND = Path("frontend")


def test_brand_assets_and_manifest_exist():
    assert (FRONTEND / "components" / "product" / "BrandLogo.tsx").exists()
    assert (FRONTEND / "components" / "product" / "BrandLoader.tsx").exists()
    assert (FRONTEND / "app" / "icon.svg").exists()
    assert (FRONTEND / "app" / "apple-icon.svg").exists()
    assert (FRONTEND / "app" / "manifest.ts").exists()

    loading = (FRONTEND / "app" / "loading.tsx").read_text(encoding="utf-8")
    assert "BrandLoader" in loading

    layout = (FRONTEND / "app" / "layout.tsx").read_text(encoding="utf-8")
    assert 'applicationName: "TRUSTLENS AI"' in layout
    assert 'icon: "/icon.svg"' in layout


def test_no_copied_infintum_branding_anywhere_in_product_ui():
    for path in (FRONTEND / "components" / "product").glob("*.tsx"):
        content = path.read_text(encoding="utf-8").lower()
        assert "infintum" not in content, f"Copied INFINTUM branding found in {path.name}"
