"""
Screenshot Reader Tool for the Personal AI Agent System.

This module provides functionality to extract and analyze text and UI elements
from screenshots using OCR and computer vision techniques.
"""

import os
import json
import time
import random
import base64
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger("screenshot_reader")

def run(
    image_path: str,
    extract_text: bool = True,
    extract_ui_elements: bool = False,
    detect_tables: bool = False,
    detect_charts: bool = False,
    language: str = "en",
    output_format: str = "text",
    store_memory: bool = False,
    memory_manager = None,
    memory_tags: List[str] = ["screenshot", "ocr", "vision"],
    memory_scope: str = "agent"
) -> Dict[str, Any]:
    """
    Extract and analyze content from screenshots.
    
    Args:
        image_path: Path to the screenshot image file
        extract_text: Whether to extract text using OCR
        extract_ui_elements: Whether to detect UI elements (buttons, forms, etc.)
        detect_tables: Whether to detect and extract tables
        detect_charts: Whether to detect and analyze charts/graphs
        language: Language code for OCR (e.g., 'en', 'fr', 'de', 'es', 'zh')
        output_format: Format for extracted content (text, json, markdown, html)
        store_memory: Whether to store the extracted content in memory
        memory_manager: Memory manager instance for storing results
        memory_tags: Tags to apply to the memory entry
        memory_scope: Scope for the memory entry (agent or global)
        
    Returns:
        Dictionary containing the extracted content and analysis results
    """
    logger.info(f"Analyzing screenshot: {image_path}")
    
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Screenshot file not found: {image_path}")
            
        # Validate inputs
        if output_format not in ["text", "json", "markdown", "html"]:
            raise ValueError(f"Invalid output format: {output_format}. Supported formats: text, json, markdown, html")
        
        # In a real implementation, this would use OCR and computer vision models
        # For now, we'll simulate the screenshot analysis
        
        # Get image metadata
        image_metadata = _get_image_metadata(image_path)
        
        # Initialize results
        results = {}
        
        # Simulate text extraction if requested
        if extract_text:
            results["text"] = _simulate_text_extraction(image_path, language)
        
        # Simulate UI element detection if requested
        if extract_ui_elements:
            results["ui_elements"] = _simulate_ui_element_detection(image_path)
        
        # Simulate table detection if requested
        if detect_tables:
            results["tables"] = _simulate_table_detection(image_path)
        
        # Simulate chart detection if requested
        if detect_charts:
            results["charts"] = _simulate_chart_detection(image_path)
        
        # Format the output
        formatted_output = _format_output(results, output_format)
        
        # Store in memory if requested
        if store_memory and memory_manager:
            try:
                # Create a memory entry with the extracted content
                memory_entry = {
                    "type": "screenshot_analysis",
                    "image_path": image_path,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add text content if available
                if "text" in results and results["text"]["content"]:
                    memory_entry["text_content"] = results["text"]["content"]
                
                # Add detected UI elements if available
                if "ui_elements" in results and results["ui_elements"]["elements"]:
                    memory_entry["ui_elements"] = [
                        {"type": elem["type"], "text": elem.get("text", "")}
                        for elem in results["ui_elements"]["elements"]
                    ]
                
                memory_manager.add_memory(
                    content=json.dumps(memory_entry),
                    scope=memory_scope,
                    tags=memory_tags + ["screenshot_analysis"]
                )
                
                logger.info(f"Stored screenshot analysis in memory with tags: {memory_tags}")
            except Exception as e:
                logger.error(f"Failed to store screenshot analysis in memory: {str(e)}")
        
        return {
            "success": True,
            "image_path": image_path,
            "metadata": image_metadata,
            "results": results,
            "formatted_output": formatted_output
        }
    except Exception as e:
        error_msg = f"Error analyzing screenshot: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "image_path": image_path
        }

def _get_image_metadata(image_path: str) -> Dict[str, Any]:
    """
    Extract metadata from an image file.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary with image metadata
    """
    # In a real implementation, this would use libraries like PIL or exifread
    # For now, we'll extract basic file information
    
    file_stats = os.stat(image_path)
    file_name = os.path.basename(image_path)
    file_ext = os.path.splitext(file_name)[1].lower()
    
    # Map common extensions to formats
    format_map = {
        ".jpg": "JPEG",
        ".jpeg": "JPEG",
        ".png": "PNG",
        ".gif": "GIF",
        ".bmp": "BMP",
        ".webp": "WebP",
        ".tiff": "TIFF",
        ".tif": "TIFF"
    }
    
    image_format = format_map.get(file_ext, "Unknown")
    
    return {
        "file_name": file_name,
        "file_path": image_path,
        "file_size": file_stats.st_size,
        "format": image_format,
        "last_modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
    }

