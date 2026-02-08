"""
Tests for stats module.
"""

import pytest
from src.stats import (
    format_size,
    calculate_savings,
    format_stats_summary,
)


class TestFormatSize:
    """Test size formatting."""
    
    def test_bytes(self):
        """Test byte formatting."""
        assert format_size(500) == "500 B"
    
    def test_kilobytes(self):
        """Test KB formatting."""
        assert format_size(1024) == "1.0 KB"
        assert format_size(2560) == "2.5 KB"
    
    def test_megabytes(self):
        """Test MB formatting."""
        assert format_size(1024 * 1024) == "1.00 MB"
        assert format_size(2.5 * 1024 * 1024) == "2.50 MB"


class TestCalculateSavings:
    """Test compression savings calculation."""
    
    def test_50_percent_savings(self):
        """Test 50% file size reduction."""
        result = calculate_savings(1000, 500)
        assert result["savings_percent"] == "50.0%"
        assert result["increased"] is False
    
    def test_file_increases(self):
        """Test when file gets larger."""
        result = calculate_savings(500, 1000)
        assert result["increased"] is True
    
    def test_compression_ratio(self):
        """Test compression ratio calculation."""
        result = calculate_savings(1000, 250)
        assert "4.0:1" in result["compression_ratio"]
    
    def test_zero_original(self):
        """Test handling zero original size."""
        result = calculate_savings(0, 100)
        assert result["savings_percent"] == "0.0%"


class TestFormatStatsSummary:
    """Test stats summary formatting."""
    
    def test_error_case(self):
        """Test error message formatting."""
        result = format_stats_summary({"error": "Test error"})
        assert "❌" in result
        assert "Test error" in result
    
    def test_basic_stats(self):
        """Test basic stats formatting."""
        stats = {
            "input": "test.png",
            "input_size": "1.00 MB",
            "webp": {
                "path": "test.webp",
                "new_size": "250 KB",
                "savings_percent": "75%",
                "increased": False,
            }
        }
        result = format_stats_summary(stats)
        assert "📊" in result
        assert "1.00 MB" in result
        assert "WebP" in result
