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
        """Async pyppeteer generation with robust Mermaid rendering for full diagrams."""
        try:
            from pyppeteer import launch
            from pyppeteer.errors import TimeoutError
            
            filename = f"{class_name}_{method_name}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            # Create HTML content with Mermaid
            html_content = self._create_mermaid_html(mermaid_code, theme, width, height)
            
            # Launch browser with large initial viewport
            initial_width = max(width, 3000)
            initial_height = max(height, 2000)
            
            browser = await launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu'])
            page = await browser.newPage()
            
            # Set larger initial viewport
            await page.setViewport({'width': initial_width, 'height': initial_height})
            
            # Load HTML content
            await page.setContent(html_content)
            
            # Robust waiting for Mermaid to finish rendering
            max_wait_time = 30000  # 30 seconds
            start_time = time.time() * 1000  # Convert to milliseconds
            rendered = False
            
            while (time.time() * 1000) - start_time < max_wait_time:
                try:
                    # Check multiple conditions for successful rendering
                    status_text = await page.evaluate('document.getElementById("render-status")?.innerText || ""')
                    
                    # Check if rendering is complete
                    if "complete" in status_text.lower():
                        rendered = True
                        break
                    
                    # Check if SVG exists (fallback method)
                    try:
                        svg_count = await page.evaluate('document.querySelectorAll(".mermaid svg").length || 0')
                        if svg_count > 0:
                            rendered = True
                            break
                    except:
                        pass
                        
                except Exception:
                    # Status element not found yet, continue waiting
                    pass
                    
                # Wait a bit before checking again
                await page.waitFor(1000)
            
            # Additional fixed wait to ensure rendering is visually complete
            await page.waitFor(3000)
            
            if not rendered:
                self.logger.warning("Mermaid rendering may not be complete, proceeding with screenshot anyway")
            
            # Try to get the bounding box of the diagram
            element = await page.querySelector('.mermaid')
            if element:
                # Get the bounding box of the element
                bounding_box = await element.boundingBox()
                if bounding_box:
                    # Add generous padding
                    padding = 150
                    actual_width = max(int(bounding_box['width'] + 2 * padding), width, initial_width)
                    actual_height = max(int(bounding_box['height'] + 2 * padding), height, initial_height)
                    
                    # Set reasonable limits
                    max_width = 5000
                    max_height = 15000
                    actual_width = min(actual_width, max_width)
                    actual_height = min(actual_height, max_height)
                    
                    # Set viewport to fit the content
                    await page.setViewport({'width': actual_width, 'height': actual_height})
                    
                    # Wait a bit for the resize to take effect
                    await page.waitFor(2000)
                    
                    # Take screenshot of the full page to ensure we capture the entire diagram
                    await page.screenshot({'path': filepath, 'fullPage': True})
                else:
                    # If we can't get bounding box, take full page screenshot
                    await page.screenshot({'path': filepath, 'fullPage': True})
            else:
                # If we can't find the element, take full page screenshot
                await page.screenshot({'path': filepath, 'fullPage': True})
            
            await browser.close()
            
            self.logger.info(f"Generated PNG: {filepath}")
            return filepath
            
        except Exception as e:
            raise RuntimeError(f"Pyppeteer PNG generation failed: {str(e)}")
    
    def _generate_with_selenium(self, mermaid_code, class_name, method_name, width, height, theme):
        """Generate PNG using Selenium WebDriver with automatic sizing."""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            import time
            
            filename = f"{class_name}_{method_name}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            # Create HTML content with larger initial window
            html_content = self._create_mermaid_html(mermaid_code, theme, width, height)
            
            # Create temporary file with UTF-8 encoding
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                html_file = f.name
            
            try:
                # Setup Chrome options with large initial window
                initial_width = max(width, 3000)
                initial_height = max(height, 2000)
                
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--disable-extensions')
                chrome_options.add_argument('--disable-logging')
                chrome_options.add_argument('--silent')
                chrome_options.add_argument('--disable-background-timer-throttling')
                chrome_options.add_argument('--disable-renderer-backgrounding')
                chrome_options.add_argument('--disable-backgrounding-occluded-windows')
                chrome_options.add_argument(f'--window-size={initial_width},{initial_height}')
                
                # Try to create WebDriver
                try:
                    driver = webdriver.Chrome(options=chrome_options)
                except Exception as e:
                    self.logger.warning(f"Failed to create Chrome driver with options: {e}")
                    # Try with minimal options
                    try:
                        chrome_options = Options()
                        chrome_options.add_argument('--headless')
                        chrome_options.add_argument('--no-sandbox')
                        driver = webdriver.Chrome(options=chrome_options)
                    except Exception as e2:
                        self.logger.warning(f"Failed to create Chrome driver with minimal options: {e2}")
                        raise RuntimeError("Could not create Chrome WebDriver")
                
                try:
                    # Load HTML file
                    driver.get(f'file://{os.path.abspath(html_file)}')
                    
                    # Robust waiting for Mermaid to finish rendering
                    import time
                    max_wait_time = 45  # Increased to 45 seconds for complex diagrams
                    start_time = time.time()
                    rendered = False
                    
                    while time.time() - start_time < max_wait_time:
                        try:
                            # Check multiple conditions for successful rendering
                            status_element = driver.find_element(By.ID, "render-status")
                            status_text = status_element.text
                            
                            # Check if rendering is complete
                            if "complete" in status_text.lower() or "success" in status_text.lower():
                                rendered = True
                                break
                            
                            # Check if SVG exists (fallback method)
                            try:
                                svg_elements = driver.find_elements(By.CSS_SELECTOR, ".mermaid svg")
                                if len(svg_elements) > 0:
                                    # Additional check: make sure SVG has content
                                    svg_html = svg_elements[0].get_attribute("innerHTML")
                                    if svg_html and len(svg_html.strip()) > 0:
                                        rendered = True
                                        break
                            except:
                                pass
                                
                        except Exception:
                            # Status element not found yet, continue waiting
                            pass
                            
                        # Wait a bit before checking again
                        time.sleep(2)
                    
                    # Additional fixed wait to ensure rendering is visually complete
                    time.sleep(5)
                    
                    if not rendered:
                        self.logger.warning("Mermaid rendering may not be complete, proceeding with screenshot anyway")
                        # Even if not fully rendered, we'll try to capture what we can
                    
                    # Get the diagram element and its size
                    try:
                        diagram_element = driver.find_element(By.CSS_SELECTOR, ".mermaid")
                        diagram_size = diagram_element.size
                        
                        # Calculate required window size with generous padding
                        padding = 200  # Increased padding for complex diagrams
                        required_width = max(int(diagram_size['width'] + 2 * padding), width, initial_width)
                        required_height = max(int(diagram_size['height'] + 2 * padding), height, initial_height)
                        
                        # Set reasonable limits to prevent excessive memory usage
                        max_width = 6000
                        max_height = 20000
                        required_width = min(required_width, max_width)
                        required_height = min(required_height, max_height)
                        
                        # Log the sizing information
                        self.logger.info(f"Diagram size: {diagram_size['width']}x{diagram_size['height']}")
                        self.logger.info(f"Setting window size: {required_width}x{required_height}")
                        
                        # Resize window to fit diagram
                        driver.set_window_size(required_width, required_height)
                        
                        # Wait for resize to take effect
                        time.sleep(3)
                        
                        # Take full page screenshot
                        driver.save_screenshot(filepath)
                        
                        # Verify the screenshot was taken
                        if os.path.exists(filepath):
                            file_size = os.path.getsize(filepath)
                            self.logger.info(f"Screenshot saved successfully. File size: {file_size} bytes")
                        else:
                            raise RuntimeError("Screenshot file was not created")
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to get diagram size or resize window: {e}")
                        # Fallback to default screenshot with large window
                        driver.set_window_size(4000, 3000)
                        time.sleep(2)
                        driver.save_screenshot(filepath)
                    
                    self.logger.info(f"Generated PNG: {filepath}")
                    return filepath
                    
                finally:
                    driver.quit()
                
                driver.quit()
                
                self.logger.info(f"Generated PNG: {filepath}")
                return filepath
                
            finally:
                # Clean up temporary file
                # Commented out for debugging - keep HTML files for inspection
                # if os.path.exists(html_file):
                #     os.unlink(html_file)
                self.logger.info(f"Temporary HTML file kept for debugging: {html_file}")
                
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
        """Create HTML content with Mermaid for browser rendering with robust initialization."""
        # Properly handle encoding for Windows systems
        # For Chinese characters, we need to ensure proper escaping
        import html
        # Escape HTML special characters but preserve Mermaid syntax
        # We need to be careful not to escape Mermaid-specific characters
        escaped_mermaid_code = html.escape(mermaid_code, quote=False)
        # But we should not escape the arrow syntax
        escaped_mermaid_code = escaped_mermaid_code.replace('&gt;', '>')
        
        # Ensure proper line breaks in the Mermaid code
        # This is critical for Mermaid.js to parse the diagram correctly
        formatted_mermaid_code = escaped_mermaid_code
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Mermaid Diagram</title>
    <!-- Use a specific version of Mermaid to avoid compatibility issues -->
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.4.0/dist/mermaid.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: white;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }}
        .mermaid-container {{
            width: 100%;
            text-align: center;
        }}
        .mermaid {{
            width: 100%;
            max-width: 100%;
            display: inline-block;
            background: white;
            padding: 10px;
            box-sizing: border-box;
        }}
        #render-status {{
            margin: 10px 0;
            padding: 10px;
            background: #f0f0f0;
            border-radius: 4px;
            font-family: monospace;
        }}
    </style>