def _simulate_text_extraction(image_path: str, language: str) -> Dict[str, Any]:
    """
    Simulate text extraction from a screenshot using OCR.
    
    Args:
        image_path: Path to the screenshot image
        language: Language code for OCR
        
    Returns:
        Dictionary with simulated OCR results
    """
    # Generate a deterministic but seemingly random seed based on the image path
    seed = sum(ord(c) for c in image_path)
    random.seed(seed)
    
    # Determine the type of screenshot based on the file name
    file_name = os.path.basename(image_path).lower()
    
    # Predefined text content for different types of screenshots
    if "website" in file_name or "web" in file_name:
        text_content = _generate_website_text()
    elif "code" in file_name or "programming" in file_name:
        text_content = _generate_code_text()
    elif "document" in file_name or "doc" in file_name or "pdf" in file_name:
        text_content = _generate_document_text()
    elif "form" in file_name:
        text_content = _generate_form_text()
    elif "error" in file_name:
        text_content = _generate_error_text()
    elif "dashboard" in file_name or "chart" in file_name or "graph" in file_name:
        text_content = _generate_dashboard_text()
    elif "social" in file_name or "tweet" in file_name or "post" in file_name:
        text_content = _generate_social_media_text()
    elif "email" in file_name or "mail" in file_name:
        text_content = _generate_email_text()
    else:
        # Generic text for other types of screenshots
        text_content = _generate_generic_text()
    
    # Simulate OCR confidence
    confidence = random.uniform(0.85, 0.98)
    
    # Simulate text blocks with positions
    text_blocks = []
    lines = text_content.split("\n")
    y_position = 0.1
    
    for line in lines:
        if line.strip():
            text_blocks.append({
                "text": line,
                "confidence": round(confidence * random.uniform(0.95, 1.05), 2),
                "bounding_box": {
                    "x": round(random.uniform(0.1, 0.2), 2),
                    "y": round(y_position, 2),
                    "width": round(random.uniform(0.6, 0.8), 2),
                    "height": round(random.uniform(0.03, 0.05), 2)
                }
            })
            y_position += random.uniform(0.06, 0.08)
    
    return {
        "content": text_content,
        "language": language,
        "confidence": round(confidence, 2),
        "text_blocks": text_blocks,
        "word_count": len(text_content.split())
    }

def _simulate_ui_element_detection(image_path: str) -> Dict[str, Any]:
    """
    Simulate UI element detection in a screenshot.
    
    Args:
        image_path: Path to the screenshot image
        
    Returns:
        Dictionary with simulated UI element detection results
    """
    # Generate a deterministic but seemingly random seed based on the image path
    seed = sum(ord(c) for c in image_path)
    random.seed(seed)
    
    # Determine the type of screenshot based on the file name
    file_name = os.path.basename(image_path).lower()
    
    # Initialize UI elements
    ui_elements = []
    
    # Generate different UI elements based on the type of screenshot
    if "website" in file_name or "web" in file_name:
        # Website UI elements
        ui_elements.extend(_generate_website_ui_elements())
    elif "form" in file_name:
        # Form UI elements
        ui_elements.extend(_generate_form_ui_elements())
    elif "dashboard" in file_name or "app" in file_name:
        # Dashboard/app UI elements
        ui_elements.extend(_generate_dashboard_ui_elements())
    elif "mobile" in file_name:
        # Mobile app UI elements
        ui_elements.extend(_generate_mobile_ui_elements())
    else:
        # Generic UI elements
        ui_elements.extend(_generate_generic_ui_elements())
    
    return {
        "elements": ui_elements,
        "count": len(ui_elements)
    }

