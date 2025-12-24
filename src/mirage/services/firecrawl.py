"""Firecrawl API service for web scraping and brand extraction."""

import os
from typing import Optional

import httpx

from ..schemas.brand import (
    BrandData,
    BrandColors,
    BrandTypography,
    BrandSpacing,
    BrandButtons,
    ButtonStyle,
)


class FirecrawlService:
    """Async client for Firecrawl API."""

    BASE_URL = "https://api.firecrawl.dev/v1"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Firecrawl service.

        Args:
            api_key: Firecrawl API key. If not provided, reads from FIRECRAWL_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            raise ValueError("FIRECRAWL_API_KEY is required")

        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    async def scrape(self, url: str, include_screenshot: bool = False) -> dict:
        """Scrape a URL using Firecrawl.

        Args:
            url: The URL to scrape
            include_screenshot: Whether to include a screenshot

        Returns:
            Raw scrape response from Firecrawl
        """
        payload = {
            "url": url,
            "formats": ["html", "markdown"],
        }

        if include_screenshot:
            payload["formats"].append("screenshot")

        response = await self.client.post("/scrape", json=payload)
        response.raise_for_status()
        return response.json()

    async def extract_brand(self, url: str, include_screenshots: bool = False) -> BrandData:
        """Extract brand identity from a website.

        Args:
            url: The website URL to analyze
            include_screenshots: Whether to capture screenshots

        Returns:
            Structured brand data
        """
        # Use Firecrawl's extract endpoint with a schema for brand data
        payload = {
            "url": url,
            "formats": ["extract"],
            "extract": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "colors": {
                            "type": "object",
                            "properties": {
                                "primary": {"type": "string", "description": "Primary brand color in hex"},
                                "secondary": {"type": "string", "description": "Secondary brand color in hex"},
                                "accent": {"type": "string", "description": "Accent color in hex"},
                                "background": {"type": "string", "description": "Background color in hex"},
                                "text": {"type": "string", "description": "Primary text color in hex"},
                                "palette": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "All colors found on the page"
                                }
                            }
                        },
                        "typography": {
                            "type": "object",
                            "properties": {
                                "headings": {"type": "string", "description": "Font family for headings"},
                                "body": {"type": "string", "description": "Font family for body text"},
                                "weights": {
                                    "type": "array",
                                    "items": {"type": "integer"},
                                    "description": "Font weights used"
                                }
                            }
                        },
                        "buttons": {
                            "type": "object",
                            "properties": {
                                "primary": {
                                    "type": "object",
                                    "properties": {
                                        "bg": {"type": "string"},
                                        "text": {"type": "string"},
                                        "border_radius": {"type": "string"},
                                        "padding": {"type": "string"}
                                    }
                                }
                            }
                        },
                        "logo_url": {"type": "string", "description": "URL to the website logo"},
                        "favicon_url": {"type": "string", "description": "URL to the favicon"}
                    }
                },
                "prompt": "Extract the brand identity including colors, typography, and button styles from this website. For colors, provide hex values. For typography, identify the font families used for headings and body text."
            }
        }

        if include_screenshots:
            payload["formats"].append("screenshot")

        response = await self.client.post("/scrape", json=payload)
        response.raise_for_status()
        data = response.json()

        # Parse the extracted data
        extracted = data.get("data", {}).get("extract", {})
        screenshots = []

        if include_screenshots and "screenshot" in data.get("data", {}):
            screenshots.append(data["data"]["screenshot"])

        # Build the brand data structure
        colors_data = extracted.get("colors", {})
        colors = BrandColors(
            primary=colors_data.get("primary", "#000000"),
            secondary=colors_data.get("secondary"),
            accent=colors_data.get("accent"),
            background=colors_data.get("background"),
            text=colors_data.get("text"),
            palette=colors_data.get("palette", []),
        )

        typo_data = extracted.get("typography", {})
        typography = BrandTypography(
            headings=typo_data.get("headings", "sans-serif"),
            body=typo_data.get("body", "sans-serif"),
            weights=typo_data.get("weights", [400, 600, 700]),
        )

        spacing = BrandSpacing()

        buttons_data = extracted.get("buttons", {})
        buttons = BrandButtons()
        if buttons_data.get("primary"):
            btn = buttons_data["primary"]
            buttons.primary = ButtonStyle(
                bg=btn.get("bg", colors.primary),
                text=btn.get("text", "#ffffff"),
                border_radius=btn.get("border_radius", "4px"),
                padding=btn.get("padding", "12px 24px"),
            )

        return BrandData(
            url=url,
            colors=colors,
            typography=typography,
            spacing=spacing,
            buttons=buttons,
            logo_url=extracted.get("logo_url"),
            favicon_url=extracted.get("favicon_url"),
            screenshots=screenshots,
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
