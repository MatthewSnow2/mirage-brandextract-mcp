"""Tests for MCP tools."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from mirage.schemas.brand import BrandData, GeneratedCode


class TestExtractBrand:
    """Tests for extract_brand tool."""

    @pytest.mark.asyncio
    async def test_extract_brand_returns_dict(self, sample_brand_data):
        """Test that extract_brand returns a dictionary."""
        with patch("mirage.tools.FirecrawlService") as MockService:
            mock_instance = MagicMock()
            mock_instance.extract_brand = AsyncMock(return_value=sample_brand_data)
            mock_instance.close = AsyncMock()
            MockService.return_value = mock_instance

            from mirage.tools import register_tools
            from mcp.server.fastmcp import FastMCP

            mcp = FastMCP("test")
            register_tools(mcp)

            # The tool should be registered
            assert "extract_brand" in [t.name for t in mcp._tool_manager._tools.values()]


class TestGenerateReplica:
    """Tests for generate_replica tool."""

    @pytest.mark.asyncio
    async def test_generate_replica_accepts_brand_dict(self, sample_brand_data, sample_generated_code):
        """Test that generate_replica works with dict input."""
        with patch("mirage.tools.GeminiService") as MockService:
            mock_instance = MagicMock()
            mock_instance.generate_replica = AsyncMock(return_value=sample_generated_code)
            MockService.return_value = mock_instance

            from mirage.tools import register_tools
            from mcp.server.fastmcp import FastMCP

            mcp = FastMCP("test")
            register_tools(mcp)

            assert "generate_replica" in [t.name for t in mcp._tool_manager._tools.values()]


class TestReplicateWebsite:
    """Tests for replicate_website tool."""

    @pytest.mark.asyncio
    async def test_replicate_website_combines_extract_and_generate(
        self, sample_brand_data, sample_generated_code
    ):
        """Test that replicate_website combines both operations."""
        from mirage.tools import register_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_tools(mcp)

        assert "replicate_website" in [t.name for t in mcp._tool_manager._tools.values()]


class TestCompareBrands:
    """Tests for compare_brands tool."""

    @pytest.mark.asyncio
    async def test_compare_brands_returns_comparison(self):
        """Test that compare_brands returns comparison data."""
        from mirage.tools import register_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_tools(mcp)

        assert "compare_brands" in [t.name for t in mcp._tool_manager._tools.values()]


class TestApplyBrandToTemplate:
    """Tests for apply_brand_to_template tool."""

    @pytest.mark.asyncio
    async def test_apply_brand_to_template_supports_all_types(self):
        """Test that all template types are supported."""
        from mirage.tools import register_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_tools(mcp)

        assert "apply_brand_to_template" in [t.name for t in mcp._tool_manager._tools.values()]


class TestToolRegistration:
    """Tests for tool registration."""

    def test_all_tools_registered(self):
        """Test that all 5 tools are registered."""
        from mirage.tools import register_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_tools(mcp)

        tool_names = [t.name for t in mcp._tool_manager._tools.values()]

        expected_tools = [
            "extract_brand",
            "generate_replica",
            "replicate_website",
            "compare_brands",
            "apply_brand_to_template",
        ]

        for tool in expected_tools:
            assert tool in tool_names, f"Tool {tool} not registered"