def _simulate_table_detection(image_path: str) -> Dict[str, Any]:
    """
    Simulate table detection and extraction in a screenshot.
    
    Args:
        image_path: Path to the screenshot image
        
    Returns:
        Dictionary with simulated table detection results
    """
    # Generate a deterministic but seemingly random seed based on the image path
    seed = sum(ord(c) for c in image_path)
    random.seed(seed)
    
    # Determine the type of screenshot based on the file name
    file_name = os.path.basename(image_path).lower()
    
    # Determine if the screenshot likely contains tables
    has_tables = (
        "table" in file_name or
        "spreadsheet" in file_name or
        "excel" in file_name or
        "data" in file_name or
        "report" in file_name or
        random.random() < 0.3  # 30% chance for other screenshots
    )
    
    if not has_tables:
        return {
            "tables": [],
            "count": 0
        }
    
    # Generate simulated tables
    tables = []
    num_tables = random.randint(1, 2)
    
    for i in range(num_tables):
        # Generate table dimensions
        rows = random.randint(3, 8)
        cols = random.randint(2, 5)
        
        # Generate table data
        table_data = []
        
        # Generate header row
        header_row = []
        for j in range(cols):
            header_row.append(f"Column {j+1}")
        table_data.append(header_row)
        
        # Generate data rows
        for r in range(rows - 1):
            row_data = []
            for c in range(cols):
                if c == 0:
                    row_data.append(f"Row {r+1}")
                else:
                    # Generate different types of data
                    data_type = random.choice(["text", "number", "date", "percentage"])
                    if data_type == "text":
                        row_data.append(f"Item {r+1}-{c}")
                    elif data_type == "number":
                        row_data.append(str(random.randint(10, 1000)))
                    elif data_type == "date":
                        month = random.randint(1, 12)
                        day = random.randint(1, 28)
                        year = random.randint(2020, 2023)
                        row_data.append(f"{month}/{day}/{year}")
                    else:  # percentage
                        row_data.append(f"{random.randint(1, 100)}%")
            table_data.append(row_data)
        
        # Generate table position
        table_position = {
            "x": round(random.uniform(0.1, 0.3), 2),
            "y": round(random.uniform(0.2, 0.5), 2),
            "width": round(random.uniform(0.4, 0.8), 2),
            "height": round(random.uniform(0.2, 0.4), 2)
        }
        
        tables.append({
            "id": f"table_{i+1}",
            "rows": rows,
            "columns": cols,
            "data": table_data,
            "position": table_position,
            "confidence": round(random.uniform(0.8, 0.95), 2)
        })
    
    return {
        "tables": tables,
        "count": len(tables)
    }

def _simulate_chart_detection(image_path: str) -> Dict[str, Any]:
    """
    Simulate chart/graph detection and analysis in a screenshot.
    
    Args:
        image_path: Path to the screenshot image
        
    Returns:
        Dictionary with simulated chart detection results
    """
    # Generate a deterministic but seemingly random seed based on the image path
    seed = sum(ord(c) for c in image_path)
    random.seed(seed)
    
    # Determine the type of screenshot based on the file name
    file_name = os.path.basename(image_path).lower()
    
    # Determine if the screenshot likely contains charts
    has_charts = (
        "chart" in file_name or
        "graph" in file_name or
        "plot" in file_name or
        "dashboard" in file_name or
        "analytics" in file_name or
        "report" in file_name or
        random.random() < 0.2  # 20% chance for other screenshots
    )
    
    if not has_charts:
        return {
            "charts": [],
            "count": 0
        }
    
    # Generate simulated charts
    charts = []
    num_charts = random.randint(1, 2)
    
    for i in range(num_charts):
        # Generate chart type
        chart_types = ["bar", "line", "pie", "scatter", "area"]
        chart_type = random.choice(chart_types)
        
        # Generate chart title
        chart_titles = [
            "Sales Performance", "Revenue Growth", "User Engagement",
            "Market Share", "Quarterly Results", "Monthly Trends",
            "Customer Satisfaction", "Product Comparison"
        ]
        chart_title = random.choice(chart_titles)
        
        # Generate chart data
        chart_data = {}
        
        if chart_type in ["bar", "line", "area"]:
            # Generate x-axis labels
            if random.random() < 0.5:
                # Time-based labels
                x_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
            else:
                # Category-based labels
                x_labels = ["Product A", "Product B", "Product C", "Product D", "Product E"]
            
            # Generate y-axis data
            series = []
            num_series = random.randint(1, 3)
            
            for s in range(num_series):
                series_data = []
                for _ in range(len(x_labels)):
                    series_data.append(random.randint(10, 100))
                
                series.append({
                    "name": f"Series {s+1}",
                    "data": series_data
                })
            
            chart_data = {
                "x_axis": {
                    "title": "Time Period" if "Jan" in x_labels else "Category",
                    "labels": x_labels
                },
                "y_axis": {
                    "title": "Value",
                    "min": 0,
                    "max": 100
                },
                "series": series
            }
        
        elif chart_type == "pie":
            # Generate pie chart data
            labels = ["Segment A", "Segment B", "Segment C", "Segment D", "Segment E"]
            values = []
            
            remaining = 100
            for i in range(len(labels) - 1):
                value = random.randint(5, min(remaining - 5, 40))
                values.append(value)
                remaining -= value
            
            values.append(remaining)  # Last segment gets the remainder
            
            chart_data = {
                "labels": labels,
                "values": values
            }
        
        elif chart_type == "scatter":
            # Generate scatter plot data
            points = []
            for _ in range(random.randint(10, 20)):
                points.append({
                    "x": random.uniform(0, 100),
                    "y": random.uniform(0, 100)
                })
            
            chart_data = {
                "x_axis": {
                    "title": "X Value",
                    "min": 0,
                    "max": 100
                },
                "y_axis": {
                    "title": "Y Value",
                    "min": 0,
                    "max": 100
                },
                "points": points
            }
        
        # Generate chart position
        chart_position = {
            "x": round(random.uniform(0.1, 0.3), 2),
            "y": round(random.uniform(0.2, 0.5), 2),
            "width": round(random.uniform(0.4, 0.7), 2),
            "height": round(random.uniform(0.3, 0.5), 2)
        }
        
        charts.append({
            "id": f"chart_{i+1}",
            "type": chart_type,
            "title": chart_title,
            "data": chart_data,
            "position": chart_position,
            "confidence": round(random.uniform(0.75, 0.95), 2)
        })
    
    return {
        "charts": charts,
        "count": len(charts)
    }

