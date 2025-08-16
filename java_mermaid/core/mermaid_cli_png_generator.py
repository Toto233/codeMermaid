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
        Generate PNG using Mermaid CLI.
        
        Args:
            mermaid_code: Mermaid diagram code
            filepath: Output file path
            width: Image width
            height: Image height
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
                # Run mermaid CLI
                cmd = [
                    "npx", "mmdc",
                    "-i", mermaid_file,
                    "-o", filepath,
                    "-w", str(width),
                    "-H", str(height),
                    "-t", theme
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    self.logger.info(f"Successfully generated PNG using Mermaid CLI: {filepath}")
                    # Also save clean mermaid code file
                    self._save_clean_mermaid_code(mermaid_code, filepath)
                    return filepath
                else:
                    raise RuntimeError(f"Mermaid CLI failed: {result.stderr}")
                    
            finally:
                # Clean up temporary file
                if os.path.exists(mermaid_file):
                    os.remove(mermaid_file)
                    
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
        Generate PNG using Selenium browser automation.
        
        Args:
            mermaid_code: Mermaid diagram code
            filepath: Output file path
            width: Image width
            height: Image height
            theme: Mermaid theme
            
        Returns:
            Path to the generated PNG file
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            import tempfile
            
            # Create HTML content with Mermaid diagram
            html_content = self._create_mermaid_html(mermaid_code, theme)
            
            # Create temporary HTML file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                f.write(html_content)
                html_file = f.name
            
            try:
                # Setup Chrome options
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument(f"--window-size={width},{height}")
                
                # Try to create WebDriver
                try:
                    driver = webdriver.Chrome(options=chrome_options)
                except Exception:
                    # Try with default options
                    driver = webdriver.Chrome()
                
                try:
                    # Load the HTML file
                    driver.get(f"file://{os.path.abspath(html_file)}")
                    
                    # Wait a bit for rendering
                    import time
                    time.sleep(2)
                    
                    # Take screenshot
                    driver.save_screenshot(filepath)
                    
                    self.logger.info(f"Successfully generated PNG using Selenium: {filepath}")
                    # Also save clean mermaid code file
                    self._save_clean_mermaid_code(mermaid_code, filepath)
                    return filepath
                    
                finally:
                    driver.quit()
                    
            finally:
                # Clean up temporary file
                if os.path.exists(html_file):
                    os.remove(html_file)
                    
        except Exception as e:
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
        Create HTML content for rendering Mermaid diagram.
        
        Args:
            mermaid_code: Mermaid diagram code
            theme: Mermaid theme
            
        Returns:
            HTML content as string
        """
        return f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: white;
        }}
        .mermaid {{
            width: 100%;
            height: 100%;
        }}
    </style>
</head>
<body>
    <div class="mermaid">
{mermaid_code}
    </div>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: '{theme}',
            securityLevel: 'loose'
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