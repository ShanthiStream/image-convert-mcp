"""
Unit tests for the image-convert-mcp server.

Run with: python -m pytest test_mcp_server.py -v
"""

import json
import pytest
from pathlib import Path
from PIL import Image
import tempfile
import shutil

from api.index import (
    load_image,
    resize_if_needed,
    convert_one,
    validate_path,
    validate_file_size,
    validate_image_dimensions,
    validate_params,
    ValidationError,
    ImageConversionError,
    MAX_FILE_SIZE_MB,
    MAX_DIMENSION,
)


class TestValidation:
    """Test validation functions"""
    
    def test_validate_params_missing_input_path(self):
        """Test that missing input_path raises ValidationError"""
        with pytest.raises(ValidationError, match="Missing required parameter"):
            validate_params({})
    
    def test_validate_params_invalid_mode(self):
        """Test that invalid mode raises ValidationError"""
        with pytest.raises(ValidationError, match="Invalid mode"):
            validate_params({"input_path": "/tmp/test.png", "mode": "invalid"})
    
    def test_validate_params_invalid_format(self):
        """Test that invalid format raises ValidationError"""
        with pytest.raises(ValidationError, match="Invalid format"):
            validate_params({"input_path": "/tmp/test.png", "format": "invalid"})
    
    def test_validate_params_invalid_quality(self):
        """Test that invalid quality raises ValidationError"""
        with pytest.raises(ValidationError, match="webp_quality must be 1-100"):
            validate_params({"input_path": "/tmp/test.png", "webp_quality": 150})
        
        with pytest.raises(ValidationError, match="avif_quality must be 1-100"):
            validate_params({"input_path": "/tmp/test.png", "avif_quality": 0})
    
    def test_validate_params_valid(self):
        """Test that valid params don't raise errors"""
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
    """Test path validation and security"""
    
    def test_validate_path_nonexistent(self):
        """Test that nonexistent paths raise ValidationError"""
        with pytest.raises(ValidationError, match="Path does not exist"):
            validate_path(Path("/nonexistent/path/file.png"), must_exist=True)
    
    def test_validate_path_allow_nonexistent(self):
        """Test that nonexistent paths are allowed when must_exist=False"""
        # Should not raise
        path = validate_path(Path("/tmp/new_output"), must_exist=False)
        assert isinstance(path, Path)


class TestImageOperations:
    """Test image loading and manipulation"""
    
    @pytest.fixture
    def temp_image(self):
        """Create a temporary test image"""
        temp_dir = tempfile.mkdtemp()
        img_path = Path(temp_dir) / "test.png"
        
        # Create a small test image
        img = Image.new("RGB", (100, 100), color="red")
        img.save(img_path, "PNG")
        
        yield img_path
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_load_image_success(self, temp_image):
        """Test successful image loading"""
        img = load_image(temp_image)
        assert img.mode == "RGBA"
        assert img.size == (100, 100)
    
    def test_load_image_nonexistent(self):
        """Test loading nonexistent image raises error"""
        with pytest.raises(ImageConversionError):
            load_image(Path("/nonexistent/image.png"))
    
    def test_resize_if_needed_no_resize(self):
        """Test that image is not resized when no limits specified"""
        img = Image.new("RGB", (100, 100))
        resized = resize_if_needed(img, None, None)
        assert resized.size == (100, 100)
    
    def test_resize_if_needed_width_limit(self):
        """Test resizing with width limit"""
        img = Image.new("RGB", (200, 100))
        resized = resize_if_needed(img, 100, None)
        assert resized.size == (100, 50)  # Aspect ratio preserved
    
    def test_resize_if_needed_height_limit(self):
        """Test resizing with height limit"""
        img = Image.new("RGB", (100, 200))
        resized = resize_if_needed(img, None, 100)
        assert resized.size == (50, 100)  # Aspect ratio preserved


class TestConversion:
    """Test image conversion functions"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for conversions"""
        temp_dir = tempfile.mkdtemp()
        input_path = Path(temp_dir) / "input.png"
        output_dir = Path(temp_dir) / "output"
        output_dir.mkdir()
        
        # Create test image
        img = Image.new("RGB", (50, 50), color="blue")
        img.save(input_path, "PNG")
        
        yield input_path, output_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_convert_one_webp(self, temp_workspace):
        """Test converting to WebP"""
        input_path, output_dir = temp_workspace
        
        result = convert_one(
            image_path=input_path,
            output_dir=output_dir,
            format="webp",
            webp_quality=80,
            avif_quality=50,
            lossless=False,
            max_width=None,
            max_height=None,
        )
        
        assert "input" in result
        assert "webp" in result
        assert "avif" not in result
        assert Path(result["webp"]).exists()
    
    def test_convert_one_avif(self, temp_workspace):
        """Test converting to AVIF"""
        input_path, output_dir = temp_workspace
        
        result = convert_one(
            image_path=input_path,
            output_dir=output_dir,
            format="avif",
            webp_quality=80,
            avif_quality=50,
            lossless=False,
            max_width=None,
            max_height=None,
        )
        
        assert "input" in result
        assert "avif" in result
        assert "webp" not in result
        assert Path(result["avif"]).exists()
    
    def test_convert_one_both(self, temp_workspace):
        """Test converting to both formats"""
        input_path, output_dir = temp_workspace
        
        result = convert_one(
            image_path=input_path,
            output_dir=output_dir,
            format="both",
            webp_quality=80,
            avif_quality=50,
            lossless=False,
            max_width=None,
            max_height=None,
        )
        
        assert "input" in result
        assert "webp" in result
        assert "avif" in result
        assert Path(result["webp"]).exists()
        assert Path(result["avif"]).exists()
    
    def test_convert_one_with_resize(self, temp_workspace):
        """Test conversion with resizing"""
        input_path, output_dir = temp_workspace
        
        result = convert_one(
            image_path=input_path,
            output_dir=output_dir,
            format="webp",
            webp_quality=80,
            avif_quality=50,
            lossless=False,
            max_width=25,
            max_height=25,
        )
        
        # Verify the output exists and is smaller
        webp_path = Path(result["webp"])
        assert webp_path.exists()
        
        # Load and check dimensions
        img = Image.open(webp_path)
        assert img.size == (25, 25)


class TestSecurityLimits:
    """Test security and resource limit validations"""
    
    def test_validate_file_size_too_large(self):
        """Test file size validation"""
        # Create a temporary large-ish path for testing
        # We won't create actual file, just test the validation logic
        # In real scenario, this would check actual file size
        pass  # Requires actual large file for integration test
    
    def test_validate_image_dimensions_too_large(self):
        """Test image dimension validation"""
        # Create oversized image
        img = Image.new("RGB", (MAX_DIMENSION + 1, 100))
        
        with pytest.raises(ValidationError, match="Image dimensions too large"):
            validate_image_dimensions(img)
    
    def test_validate_image_dimensions_valid(self):
        """Test valid image dimensions"""
        img = Image.new("RGB", (1000, 1000))
        # Should not raise
        validate_image_dimensions(img)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