def _format_output(results: Dict[str, Any], output_format: str) -> Any:
    """
    Format the screenshot analysis results in the specified format.
    
    Args:
        results: Analysis results
        output_format: Output format (text, json, markdown, html)
        
    Returns:
        Formatted output
    """
    if output_format == "json":
        # Return the results as is (already in JSON-compatible format)
        return results
    
    elif output_format == "text":
        # Format as plain text
        output = []
        
        # Add extracted text
        if "text" in results:
            output.append("=== EXTRACTED TEXT ===")
            output.append(results["text"]["content"])
            output.append("")
        
        # Add UI elements
        if "ui_elements" in results and results["ui_elements"]["elements"]:
            output.append("=== DETECTED UI ELEMENTS ===")
            for elem in results["ui_elements"]["elements"]:
                elem_text = elem.get("text", "")
                output.append(f"- {elem['type']}" + (f": {elem_text}" if elem_text else ""))
            output.append("")
        
        # Add tables
        if "tables" in results and results["tables"]["tables"]:
            output.append("=== DETECTED TABLES ===")
            for i, table in enumerate(results["tables"]["tables"]):
                output.append(f"Table {i+1} ({table['rows']}x{table['columns']}):")
                
                # Format table data as text
                for row in table["data"]:
                    output.append("  " + " | ".join(row))
                
                output.append("")
        
        # Add charts
        if "charts" in results and results["charts"]["charts"]:
            output.append("=== DETECTED CHARTS ===")
            for i, chart in enumerate(results["charts"]["charts"]):
                output.append(f"Chart {i+1}: {chart['title']} ({chart['type']} chart)")
                output.append("")
        
        return "\n".join(output)
    
    elif output_format == "markdown":
        # Format as markdown
        output = []
        
        # Add extracted text
        if "text" in results:
            output.append("## Extracted Text")
            output.append("```")
            output.append(results["text"]["content"])
            output.append("```")
            output.append("")
        
        # Add UI elements
        if "ui_elements" in results and results["ui_elements"]["elements"]:
            output.append("## Detected UI Elements")
            for elem in results["ui_elements"]["elements"]:
                elem_text = elem.get("text", "")
                output.append(f"- **{elem['type']}**" + (f": {elem_text}" if elem_text else ""))
            output.append("")
        
        # Add tables
        if "tables" in results and results["tables"]["tables"]:
            output.append("## Detected Tables")
            for i, table in enumerate(results["tables"]["tables"]):
                output.append(f"### Table {i+1}")
                
                # Format table data as markdown table
                for j, row in enumerate(table["data"]):
                    output.append("| " + " | ".join(row) + " |")
                    
                    # Add separator after header row
                    if j == 0:
                        output.append("| " + " | ".join(["---"] * len(row)) + " |")
                
                output.append("")
        
        # Add charts
        if "charts" in results and results["charts"]["charts"]:
            output.append("## Detected Charts")
            for i, chart in enumerate(results["charts"]["charts"]):
                output.append(f"### Chart {i+1}: {chart['title']}")
                output.append(f"**Type**: {chart['type']} chart")
                output.append("")
        
        return "\n".join(output)
    
    elif output_format == "html":
        # Format as HTML
        output = ["<html><body>"]
        
        # Add extracted text
        if "text" in results:
            output.append("<h2>Extracted Text</h2>")
            output.append("<pre>")
            output.append(results["text"]["content"])
            output.append("</pre>")
        
        # Add UI elements
        if "ui_elements" in results and results["ui_elements"]["elements"]:
            output.append("<h2>Detected UI Elements</h2>")
            output.append("<ul>")
            for elem in results["ui_elements"]["elements"]:
                elem_text = elem.get("text", "")
                output.append(f"<li><strong>{elem['type']}</strong>" + (f": {elem_text}" if elem_text else "") + "</li>")
            output.append("</ul>")
        
        # Add tables
        if "tables" in results and results["tables"]["tables"]:
            output.append("<h2>Detected Tables</h2>")
            for i, table in enumerate(results["tables"]["tables"]):
                output.append(f"<h3>Table {i+1}</h3>")
                
                # Format table data as HTML table
                output.append("<table border='1'>")
                for j, row in enumerate(table["data"]):
                    output.append("<tr>")
                    
                    # Use th for header row, td for data rows
                    cell_tag = "th" if j == 0 else "td"
                    
                    for cell in row:
                        output.append(f"<{cell_tag}>{cell}</{cell_tag}>")
                    
                    output.append("</tr>")
                
                output.append("</table>")
        
        # Add charts
        if "charts" in results and results["charts"]["charts"]:
            output.append("<h2>Detected Charts</h2>")
            for i, chart in enumerate(results["charts"]["charts"]):
                output.append(f"<h3>Chart {i+1}: {chart['title']}</h3>")
                output.append(f"<p><strong>Type</strong>: {chart['type']} chart</p>")
        
        output.append("</body></html>")
        return "\n".join(output)
    
    else:
        # Default to text format
        return _format_output(results, "text")

