"""Pydantic schemas for brand data structures."""

from typing import Optional
from pydantic import BaseModel, Field


class BrandColors(BaseModel):
    """Color palette extracted from a website."""

    primary: str = Field(description="Primary brand color in hex format")
    secondary: Optional[str] = Field(default=None, description="Secondary brand color")
    accent: Optional[str] = Field(default=None, description="Accent color")
    background: Optional[str] = Field(default=None, description="Background color")
    text: Optional[str] = Field(default=None, description="Primary text color")
    palette: list[str] = Field(default_factory=list, description="Full color palette")


class BrandTypography(BaseModel):
    """Typography settings extracted from a website."""

    headings: str = Field(description="Font family for headings")
    body: str = Field(description="Font family for body text")
    weights: list[int] = Field(default_factory=lambda: [400, 600, 700], description="Available font weights")
    base_size: Optional[str] = Field(default="16px", description="Base font size")
    line_height: Optional[str] = Field(default="1.5", description="Default line height")


class BrandSpacing(BaseModel):
    """Spacing system extracted from a website."""

    grid: str = Field(default="8px", description="Base grid unit")
    margins: dict[str, str] = Field(default_factory=dict, description="Margin values")
    padding: dict[str, str] = Field(default_factory=dict, description="Padding values")
    gap: Optional[str] = Field(default=None, description="Default gap between elements")


class ButtonStyle(BaseModel):
    """Individual button style."""

    bg: str = Field(description="Background color")
    text: str = Field(description="Text color")
    border_radius: str = Field(default="4px", description="Border radius")
    padding: str = Field(default="12px 24px", description="Button padding")
    border: Optional[str] = Field(default=None, description="Border style")
    hover_bg: Optional[str] = Field(default=None, description="Hover background color")


class BrandButtons(BaseModel):
    """Button styles extracted from a website."""

    primary: Optional[ButtonStyle] = Field(default=None, description="Primary button style")
    secondary: Optional[ButtonStyle] = Field(default=None, description="Secondary button style")
    outline: Optional[ButtonStyle] = Field(default=None, description="Outline button style")


class BrandData(BaseModel):
    """Complete brand identity extracted from a website."""

    url: str = Field(description="Source URL")
    colors: BrandColors = Field(description="Color palette")
    typography: BrandTypography = Field(description="Typography settings")
    spacing: BrandSpacing = Field(default_factory=BrandSpacing, description="Spacing system")
    buttons: BrandButtons = Field(default_factory=BrandButtons, description="Button styles")
    logo_url: Optional[str] = Field(default=None, description="URL to the logo if found")
    favicon_url: Optional[str] = Field(default=None, description="URL to the favicon if found")
    screenshots: list[str] = Field(default_factory=list, description="Screenshot URLs if requested")


class GeneratedCode(BaseModel):
    """Generated HTML/CSS code."""

    html: str = Field(description="Generated HTML code")
    css: str = Field(description="Generated CSS code")
    preview_url: Optional[str] = Field(default=None, description="Data URL for preview")
    component_type: Optional[str] = Field(default=None, description="Type of component generated")


class ComparisonMetrics(BaseModel):
    """Comparison metrics between two brands."""

    color_similarity: float = Field(ge=0, le=1, description="Color similarity score (0-1)")
    typography_match: bool = Field(description="Whether typography fonts match")
    font_overlap: list[str] = Field(default_factory=list, description="Shared fonts")
    differences: list[str] = Field(default_factory=list, description="Key differences found")


class BrandComparison(BaseModel):
    """Comparison result between two websites."""

    site1: BrandData = Field(description="Brand data from first site")
    site2: BrandData = Field(description="Brand data from second site")
    comparison: ComparisonMetrics = Field(description="Comparison metrics")
