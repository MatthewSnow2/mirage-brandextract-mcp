#!/usr/bin/env python3
"""Mirage Brand Extract MCP Server.

Extract brand identity from websites and recreate it programmatically.
Uses Firecrawl for web scraping and Google Generative AI for code generation.
"""

import os
import sys

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from mirage.tools import register_tools


def create_server() -> FastMCP:
    """Create and configure the MCP server."""
    mcp = FastMCP("mirage-brandextract")

    # Register all tools
    register_tools(mcp)

    return mcp


# Create server instance
mcp = create_server()

if __name__ == "__main__":
    mcp.run()