def _generate_website_text() -> str:
    """
    Generate simulated text content for a website screenshot.
    
    Returns:
        Simulated website text
    """
    return """Home   Products   Services   About   Contact

Welcome to Our Website

Discover innovative solutions for your business needs. Our products and services are designed to help you achieve your goals and streamline your operations.

Featured Products
- Product A: Advanced analytics platform
- Product B: Cloud-based collaboration tools
- Product C: Enterprise security solutions

Latest News
- Company announces new partnership with industry leader
- Upcoming webinar: Digital transformation strategies
- Product update: New features released for Product B

Contact Us
Email: info@example.com
Phone: (555) 123-4567
Address: 123 Main Street, Anytown, USA"""

def _generate_code_text() -> str:
    """
    Generate simulated text content for a code screenshot.
    
    Returns:
        Simulated code text
    """
    return """def process_data(data, options=None):
    \"\"\"
    Process the input data according to specified options.
    
    Args:
        data: Input data to process
        options: Processing options (default: None)
        
    Returns:
        Processed data
    \"\"\"
    if options is None:
        options = {'normalize': True, 'filter_outliers': False}
    
    result = []
    
    # Normalize data if requested
    if options.get('normalize', False):
        data = normalize(data)
    
    # Filter outliers if requested
    if options.get('filter_outliers', False):
        data = remove_outliers(data)
    
    # Process each data point
    for item in data:
        processed_item = transform(item)
        result.append(processed_item)
    
    return result"""

def _generate_document_text() -> str:
    """
    Generate simulated text content for a document screenshot.
    
    Returns:
        Simulated document text
    """
    return """Quarterly Business Report
Q2 2023

Executive Summary

The second quarter of 2023 showed strong performance across all business units, with revenue exceeding projections by 12%. Key highlights include:

- Total revenue: $24.5M (↑15% YoY)
- Operating margin: 28% (↑3% from Q1)
- New customer acquisition: 1,250 (↑8% from Q1)
- Customer retention rate: 94%

Market Analysis

The overall market showed positive growth trends, with our company outperforming the industry average by approximately 5 percentage points. Competitor activity remained consistent with Q1, with no significant new product launches or pricing changes.

Financial Performance

Revenue by business unit:
- Software Solutions: $12.8M (↑18% YoY)
- Professional Services: $7.2M (↑12% YoY)
- Managed Services: $4.5M (↑10% YoY)"""

def _generate_form_text() -> str:
    """
    Generate simulated text content for a form screenshot.
    
    Returns:
        Simulated form text
    """
    return """Registration Form

Personal Information
First Name: 
Last Name: 
Email Address: 
Phone Number: 

Account Details
Username: 
Password: 
Confirm Password: 

Address
Street Address: 
City: 
State/Province: 
ZIP/Postal Code: 
Country: 

Preferences
[ ] Subscribe to newsletter
[ ] Receive product updates
[ ] Allow marketing communications

[ Cancel ]   [ Submit ]"""