</head>
<body>
    <div id="render-status">Initializing Mermaid...</div>
    <div class="mermaid-container">
        <div class="mermaid">
{formatted_mermaid_code}
        </div>
    </div>
    <script>
        // Robust Mermaid initialization
        function initializeMermaid() {{
            try {{
                // Configure Mermaid with robust settings
                mermaid.initialize({{
                    startOnLoad: false,  // We'll call init manually
                    theme: '{theme}',
                    securityLevel: 'loose',
                    flowchart: {{
                        useMaxWidth: true,
                        htmlLabels: true,
                        curve: 'basis'  // Smooth curves
                    }},
                    fontFamily: 'inherit',
                    fontSize: 16,
                    logLevel: 4,  // Debug level
                    sequence: {{
                        diagramMarginX: 50,
                        diagramMarginY: 10,
                        actorMargin: 50
                    }},
                    // Important for Chinese characters
                    encoding: 'utf-8'
                }});
                
                // Update status
                document.getElementById('render-status').innerText = 'Mermaid configured, starting render...';
                
                // Render the diagram
                mermaid.run({{
                    querySelector: '.mermaid'
                }}).then(() => {{
                    document.getElementById('render-status').innerText = 'Mermaid rendering complete';
                    document.getElementById('render-status').style.background = '#d4edda';
                    document.getElementById('render-status').style.color = '#155724';
                }}).catch((error) => {{
                    document.getElementById('render-status').innerText = 'Mermaid rendering failed: ' + error;
                    document.getElementById('render-status').style.background = '#f8d7da';
                    document.getElementById('render-status').style.color = '#721c24';
                    console.error('Mermaid rendering error:', error);
                }});
            }} catch (error) {{
                document.getElementById('render-status').innerText = 'Mermaid initialization failed: ' + error;
                document.getElementById('render-status').style.background = '#f8d7da';
                document.getElementById('render-status').style.color = '#721c24';
                console.error('Mermaid initialization error:', error);
            }}
        }}
        
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', initializeMermaid);
        }} else {{
            // DOM is already ready
            initializeMermaid();
        }}
        
        // Additional fallback in case the above doesn't work
        window.addEventListener('load', function() {{
            if (document.getElementById('render-status').innerText === 'Initializing Mermaid...') {{
                setTimeout(initializeMermaid, 1000);
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