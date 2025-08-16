@echo off
REM Example usage of Java Mermaid Flowchart Generator

echo Java Mermaid Flowchart Generator Examples
echo ======================================

REM Change to the script directory
cd /d "%~dp0"

echo Example 1: Basic usage
echo java-mermaid.bat SampleJava simpleMethod SampleJava.java
echo.

echo Example 2: Generate only PNG images (no comments)
echo java-mermaid.bat SampleJava simpleMethod SampleJava.java --doc-off
echo.

echo Example 3: Generate only comments (no PNG)
echo java-mermaid.bat SampleJava simpleMethod SampleJava.java --pic-off
echo.

echo Example 4: Custom output directory
echo java-mermaid.bat SampleJava simpleMethod SampleJava.java --output-dir ./output/
echo.

echo Example 5: With custom API settings
echo java-mermaid.bat SampleJava simpleMethod SampleJava.java --api-endpoint https://api.moonshot.cn --model moonshot-v1-8k
echo.

echo Example 6: Verbose output for debugging
echo java-mermaid.bat SampleJava simpleMethod SampleJava.java --verbose
echo.

echo Notes:
echo - Replace "SampleJava", "simpleMethod", and "SampleJava.java" with your actual class, method, and file
echo - Make sure to set your API key using: set OPENAI_API_KEY=your-api-key-here
echo - Generated .mmd files contain clean Mermaid code for easy copy/paste to other tools
echo.

pause