def _generate_error_text() -> str:
    """
    Generate simulated text content for an error message screenshot.
    
    Returns:
        Simulated error text
    """
    return """Error

The application encountered an unexpected error.

Error Code: E-1234
Message: Unable to connect to the database server.

Possible causes:
- Network connectivity issues
- Database server is offline
- Incorrect database credentials

Please try again later or contact support if the problem persists.

[ Retry ]   [ Cancel ]   [ Contact Support ]"""

def _generate_dashboard_text() -> str:
    """
    Generate simulated text content for a dashboard screenshot.
    
    Returns:
        Simulated dashboard text
    """
    return """Performance Dashboard - July 2023

Key Metrics
Revenue: $1.25M
Expenses: $820K
Profit: $430K
Conversion Rate: 3.8%
Customer Satisfaction: 92%

Top Products
1. Product X - $320K
2. Product Y - $280K
3. Product Z - $210K
4. Product W - $180K

Regional Performance
- North America: $580K (↑12%)
- Europe: $420K (↑8%)
- Asia Pacific: $150K (↑15%)
- Other: $100K (↑5%)

Recent Activity
- 24 new orders in the last hour
- 3 support tickets pending
- 5 inventory items below threshold"""

def _generate_social_media_text() -> str:
    """
    Generate simulated text content for a social media screenshot.
    
    Returns:
        Simulated social media text
    """
    return """Jane Smith @janesmith · 2h
Just announced our new product launch! After months of hard work, we're excited to share this with our community. #ProductLaunch #Innovation

❤ 245   🔄 78   💬 32

John Doe @johndoe · 1h
Replying to @janesmith
Congratulations! Looking forward to trying it out. When will it be available in Europe?

❤ 12   🔄 2   💬 1

Jane Smith @janesmith · 45m
Replying to @johndoe
Thanks John! European launch is scheduled for next week. We'll send you a DM with more details.

❤ 8   🔄 1   💬 0"""

def _generate_email_text() -> str:
    """
    Generate simulated text content for an email screenshot.
    
    Returns:
        Simulated email text
    """
    return """From: john.smith@example.com
To: jane.doe@example.com
Subject: Project Update - Q3 Planning
Date: July 15, 2023 10:30 AM

Hi Jane,

I hope this email finds you well. I wanted to provide an update on the Q3 planning process.

We've completed the initial draft of the project roadmap and resource allocation. Key points:

1. Development phase scheduled to begin August 1
2. Testing phase planned for September 10-20
3. Launch target remains October 1

Could we schedule a meeting next week to review the details? I'm available Monday or Wednesday afternoon.

Please let me know if you have any questions or concerns.

Best regards,
John Smith
Project Manager
Example Company

This email and any files transmitted with it are confidential and intended solely for the use of the individual or entity to whom they are addressed."""

def _generate_generic_text() -> str:
    """
    Generate simulated generic text content for a screenshot.
    
    Returns:
        Simulated generic text
    """
    return """Main Title

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.

Section 1
- Item one with some details
- Item two with additional information
- Item three with important notes

Section 2
This section contains supplementary information that provides context for the main content. Please review carefully before proceeding.

Final Notes
For additional information, please contact support@example.com or visit our website at www.example.com.

[ Button 1 ]   [ Button 2 ]"""

def _generate_website_ui_elements() -> List[Dict[str, Any]]:
    """
    Generate simulated UI elements for a website screenshot.
    
    Returns:
        List of simulated UI elements
    """
    elements = [
        {
            "type": "navigation_menu",
            "text": "Home Products Services About Contact",
            "bounding_box": {
                "x": 0.05,
                "y": 0.05,
                "width": 0.9,
                "height": 0.05
            },
            "confidence": 0.95
        },
        {
            "type": "heading",
            "text": "Welcome to Our Website",
            "bounding_box": {
                "x": 0.1,
                "y": 0.15,
                "width": 0.8,
                "height": 0.08
            },
            "confidence": 0.98
        },
        {
            "type": "paragraph",
            "text": "Discover innovative solutions for your business needs...",
            "bounding_box": {
                "x": 0.1,
                "y": 0.25,
                "width": 0.8,
                "height": 0.1
            },
            "confidence": 0.92
        },
        {
            "type": "button",
            "text": "Learn More",
            "bounding_box": {
                "x": 0.4,
                "y": 0.4,
                "width": 0.2,
                "height": 0.06
            },
            "confidence": 0.96
        },
        {
            "type": "image",
            "text": "",
            "bounding_box": {
                "x": 0.6,
                "y": 0.2,
                "width": 0.3,
                "height": 0.25
            },
            "confidence": 0.9
        },
        {
            "type": "list",
            "text": "Featured Products",
            "bounding_box": {
                "x": 0.1,
                "y": 0.5,
                "width": 0.4,
                "height": 0.2
            },
            "confidence": 0.93
        },
        {
            "type": "footer",
            "text": "Contact Us Email: info@example.com Phone: (555) 123-4567",
            "bounding_box": {
                "x": 0.05,
                "y": 0.85,
                "width": 0.9,
                "height": 0.1
            },
            "confidence": 0.91
        }
    ]
    
    return elements

