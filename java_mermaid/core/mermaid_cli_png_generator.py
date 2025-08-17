"""
Mermaid PNG Generator for creating flowchart images.

Provides multiple approaches for generating PNG images from Mermaid diagrams:
1. Mermaid CLI (if dependencies are available)
2. Selenium with Chrome/Chromium (if browser is available)
3. No PNG generation if high-quality rendering is not available
"""

import os
import platform
import tempfile
from typing import Optional
from java_mermaid.utils.logger import get_logger


class MermaidPNGGenerator:
    """
    PNG generator that creates flowchart images from Mermaid code
    using multiple approaches based on environment capabilities.
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
        
        # Check available rendering methods
        self._detect_rendering_methods()
    
    def _detect_rendering_methods(self):
        """Detect available rendering methods based on environment."""
        self.mermaid_cli_available = self._check_mermaid_cli()
        self.selenium_available = self._check_selenium()
        
        self.logger.info(f"Available rendering methods:")
        self.logger.info(f"  Mermaid CLI: {self.mermaid_cli_available}")
        self.logger.info(f"  Selenium: {self.selenium_available}")
    
    def _check_mermaid_cli(self) -> bool:
        """Check if Mermaid CLI is available and working."""
        try:
            import subprocess
            result = subprocess.run(
                ["npx", "mmdc", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError, Exception):
            return False
    
    def _check_selenium(self) -> bool:
        """Check if Selenium is available."""
        try:
            import selenium
            from selenium import webdriver
            return True
        except ImportError:
            return False
    
    def generate_png(
        self,
        mermaid_code: str,
        class_name: str,
        method_name: str,
        width: int = 1200,
        height: int = 800,
        theme: str = "default"
    ) -> Optional[str]:
        """
        Generate PNG image from Mermaid diagram code.
        
        Args:
            mermaid_code: Mermaid diagram code
            class_name: Name of the Java class
            method_name: Name of the Java method
            width: Image width in pixels
            height: Image height in pixels
            theme: Mermaid theme (default, forest, dark, neutral)
            
        Returns:
            Path to the generated PNG file, or None if PNG generation failed
            
        Raises:
            RuntimeError: If PNG generation fails
        """
        filename = f"{class_name}_{method_name}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        # Handle long filenames
        if len(filename) > 200:
            import hashlib
            hash_suffix = hashlib.md5(f"{class_name}_{method_name}".encode()).hexdigest()[:8]
            filename = f"{class_name[:50]}_{method_name[:50]}_{hash_suffix}.png"
            filepath = os.path.join(self.output_dir, filename)
        
        try:
            self.logger.info(f"Generating PNG: {filepath}")
            
            # Try different rendering methods in order of preference
            if self.mermaid_cli_available:
                try:
                    self.logger.debug("Attempting to use Mermaid CLI for PNG generation")
                    return self._generate_with_mermaid_cli(mermaid_code, filepath, width, height, theme)
                except Exception as e:
                    self.logger.warning(f"Mermaid CLI failed: {str(e)}")
            
            if self.selenium_available:
                try:
                    self.logger.debug("Attempting to use Selenium for PNG generation")
                    return self._generate_with_selenium(mermaid_code, filepath, width, height, theme)
                except Exception as e:
                    self.logger.warning(f"Selenium failed: {str(e)}")
            
            # If no rendering method is available, skip PNG generation
            self.logger.info("Skipping PNG generation - no rendering method available")
            return None
                
        except Exception as e:
            raise RuntimeError(f"PNG generation failed: {str(e)}")
    
    def _generate_with_mermaid_cli(
        self, 
        mermaid_code: str, 
        filepath: str, 
        width: int, 
        height: int, 
        theme: str
    ) -> str:
        """
        Generate PNG using Mermaid CLI with optimal sizing for full diagrams.
        
        Args:
            mermaid_code: Mermaid diagram code
            filepath: Output file path
            width: Preferred minimum width
            height: Preferred minimum height
            theme: Mermaid theme
            
        Returns:
            Path to the generated PNG file
        """
        try:
            import subprocess
            
            # Create temporary mermaid file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
                f.write(mermaid_code)
                mermaid_file = f.name
            
            try:
                # Calculate optimal dimensions for the CLI
                # Mermaid CLI works better with explicit sizing
                optimal_width = max(width, 2000)
                optimal_height = max(height, 1500)
                
                # Try with optimal dimensions first
                cmd = [
                    "npx", "mmdc",
                    "-i", mermaid_file,
                    "-o", filepath,
                    "-w", str(optimal_width),
                    "-H", str(optimal_height),
                    "-t", theme,
                    "-s", "2",  # Scale factor for better quality
                    "-b", "white"  # Background color
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60  # Increased timeout for complex diagrams
                )
                
                if result.returncode == 0:
                    self.logger.info(f"Successfully generated PNG using Mermaid CLI: {filepath}")
                    # Also save clean mermaid code file
                    self._save_clean_mermaid_code(mermaid_code, filepath)
                    return filepath
                else:
                    # Try with auto-sizing if explicit sizing fails
                    cmd_auto = [
                        "npx", "mmdc",
                        "-i", mermaid_file,
                        "-o", filepath,
                        "-t", theme,
                        "-b", "white"
                    ]
                    
                    result_auto = subprocess.run(
                        cmd_auto,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    if result_auto.returncode == 0:
                        self.logger.info(f"Successfully generated PNG using Mermaid CLI with auto-sizing: {filepath}")
                        # Also save clean mermaid code file
                        self._save_clean_mermaid_code(mermaid_code, filepath)
                        return filepath
                    else:
                        # Last resort: try with conservative dimensions
                        cmd_conservative = [
                            "npx", "mmdc",
                            "-i", mermaid_file,
                            "-o", filepath,
                            "-w", str(max(width, 1200)),
                            "-H", str(max(height, 800)),
                            "-t", theme,
                            "-b", "white"
                        ]
                        
                        result_conservative = subprocess.run(
                            cmd_conservative,
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        
                        if result_conservative.returncode == 0:
                            self.logger.info(f"Successfully generated PNG using Mermaid CLI with conservative size: {filepath}")
                            # Also save clean mermaid code file
                            self._save_clean_mermaid_code(mermaid_code, filepath)
                            return filepath
                        else:
                            raise RuntimeError(f"Mermaid CLI failed:\nSTDOUT: {result_conservative.stdout}\nSTDERR: {result_conservative.stderr}")
                    
            finally:
                # Clean up temporary file
                if os.path.exists(mermaid_file):
                    os.remove(mermaid_file)
                    
        except subprocess.TimeoutExpired:
            raise RuntimeError("Mermaid CLI timed out - diagram may be too complex")
        except Exception as e:
            raise RuntimeError(f"Mermaid CLI rendering failed: {str(e)}")
    
    def _generate_with_selenium(
        self, 
        mermaid_code: str, 
        filepath: str, 
        width: int, 
        height: int, 
        theme: str
    ) -> str:
        """
        Generate PNG using Selenium browser automation with robust Mermaid rendering and full diagram capture.
        
        Args:
            mermaid_code: Mermaid diagram code
            filepath: Output file path
            width: Preferred minimum width
            height: Preferred minimum height
            theme: Mermaid theme
            
        Returns:
            Path to the generated PNG file
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            import tempfile
            import time
            
            # Create HTML content with Mermaid diagram
            html_content = self._create_mermaid_html(mermaid_code, theme)
            
            # Create temporary HTML file with UTF-8 encoding
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                html_file = f.name
            
            try:
                # Setup Chrome options with large initial window
                initial_width = max(width, 3000)
                initial_height = max(height, 2000)
                
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument("--disable-logging")
                chrome_options.add_argument("--silent")
                chrome_options.add_argument("--disable-background-timer-throttling")
                chrome_options.add_argument("--disable-renderer-backgrounding")
                chrome_options.add_argument("--disable-backgrounding-occluded-windows")
                chrome_options.add_argument(f"--window-size={initial_width},{initial_height}")
                
                # Try to create WebDriver
                try:
                    driver = webdriver.Chrome(options=chrome_options)
                except Exception as e:
                    self.logger.warning(f"Failed to create Chrome driver with options: {e}")
                    # Try with minimal options
                    try:
                        chrome_options = Options()
                        chrome_options.add_argument("--headless")
                        chrome_options.add_argument("--no-sandbox")
                        driver = webdriver.Chrome(options=chrome_options)
                    except Exception as e2:
                        self.logger.warning(f"Failed to create Chrome driver with minimal options: {e2}")
                        raise RuntimeError("Could not create Chrome WebDriver")
                
                try:
                    # Load the HTML file with UTF-8 encoding
                    driver.get(f"file://{os.path.abspath(html_file)}")
                    
                    # Robust waiting for Mermaid to finish rendering
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
                    
                    self.logger.info(f"Successfully generated PNG using Selenium: {filepath}")
                    # Also save clean mermaid code file with UTF-8 encoding
                    self._save_clean_mermaid_code(mermaid_code, filepath)
                    return filepath
                    
                finally:
                    driver.quit()
                    
            finally:
                # Clean up temporary file
                # Commented out for debugging - keep HTML files for inspection
                # if os.path.exists(html_file):
                #     os.remove(html_file)
                self.logger.info(f"Temporary HTML file kept for debugging: {html_file}")
                    
        except Exception as e:
            self.logger.error(f"Selenium rendering failed: {str(e)}")
            raise RuntimeError(f"Selenium rendering failed: {str(e)}")
    
    def _save_clean_mermaid_code(self, mermaid_code: str, png_filepath: str) -> None:
        """
        Save clean Mermaid code to a separate .mmd file.
        
        Args:
            mermaid_code: Mermaid diagram code
            png_filepath: Path to the generated PNG file
        """
        try:
            # Create .mmd file path
            mmd_filepath = os.path.splitext(png_filepath)[0] + ".mmd"
            
            # Write clean mermaid code
            with open(mmd_filepath, 'w', encoding='utf-8') as f:
                f.write(mermaid_code)
            
            self.logger.info(f"Saved clean Mermaid code to: {mmd_filepath}")
        except Exception as e:
            self.logger.warning(f"Failed to save clean Mermaid code: {str(e)}")
    
    def _create_mermaid_html(self, mermaid_code: str, theme: str) -> str:
        """
        Create HTML content for rendering Mermaid diagram with robust initialization.
        
        Args:
            mermaid_code: Mermaid diagram code
            theme: Mermaid theme
            
        Returns:
            HTML content as string
        """
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
    
    def _save_clean_mermaid_code(self, mermaid_code: str, png_filepath: str) -> None:
        """
        Save clean Mermaid code to a separate .mmd file.
        
        Args:
            mermaid_code: Mermaid diagram code
            png_filepath: Path to the generated PNG file
        """
        try:
            # Create .mmd file path
            mmd_filepath = os.path.splitext(png_filepath)[0] + ".mmd"
            
            # Write clean mermaid code
            with open(mmd_filepath, 'w', encoding='utf-8') as f:
                f.write(mermaid_code)
            
            self.logger.info(f"Saved clean Mermaid code to: {mmd_filepath}")
        except Exception as e:
            self.logger.warning(f"Failed to save clean Mermaid code: {str(e)}")
    
    def is_available(self) -> bool:
        """
        Check if any PNG generation method is available.
        
        Returns:
            True if PNG generation is available, False otherwise
        """
        return self.mermaid_cli_available or self.selenium_available