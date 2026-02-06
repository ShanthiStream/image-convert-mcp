"""
Unit tests for validation functions.

Run with: python -m pytest tests/test_validation.py -v
"""

import pytest
from pathlib import Path
from PIL import Image

from src import (
    validate_path,
    validate_file_size,
    validate_image_dimensions,
    validate_params,
    ValidationError,
    MAX_DIMENSION,
)


class TestValidation:
    """Test validation functions."""
    
    def test_validate_params_missing_input_path(self):
        """Test that missing input_path raises ValidationError."""
        with pytest.raises(ValidationError, match="Missing required parameter"):
            validate_params({})
    
    def test_validate_params_invalid_mode(self):
        """Test that invalid mode raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid mode"):
            validate_params({"input_path": "/tmp/test.png", "mode": "invalid"})
    
    def test_validate_params_invalid_format(self):
        """Test that invalid format raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid format"):
            validate_params({"input_path": "/tmp/test.png", "format": "invalid"})
    
    def test_validate_params_invalid_quality(self):
        """Test that invalid quality raises ValidationError."""
        with pytest.raises(ValidationError, match="webp_quality must be 1-100"):
            validate_params({"input_path": "/tmp/test.png", "webp_quality": 150})
        
        with pytest.raises(ValidationError, match="avif_quality must be 1-100"):
            validate_params({"input_path": "/tmp/test.png", "avif_quality": 0})
    
    def test_validate_params_valid(self):
        """Test that valid params don't raise errors."""
        params = {
            "input_path": "/tmp/test.png",
            "mode": "single",
            "format": "webp",
            "webp_quality": 80,
            "avif_quality": 50
        }
        # Should not raise
        validate_params(params)


class TestPathValidation:
    """Test path validation and security."""
    
    def test_validate_path_nonexistent(self):
        """Test that nonexistent paths raise ValidationError."""
        with pytest.raises(ValidationError, match="Path does not exist"):
            validate_path(Path("/nonexistent/path/file.png"), must_exist=True)
    
    def test_validate_path_allow_nonexistent(self):
        """Test that nonexistent paths are allowed when must_exist=False."""
        # Should not raise
        path = validate_path(Path("/tmp/new_output"), must_exist=False)
        assert isinstance(path, Path)


class TestSecurityLimits:
    """Test security and resource limit validations."""
    
    def test_validate_image_dimensions_too_large(self):
        """Test image dimension validation."""
        # Create oversized image
        img = Image.new("RGB", (MAX_DIMENSION + 1, 100))
        
        with pytest.raises(ValidationError, match="Image dimensions too large"):
            validate_image_dimensions(img)
    
    def test_validate_image_dimensions_valid(self):
        """Test valid image dimensions."""
        img = Image.new("RGB", (1000, 1000))
        # Should not raise
        validate_image_dimensions(img)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
