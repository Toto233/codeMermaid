"""
Pure Python PNG generator for Mermaid diagrams.

Uses pyppeteer or selenium to generate PNG images from Mermaid code
without requiring mermaid-cli (npm).
"""

import asyncio
import tempfile
import os
from typing import Optional
from java_mermaid.utils.logger import get_logger


class PythonPNGGenerator:
    """
    Pure Python PNG generator that uses browser automation to render Mermaid diagrams.
    
    Supports multiple backends:
    1. Pyppeteer (headless Chrome)
    2. Selenium (Chrome/Firefox)
    3. Fallback to SVG generation
    """
    
    def __init__(self, output_dir: str = ".", verbose: bool = False):
        """
        Initialize the PNG generator.
        
        Args:
            output_dir: Directory for output files
            verbose: Enable verbose logging
        """
        self.output_dir = output_dir
        self.logger = get_logger(verbose=verbose)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_png(
        self,
        mermaid_code: str,
        class_name: str,
        method_name: str,
        width: int = 1200,
        height: int = 800,
        theme: str = "default"
    ) -> str:
        """
        Generate PNG using pure Python approach.
        
        Args:
            mermaid_code: Mermaid diagram code
            class_name: Name of the Java class
            method_name: Name of the Java method
            width: Image width in pixels
            height: Image height in pixels
            theme: Mermaid theme
            
        Returns:
            Path to the generated PNG file
            
        Raises:
            RuntimeError: If no suitable backend is available
        """
        try:
            # Try pyppeteer first
            return self._generate_with_pyppeteer(
                mermaid_code, class_name, method_name, width, height, theme
            )
        except ImportError:
            self.logger.warning("Pyppeteer not available, trying selenium...")
            try:
                return self._generate_with_selenium(
                    mermaid_code, class_name, method_name, width, height, theme
                )
            except ImportError:
                self.logger.warning("Selenium not available, generating SVG fallback...")
                return self._generate_svg_fallback(
                    mermaid_code, class_name, method_name, theme
                )
    
    def _generate_with_pyppeteer(self, mermaid_code, class_name, method_name, width, height, theme):
        """Generate PNG using pyppeteer (headless Chrome)."""
        try:
            import pyppeteer
        except ImportError:
            raise ImportError("pyppeteer not available")
        
        return asyncio.run(self._generate_with_pyppeteer_async(
            mermaid_code, class_name, method_name, width, height, theme
        ))
    
    async def _generate_with_pyppeteer_async(self, mermaid_code, class_name, method_name, width, height, theme):
        """Async pyppeteer generation."""
        try:
            from pyppeteer import launch
            
            filename = f"{class_name}_{method_name}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            # Create HTML content with Mermaid
            html_content = self._create_mermaid_html(mermaid_code, theme, width, height)
            
            # Launch browser
            browser = await launch(headless=True, args=['--no-sandbox'])
            page = await browser.newPage()
            
            # Set viewport
            await page.setViewport({'width': width, 'height': height})
            
            # Load HTML content
            await page.setContent(html_content)
            
            # Wait for Mermaid to render
            await page.waitForSelector('#mermaid-diagram svg', timeout=10000)
            
            # Take screenshot
            element = await page.querySelector('#mermaid-diagram')
            await element.screenshot({'path': filepath})
            
            await browser.close()
            
            self.logger.info(f"Generated PNG: {filepath}")
            return filepath
            
        except Exception as e:
            raise RuntimeError(f"Pyppeteer PNG generation failed: {str(e)}")
    
    def _generate_with_selenium(self, mermaid_code, class_name, method_name, width, height, theme):
        """Generate PNG using Selenium WebDriver."""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            filename = f"{class_name}_{method_name}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            # Create HTML content
            html_content = self._create_mermaid_html(mermaid_code, theme, width, height)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                f.write(html_content)
                html_file = f.name
            
            try:
                # Setup Chrome options
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument(f'--window-size={width},{height}')
                
                # Initialize driver
                driver = webdriver.Chrome(options=chrome_options)
                
                # Load HTML file
                driver.get(f'file://{html_file}')
                
                # Wait for Mermaid to render
                driver.implicitly_wait(5)
                
                # Take screenshot
                element = driver.find_element('id', 'mermaid-diagram')
                element.screenshot(filepath)
                
                driver.quit()
                
                self.logger.info(f"Generated PNG: {filepath}")
                return filepath
                
            finally:
                # Clean up temporary file
                os.unlink(html_file)
                
        except ImportError:
            raise ImportError("selenium not available")
        except Exception as e:
            raise RuntimeError(f"Selenium PNG generation failed: {str(e)}")
    
    def _generate_svg_fallback(self, mermaid_code, class_name, method_name, theme):
        """Generate SVG as fallback when no browser automation is available."""
        filename = f"{class_name}_{method_name}.svg"
        filepath = os.path.join(self.output_dir, filename)
        
        # Create SVG content with embedded Mermaid
        svg_content = self._create_mermaid_svg(mermaid_code, theme)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        self.logger.info(f"Generated SVG fallback: {filepath}")
        return filepath
    
    def _create_mermaid_html(self, mermaid_code: str, theme: str, width: int, height: int) -> str:
        """Create HTML content with Mermaid for browser rendering."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Mermaid Diagram</title>
            <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
            <style>
                body {{ margin: 0; padding: 20px; background: white; }}
                #mermaid-diagram {{ width: {width}px; height: {height}px; }}
            </style>
        </head>
        <body>
            <div id="mermaid-diagram" class="mermaid">
                {mermaid_code}
            </div>
            <script>
                mermaid.initialize({{
                    startOnLoad: true,
                    theme: '{theme}',
                    flowchart: {{
                        useMaxWidth: false,
                        htmlLabels: true
                    }}
                }});
            </script>
        </body>
        </html>
        """
    
    def _create_mermaid_svg(self, mermaid_code: str, theme: str) -> str:
        """Create SVG content with embedded Mermaid (basic fallback)."""
        return f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">
            <defs>
                <style>
                    .mermaid {{
                        font-family: Arial, sans-serif;
                        font-size: 14px;
                    }}
                    .node rect {{
                        fill: #f9f9f9;
                        stroke: #333;
                        stroke-width: 1px;
                    }}
                </style>
            </defs>
            <text x="400" y="300" text-anchor="middle" class="mermaid">
                Mermaid diagram will be rendered here:
                </tspan>
                <tspan x="400" dy="20">{repr(mermaid_code)}</tspan>
            </text>
        </svg>
        """
    
    def is_available(self) -> bool:
        """Check if any PNG generation backend is available."""
        try:
            import pyppeteer
            return True
        except ImportError:
            try:
                import selenium
                return True
            except ImportError:
                return False
    
    def get_required_packages(self) -> list:
        """Get list of required packages for PNG generation."""
        return [
            "pyppeteer (recommended)",
            "selenium-webdriver (alternative)",
            "Pillow (for SVG to PNG conversion)"
        ]