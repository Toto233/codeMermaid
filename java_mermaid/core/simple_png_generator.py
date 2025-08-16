"""
Simple Python PNG generator for Mermaid diagrams using PIL/Pillow.

Creates basic PNG images from Mermaid flowcharts without external dependencies.
"""

import os
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Dict, List, Tuple
from java_mermaid.utils.logger import get_logger


class SimplePNGGenerator:
    """
    Simple PNG generator that creates basic flowchart images from Mermaid code.
    
    Parses simple Mermaid flowcharts and creates PNG images using PIL/Pillow.
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
        
        # Colors for different elements
        self.colors = {
            'background': '#ffffff',
            'node': '#e1f5fe',
            'decision': '#fff3e0',
            'edge': '#333333',
            'text': '#000000',
            'start_end': '#c8e6c9'
        }
    
    def generate_png(
        self,
        mermaid_code: str,
        class_name: str,
        method_name: str,
        width: int = 1200,
        height: int = 800
    ) -> str:
        """
        Generate PNG image from Mermaid flowchart code.
        
        Args:
            mermaid_code: Mermaid diagram code
            class_name: Name of the Java class
            method_name: Name of the Java method
            width: Image width in pixels
            height: Image height in pixels
            
        Returns:
            Path to the generated PNG file
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
            
            # Parse Mermaid code and create flowchart
            nodes, edges = self._parse_mermaid_flowchart(mermaid_code)
            
            # Create PNG
            self._create_flowchart_png(nodes, edges, filepath, width, height, class_name, method_name, mermaid_code)
            
            self.logger.info(f"Successfully generated PNG: {filepath}")
            return filepath
            
        except Exception as e:
            # Create a simple text-based PNG as fallback
            return self._create_text_png(mermaid_code, class_name, method_name, filepath)
    
    def _parse_mermaid_flowchart(self, mermaid_code: str) -> Tuple[List[Dict], List[Dict]]:
        """Parse Mermaid flowchart into nodes and edges."""
        nodes = []
        edges = []
        
        lines = [line.strip() for line in mermaid_code.split('\n') if line.strip()]
        
        # Skip flowchart/graph TD declaration and class definitions
        content_lines = [line for line in lines 
                        if not line.lower().startswith('flowchart') 
                        and not line.lower().startswith('graph')
                        and not line.startswith('```')
                        and not line.startswith('classDef')
                        and not line.startswith('class ')]
        
        node_map = {}
        
        # First pass: collect all nodes
        for line in content_lines:
            if '-->' not in line:
                node = self._parse_node(line)
                if node:
                    nodes.append(node)
                    node_map[node['id']] = node
        
        # Second pass: collect all edges
        for line in content_lines:
            if '-->' in line:
                edge = self._parse_edge(line)
                if edge:
                    edges.append(edge)
                    # Ensure start/end nodes exist
                    if edge['source'] not in node_map:
                        nodes.append({'id': edge['source'], 'label': edge['source'], 'type': 'process'})
                        node_map[edge['source']] = nodes[-1]
                    if edge['target'] not in node_map:
                        nodes.append({'id': edge['target'], 'label': edge['target'], 'type': 'process'})
                        node_map[edge['target']] = nodes[-1]
        
        return nodes, edges
    
    def _parse_node(self, line: str) -> Optional[Dict]:
        """Parse a single node from Mermaid syntax."""
        line = line.strip()
        if not line or line.startswith('%%'):
            return None
            
        # Remove comments
        if '%%' in line:
            line = line.split('%%')[0].strip()
        
        # Parse different node types
        node = None
        
        # Remove edge arrows if present
        if '--' in line:
            return None
            
        # Parse node definitions like: A[label] or A((label)) or A{label}
        
        # Circle (( )) or (())
        if '((' in line and '))' in line:
            start = line.find('((')
            end = line.find('))')
            if start < end:
                match = line[start+2:end]
                node_id = line[:start].strip()
                node = {'id': node_id, 'label': match, 'type': 'start_end'}
        
        # Diamond {{ }}
        elif '{{' in line and '}}' in line:
            start = line.find('{{')
            end = line.find('}}')
            if start < end:
                match = line[start+2:end]
                node_id = line[:start].strip()
                node = {'id': node_id, 'label': match, 'type': 'decision'}
        
        # Rectangle [ ] or [[ ]]
        elif '[' in line and ']' in line:
            start = line.find('[')
            end = line.rfind(']')
            if start < end:
                match = line[start+1:end]
                node_id = line[:start].strip()
                node = {'id': node_id, 'label': match, 'type': 'process'}
        
        return node
    
    def _parse_edge(self, line: str) -> Optional[Dict]:
        """Parse an edge from Mermaid syntax."""
        line = line.strip()
        if '-->' not in line:
            return None
            
        # Split on arrow
        parts = line.split('-->')
        if len(parts) < 2:
            return None
            
        source = parts[0].strip()
        
        # Parse target and label
        target_part = parts[1].strip()
        label = ""
        
        # Handle labels like: A -->|label| B or A --> B
        if '|' in target_part and ']' in target_part:
            # Has label
            label_start = target_part.find('|')
            label_end = target_part.find('|', label_start + 1)
            if label_start < label_end:
                label = target_part[label_start+1:label_end]
                target = target_part[label_end+1:].strip()
            else:
                target = target_part
        else:
            target = target_part
            
        # Clean up target (remove brackets, etc)
        target = target.split('[')[0].split('{')[0].split('(')[0].strip()
        
        return {
            'source': source,
            'target': target,
            'label': label
        }
    
    def _create_flowchart_png(self, nodes: List[Dict], edges: List[Dict], filepath: str, width: int, height: int, class_name: str, method_name: str, mermaid_code: str):
        """Create a PNG flowchart from parsed nodes and edges."""
        # Create image
        img = Image.new('RGB', (width, height), color=self.colors['background'])
        draw = ImageDraw.Draw(img)
        
        # Try to use a font
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
            title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
        except:
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()
        
        # Add title
        title = f"{class_name}.{method_name}()"
        draw.text((width//2, 20), title, fill=self.colors['text'], font=title_font, anchor='mm')
        
        # Create proper flowchart from Mermaid code
        self._create_proper_flowchart(draw, nodes, edges, width, height, font, class_name, method_name)
        
        # Save image
        img.save(filepath)
    
    def _create_proper_flowchart(self, draw: ImageDraw.Draw, nodes: List[Dict], edges: List[Dict], width: int, height: int, font, class_name: str, method_name: str):
        """Create a proper visual flowchart with nodes and connections."""
        if not nodes:
            self._create_flowchart_from_mermaid_direct(draw, width, height, font)
            return
            
        # Calculate positions for nodes
        positions = {}
        start_x, start_y = 100, 80
        node_width, node_height = 140, 50
        
        # Simple linear layout for now
        current_y = start_y
        for i, node in enumerate(nodes):
            x_center = width // 2
            y_pos = start_y + i * 100
            positions[node['id']] = (x_center, y_pos)
            
            # Draw node based on type
            self._draw_node(draw, node, x_center, y_pos, node_width, node_height, font)
        
        # Draw edges between nodes
        for edge in edges:
            if edge['source'] in positions and edge['target'] in positions:
                self._draw_edge(draw, positions[edge['source']], positions[edge['target']], edge['label'], font)
    
    def _draw_node(self, draw: ImageDraw.Draw, node: Dict, x: int, y: int, width: int, height: int, font):
        """Draw a single node in the flowchart."""
        left = x - width // 2
        top = y - height // 2
        right = x + width // 2
        bottom = y + height // 2
        
        node_type = node.get('type', 'process')
        
        if node_type == 'start_end':
            # Draw oval for start/end
            draw.ellipse([left, top, right, bottom], fill=self.colors['start_end'], outline=self.colors['edge'], width=2)
        elif node_type == 'decision':
            # Draw diamond for decision
            diamond_points = [
                (x, top),
                (right, y),
                (x, bottom),
                (left, y)
            ]
            draw.polygon(diamond_points, fill=self.colors['decision'], outline=self.colors['edge'], width=2)
        else:
            # Draw rectangle for process
            draw.rectangle([left, top, right, bottom], fill=self.colors['node'], outline=self.colors['edge'], width=2)
        
        # Center text
        text_bbox = draw.textbbox((0, 0), node['label'], font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = x - text_width // 2
        text_y = y - text_height // 2
        
        draw.text((text_x, text_y), node['label'], fill=self.colors['text'], font=font)
    
    def _draw_edge(self, draw: ImageDraw.Draw, start: Tuple[int, int], end: Tuple[int, int], label: str, font):
        """Draw an edge between nodes."""
        # Draw line
        draw.line([start, end], fill=self.colors['edge'], width=2)
        
        # Draw arrow
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        if abs(dx) > abs(dy):
            # Horizontal arrow
            if dx > 0:
                arrow_points = [(end[0]-10, end[1]-5), (end[0]-10, end[1]+5), end]
            else:
                arrow_points = [(end[0]+10, end[1]-5), (end[0]+10, end[1]+5), end]
        else:
            # Vertical arrow
            if dy > 0:
                arrow_points = [(end[0]-5, end[1]-10), (end[0]+5, end[1]-10), end]
            else:
                arrow_points = [(end[0]-5, end[1]+10), (end[0]+5, end[1]+10), end]
        
        draw.polygon(arrow_points, fill=self.colors['edge'])
        
        # Draw label if provided
        if label:
            mid_x = (start[0] + end[0]) // 2
            mid_y = (start[1] + end[1]) // 2
            draw.text((mid_x, mid_y), label, fill=self.colors['text'], font=font)
    
    def _create_flowchart_from_mermaid_direct(self, draw: ImageDraw.Draw, width: int, height: int, font):
        """Create a basic flowchart when no nodes were parsed."""
        # Draw a simple start -> process -> end flow
        start_x, start_y = width // 2, 100
        process_x, process_y = width // 2, 250
        end_x, end_y = width // 2, 400
        
        node_width, node_height = 120, 50
        
        # Draw nodes
        draw.ellipse([start_x - node_width//2, start_y - node_height//2, 
                     start_x + node_width//2, start_y + node_height//2], 
                     fill=self.colors['start_end'], outline=self.colors['edge'], width=2)
        draw.text((start_x, start_y), "Start", fill=self.colors['text'], font=font, anchor='mm')
        
        draw.rectangle([process_x - node_width//2, process_y - node_height//2,
                       process_x + node_width//2, process_y + node_height//2],
                       fill=self.colors['node'], outline=self.colors['edge'], width=2)
        draw.text((process_x, process_y), "Process", fill=self.colors['text'], font=font, anchor='mm')
        
        draw.ellipse([end_x - node_width//2, end_y - node_height//2,
                     end_x + node_width//2, end_y + node_height//2],
                     fill=self.colors['start_end'], outline=self.colors['edge'], width=2)
        draw.text((end_x, end_y), "End", fill=self.colors['text'], font=font, anchor='mm')
        
        # Draw edges
        draw.line([(start_x, start_y + node_height//2), (process_x, process_y - node_height//2)], 
                 fill=self.colors['edge'], width=2)
        draw.line([(process_x, process_y + node_height//2), (end_x, end_y - node_height//2)], 
                 fill=self.colors['edge'], width=2)
    
    def _create_text_png(self, mermaid_code: str, class_name: str, method_name: str, filepath: str) -> str:
        """Create a text-based PNG as fallback."""
        img = Image.new('RGB', (1200, 800), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
            title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
        except:
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()
        
        # Title
        title = f"{class_name}.{method_name}()"
        draw.text((600, 30), title, fill='black', font=title_font, anchor='mm')
        
        # Mermaid code as text
        lines = self._break_text(mermaid_code, 60)
        y_pos = 80
        for line in lines:
            draw.text((50, y_pos), line, fill='black', font=font)
            y_pos += 20
        
        img.save(filepath)
        return filepath
    
    def _break_text(self, text: str, max_length: int) -> List[str]:
        """Break text into lines of maximum length."""
        lines = []
        for line in text.split('\n'):
            while len(line) > max_length:
                lines.append(line[:max_length])
                line = line[max_length:]
            if line:
                lines.append(line)
        return lines