def _generate_form_ui_elements() -> List[Dict[str, Any]]:
    """
    Generate simulated UI elements for a form screenshot.
    
    Returns:
        List of simulated UI elements
    """
    elements = [
        {
            "type": "heading",
            "text": "Registration Form",
            "bounding_box": {
                "x": 0.1,
                "y": 0.05,
                "width": 0.8,
                "height": 0.08
            },
            "confidence": 0.98
        },
        {
            "type": "text_field",
            "text": "First Name:",
            "bounding_box": {
                "x": 0.1,
                "y": 0.18,
                "width": 0.8,
                "height": 0.06
            },
            "confidence": 0.96
        },
        {
            "type": "text_field",
            "text": "Last Name:",
            "bounding_box": {
                "x": 0.1,
                "y": 0.26,
                "width": 0.8,
                "height": 0.06
            },
            "confidence": 0.96
        },
        {
            "type": "text_field",
            "text": "Email Address:",
            "bounding_box": {
                "x": 0.1,
                "y": 0.34,
                "width": 0.8,
                "height": 0.06
            },
            "confidence": 0.95
        },
        {
            "type": "text_field",
            "text": "Phone Number:",
            "bounding_box": {
                "x": 0.1,
                "y": 0.42,
                "width": 0.8,
                "height": 0.06
            },
            "confidence": 0.95
        },
        {
            "type": "password_field",
            "text": "Password:",
            "bounding_box": {
                "x": 0.1,
                "y": 0.5,
                "width": 0.8,
                "height": 0.06
            },
            "confidence": 0.94
        },
        {
            "type": "password_field",
            "text": "Confirm Password:",
            "bounding_box": {
                "x": 0.1,
                "y": 0.58,
                "width": 0.8,
                "height": 0.06
            },
            "confidence": 0.94
        },
        {
            "type": "checkbox",
            "text": "Subscribe to newsletter",
            "bounding_box": {
                "x": 0.1,
                "y": 0.66,
                "width": 0.8,
                "height": 0.04
            },
            "confidence": 0.92
        },
        {
            "type": "checkbox",
            "text": "Receive product updates",
            "bounding_box": {
                "x": 0.1,
                "y": 0.72,
                "width": 0.8,
                "height": 0.04
            },
            "confidence": 0.92
        },
        {
            "type": "button",
            "text": "Cancel",
            "bounding_box": {
                "x": 0.3,
                "y": 0.85,
                "width": 0.15,
                "height": 0.06
            },
            "confidence": 0.97
        },
        {
            "type": "button",
            "text": "Submit",
            "bounding_box": {
                "x": 0.55,
                "y": 0.85,
                "width": 0.15,
                "height": 0.06
            },
            "confidence": 0.97
        }
    ]
    
    return elements

def _generate_dashboard_ui_elements() -> List[Dict[str, Any]]:
    """
    Generate simulated UI elements for a dashboard screenshot.
    
    Returns:
        List of simulated UI elements
    """
    elements = [
        {
            "type": "heading",
            "text": "Performance Dashboard",
            "bounding_box": {
                "x": 0.1,
                "y": 0.05,
                "width": 0.8,
                "height": 0.08
            },
            "confidence": 0.98
        },
        {
            "type": "chart",
            "text": "Revenue Trends",
            "bounding_box": {
                "x": 0.1,
                "y": 0.15,
                "width": 0.4,
                "height": 0.3
            },
            "confidence": 0.95
        },
        {
            "type": "chart",
            "text": "Customer Satisfaction",
            "bounding_box": {
                "x": 0.55,
                "y": 0.15,
                "width": 0.35,
                "height": 0.3
            },
            "confidence": 0.94
        },
        {
            "type": "table",
            "text": "Top Products",
            "bounding_box": {
                "x": 0.1,
                "y": 0.5,
                "width": 0.4,
                "height": 0.25
            },
            "confidence": 0.93
        },
        {
            "type": "list",
            "text": "Recent Activity",
            "bounding_box": {
                "x": 0.55,
                "y": 0.5,
                "width": 0.35,
                "height": 0.25
            },
            "confidence": 0.92
        },
        {
            "type": "button",
            "text": "Export Data",
            "bounding_box": {
                "x": 0.7,
                "y": 0.85,
                "width": 0.2,
                "height": 0.06
            },
            "confidence": 0.96
        },
        {
            "type": "dropdown",
            "text": "Time Period: Last 30 Days",
            "bounding_box": {
                "x": 0.1,
                "y": 0.85,
                "width": 0.25,
                "height": 0.06
            },
            "confidence": 0.91
        }
    ]
    
    return elements

