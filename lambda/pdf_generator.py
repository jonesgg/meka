"""
PDF generation module for creating simple reports from processed data.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional


def generate_simple_content(data: Dict[str, Any]) -> str:
    """Generate simple PDF content with test pdf and list of items."""
    content = []
    
    # Header
    content.append("test pdf")
    content.append("")
    
    # List of items from the data
    content.append("Items:")
    content.append("-" * 20)
    
    # Extract items from original data
    if 'original_data' in data:
        for key, value in data['original_data'].items():
            content.append(f"• {key}: {value}")
    else:
        # If no original_data, use the data directly
        for key, value in data.items():
            content.append(f"• {key}: {value}")
    
    content.append("")
    content.append(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    return "\n".join(content)


def generate_pdf_report(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a simple PDF report from processed data.
    
    Args:
        data: Data to include in PDF
        
    Returns:
        Dict with PDF file information and status
    """
    try:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"data_report_{timestamp}.pdf"
        
        # Generate simple PDF content
        pdf_content = generate_simple_content(data)
        
        # Create a simple text file as placeholder for PDF
        temp_file_path = f"/tmp/{filename}"
        
        with open(temp_file_path, 'w', encoding='utf-8') as f:
            f.write(pdf_content)
        
        result = {
            'filename': filename,
            'file_path': temp_file_path,
            'file_size': len(pdf_content),
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return result
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        } 