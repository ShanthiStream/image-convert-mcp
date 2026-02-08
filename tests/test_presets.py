"""
Tests for presets module.
"""

import pytest
from src.presets import get_preset, list_presets, PRESETS


class TestPresets:
    """Test preset functionality."""
    
    def test_all_presets_exist(self):
        """Verify all expected presets exist."""
        expected = ["web", "thumbnail", "social", "hd", "4k", "archive", "lossless", "max-compression"]
        assert set(expected) == set(PRESETS.keys())
    
    def test_get_preset_valid(self):
        """Test getting a valid preset."""
        preset = get_preset("web")
        assert preset["format"] == "webp"
        assert preset["webp_quality"] == 80
        assert preset["max_width"] == 1920
    
    def test_get_preset_invalid(self):
        """Test getting an invalid preset raises error."""
        with pytest.raises(ValueError) as exc_info:
            get_preset("nonexistent")
        assert "Unknown preset" in str(exc_info.value)
    
    def test_get_preset_returns_copy(self):
        """Ensure get_preset returns a copy, not the original."""
        preset1 = get_preset("web")
        preset1["webp_quality"] = 999
        preset2 = get_preset("web")
        assert preset2["webp_quality"] == 80
    
    def test_list_presets(self):
        """Test listing presets with descriptions."""
        descriptions = list_presets()
        assert "web" in descriptions
        assert "thumbnail" in descriptions
        assert len(descriptions) == len(PRESETS)
    
    def test_thumbnail_preset_has_dimensions(self):
        """Verify thumbnail preset has dimension limits."""
        preset = get_preset("thumbnail")
        assert preset["max_width"] == 300
        assert preset["max_height"] == 300
    
    def test_lossless_preset(self):
        """Verify lossless preset has correct settings."""
        preset = get_preset("lossless")
        assert preset["lossless"] is True
        assert preset["format"] == "webp"
