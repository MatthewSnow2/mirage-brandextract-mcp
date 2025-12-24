"""Tests for service layer."""

import pytest
from unittest.mock import patch, MagicMock

from mirage.schemas.brand import BrandData, BrandColors, BrandTypography


class TestFirecrawlService:
    """Tests for FirecrawlService."""

    def test_requires_api_key(self):
        """Test that service requires API key."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="FIRECRAWL_API_KEY is required"):
                from mirage.services.firecrawl import FirecrawlService
                FirecrawlService()

    def test_accepts_api_key_parameter(self):
        """Test that API key can be passed as parameter."""
        from mirage.services.firecrawl import FirecrawlService

        service = FirecrawlService(api_key="test-key")
        assert service.api_key == "test-key"

    def test_reads_api_key_from_env(self):
        """Test that API key is read from environment."""
        with patch.dict("os.environ", {"FIRECRAWL_API_KEY": "env-key"}):
            from mirage.services.firecrawl import FirecrawlService

            service = FirecrawlService()
            assert service.api_key == "env-key"


class TestGeminiService:
    """Tests for GeminiService."""

    def test_requires_api_key(self):
        """Test that service requires API key."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="GOOGLE_API_KEY is required"):
                from mirage.services.gemini import GeminiService
                GeminiService()

    def test_accepts_api_key_parameter(self):
        """Test that API key can be passed as parameter."""
        with patch("google.generativeai.configure"):
            with patch("google.generativeai.GenerativeModel"):
                from mirage.services.gemini import GeminiService

                service = GeminiService(api_key="test-key")
                assert service.api_key == "test-key"

    @pytest.mark.asyncio
    async def test_calculate_color_similarity(self):
        """Test color similarity calculation."""
        with patch("google.generativeai.configure"):
            with patch("google.generativeai.GenerativeModel"):
                from mirage.services.gemini import GeminiService

                service = GeminiService(api_key="test-key")

                # Same color should have similarity 1.0
                similarity = await service.calculate_color_similarity("#FF0000", "#FF0000")
                assert similarity == 1.0

                # Very different colors should have low similarity
                similarity = await service.calculate_color_similarity("#000000", "#FFFFFF")
                assert similarity < 0.5

                # Similar colors should have high similarity
                similarity = await service.calculate_color_similarity("#FF0000", "#FF1111")
                assert similarity > 0.9


class TestBrandDataSchema:
    """Tests for BrandData schema."""

    def test_brand_data_serialization(self):
        """Test that BrandData can be serialized to dict."""
        brand = BrandData(
            url="https://example.com",
            colors=BrandColors(primary="#FF0000"),
            typography=BrandTypography(headings="Arial", body="Helvetica"),
        )

        data = brand.model_dump()
        assert data["url"] == "https://example.com"
        assert data["colors"]["primary"] == "#FF0000"
        assert data["typography"]["headings"] == "Arial"

    def test_brand_data_validation(self):
        """Test that BrandData validates input."""
        # Valid data should work
        brand = BrandData.model_validate({
            "url": "https://example.com",
            "colors": {"primary": "#FF0000"},
            "typography": {"headings": "Arial", "body": "Helvetica"},
        })
        assert brand.url == "https://example.com"
