"""Google Generative AI (Gemini) service for code generation."""

import base64
import os
from typing import Optional

import google.generativeai as genai

from ..schemas.brand import BrandData, GeneratedCode


class GeminiService:
    """Async client for Google Generative AI (Gemini)."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Gemini service.

        Args:
            api_key: Google API key. If not provided, reads from GOOGLE_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY is required")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-lite")

    def _brand_to_css_variables(self, brand: BrandData) -> str:
        """Convert brand data to CSS custom properties."""
        css_vars = []
        css_vars.append(f"  --color-primary: {brand.colors.primary};")
        if brand.colors.secondary:
            css_vars.append(f"  --color-secondary: {brand.colors.secondary};")
        if brand.colors.accent:
            css_vars.append(f"  --color-accent: {brand.colors.accent};")
        if brand.colors.background:
            css_vars.append(f"  --color-background: {brand.colors.background};")
        if brand.colors.text:
            css_vars.append(f"  --color-text: {brand.colors.text};")

        css_vars.append(f"  --font-heading: {brand.typography.headings};")
        css_vars.append(f"  --font-body: {brand.typography.body};")
        css_vars.append(f"  --spacing-grid: {brand.spacing.grid};")

        if brand.buttons.primary:
            css_vars.append(f"  --btn-primary-bg: {brand.buttons.primary.bg};")
            css_vars.append(f"  --btn-primary-text: {brand.buttons.primary.text};")
            css_vars.append(f"  --btn-primary-radius: {brand.buttons.primary.border_radius};")

        return "\n".join(css_vars)

    async def generate_replica(
        self,
        brand_data: BrandData,
        component_type: str = "landing_page",
        customization: str = "",
    ) -> GeneratedCode:
        """Generate HTML/CSS using brand data.

        Args:
            brand_data: Extracted brand data
            component_type: Type of component to generate
            customization: Additional instructions

        Returns:
            Generated HTML and CSS code
        """
        css_variables = self._brand_to_css_variables(brand_data)

        prompt = f"""Generate a {component_type} component using these brand specifications:

BRAND DATA:
- Primary Color: {brand_data.colors.primary}
- Secondary Color: {brand_data.colors.secondary or 'N/A'}
- Accent Color: {brand_data.colors.accent or 'N/A'}
- Background: {brand_data.colors.background or '#ffffff'}
- Text Color: {brand_data.colors.text or '#000000'}
- Heading Font: {brand_data.typography.headings}
- Body Font: {brand_data.typography.body}
- Button Style: {brand_data.buttons.primary.model_dump() if brand_data.buttons.primary else 'Default'}

CSS VARIABLES (use these):
:root {{
{css_variables}
}}

COMPONENT TYPE: {component_type}

{f"ADDITIONAL INSTRUCTIONS: {customization}" if customization else ""}

REQUIREMENTS:
1. Generate clean, semantic HTML5
2. Generate CSS that uses the provided CSS variables
3. Make the component responsive
4. Use modern CSS (flexbox/grid)
5. Include hover states for interactive elements

OUTPUT FORMAT:
Return the response in this exact format:
---HTML---
[Your HTML code here]
---CSS---
[Your CSS code here]
---END---
"""

        response = await self.model.generate_content_async(prompt)
        text = response.text

        # Parse the response
        html = ""
        css = ""

        if "---HTML---" in text and "---CSS---" in text:
            parts = text.split("---HTML---")
            if len(parts) > 1:
                html_part = parts[1].split("---CSS---")[0].strip()
                html = html_part

            if "---CSS---" in text:
                css_parts = text.split("---CSS---")
                if len(css_parts) > 1:
                    css_part = css_parts[1].split("---END---")[0].strip()
                    css = css_part
        else:
            # Fallback: try to extract code blocks
            if "```html" in text:
                html = text.split("```html")[1].split("```")[0].strip()
            if "```css" in text:
                css = text.split("```css")[1].split("```")[0].strip()

        # Add CSS variables to the CSS
        full_css = f""":root {{
{css_variables}
}}

{css}"""

        # Create preview URL (data URL)
        preview_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{full_css}</style>
</head>
<body>
{html}
</body>
</html>"""

        preview_url = f"data:text/html;base64,{base64.b64encode(preview_html.encode()).decode()}"

        return GeneratedCode(
            html=html,
            css=full_css,
            preview_url=preview_url,
            component_type=component_type,
        )

    async def generate_from_template(
        self,
        brand_data: BrandData,
        template_type: str,
    ) -> GeneratedCode:
        """Generate HTML/CSS for a specific template type.

        Args:
            brand_data: Extracted brand data
            template_type: One of: hero_section, pricing_table, feature_grid, testimonial, cta

        Returns:
            Generated HTML and CSS code
        """
        template_prompts = {
            "hero_section": "Create a hero section with a headline, subheadline, CTA button, and optional image placeholder",
            "pricing_table": "Create a 3-tier pricing table with features, prices, and CTA buttons",
            "feature_grid": "Create a 3-column feature grid with icons (use emoji placeholders), titles, and descriptions",
            "testimonial": "Create a testimonial section with quote, author name, role, and company",
            "cta": "Create a call-to-action section with headline, description, and primary button",
        }

        customization = template_prompts.get(
            template_type,
            f"Create a {template_type} component"
        )

        return await self.generate_replica(brand_data, template_type, customization)

    async def calculate_color_similarity(self, color1: str, color2: str) -> float:
        """Calculate similarity between two colors.

        Args:
            color1: First color in hex format
            color2: Second color in hex format

        Returns:
            Similarity score between 0 and 1
        """
        def hex_to_rgb(hex_color: str) -> tuple:
            hex_color = hex_color.lstrip("#")
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        try:
            rgb1 = hex_to_rgb(color1)
            rgb2 = hex_to_rgb(color2)

            # Calculate Euclidean distance in RGB space
            distance = sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)) ** 0.5
            max_distance = (255 ** 2 * 3) ** 0.5  # Max possible distance

            similarity = 1 - (distance / max_distance)
            return round(similarity, 3)
        except (ValueError, IndexError):
            return 0.0