def _generate_mobile_ui_elements() -> List[Dict[str, Any]]:
    """
    Generate simulated UI elements for a mobile app screenshot.
    
    Returns:
        List of simulated UI elements
    """
    elements = [
        {
            "type": "status_bar",
            "text": "9:41 AM",
            "bounding_box": {
                "x": 0.0,
                "y": 0.0,
                "width": 1.0,
                "height": 0.05
            },
            "confidence": 0.97
        },
        {
            "type": "navigation_bar",
            "text": "Home",
            "bounding_box": {
                "x": 0.0,
                "y": 0.05,
                "width": 1.0,
                "height": 0.08
            },
            "confidence": 0.96
        },
        {
            "type": "card",
            "text": "Today's Summary",
            "bounding_box": {
                "x": 0.05,
                "y": 0.15,
                "width": 0.9,
                "height": 0.2
            },
            "confidence": 0.95
        },
        {
            "type": "list_item",
            "text": "Item 1",
            "bounding_box": {
                "x": 0.05,
                "y": 0.4,
                "width": 0.9,
                "height": 0.1
            },
            "confidence": 0.94
        },
        {
            "type": "list_item",
            "text": "Item 2",
            "bounding_box": {
                "x": 0.05,
                "y": 0.52,
                "width": 0.9,
                "height": 0.1
            },
            "confidence": 0.94
        },
        {
            "type": "list_item",
            "text": "Item 3",
            "bounding_box": {
                "x": 0.05,
                "y": 0.64,
                "width": 0.9,
                "height": 0.1
            },
            "confidence": 0.93
        },
        {
            "type": "fab_button",
            "text": "+",
            "bounding_box": {
                "x": 0.8,
                "y": 0.8,
                "width": 0.15,
                "height": 0.15
            },
            "confidence": 0.98
        },
        {
            "type": "tab_bar",
            "text": "Home Explore Profile Settings",
            "bounding_box": {
                "x": 0.0,
                "y": 0.92,
                "width": 1.0,
                "height": 0.08
            },
            "confidence": 0.95
        }
    ]
    
    return elements

def _generate_generic_ui_elements() -> List[Dict[str, Any]]:
    """
    Generate simulated generic UI elements for a screenshot.
    
    Returns:
        List of simulated UI elements
    """
    elements = [
        {
            "type": "heading",
            "text": "Main Title",
            "bounding_box": {
                "x": 0.1,
                "y": 0.1,
                "width": 0.8,
                "height": 0.08
            },
            "confidence": 0.97
        },
        {
            "type": "paragraph",
            "text": "Lorem ipsum dolor sit amet...",
            "bounding_box": {
                "x": 0.1,
                "y": 0.2,
                "width": 0.8,
                "height": 0.15
            },
            "confidence": 0.93
        },
        {
            "type": "list",
            "text": "Section 1",
            "bounding_box": {
                "x": 0.1,
                "y": 0.4,
                "width": 0.8,
                "height": 0.15
            },
            "confidence": 0.92
        },
        {
            "type": "paragraph",
            "text": "Section 2",
            "bounding_box": {
                "x": 0.1,
                "y": 0.6,
                "width": 0.8,
                "height": 0.1
            },
            "confidence": 0.91
        },
        {
            "type": "button",
            "text": "Button 1",
            "bounding_box": {
                "x": 0.3,
                "y": 0.8,
                "width": 0.15,
                "height": 0.06
            },
            "confidence": 0.95
        },
        {
            "type": "button",
            "text": "Button 2",
            "bounding_box": {
                "x": 0.55,
                "y": 0.8,
                "width": 0.15,
                "height": 0.06
            },
            "confidence": 0.95
        }
    ]
    
    return elements
