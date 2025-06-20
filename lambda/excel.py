"""
Excel integration module for uploading Python dict to Excel via API.
"""

import json
import requests
from datetime import datetime
from typing import Dict, Any


def upload_dict_to_excel(data: Dict[str, Any], api_url: str, api_key: str = None) -> Dict[str, Any]:
    """
    Upload a Python dictionary to Excel via API.
    
    Args:
        data: Python dictionary to upload
        api_url: API endpoint URL for Excel upload
        api_key: Optional API key for authentication
        
    Returns:
        Dict with upload result
    """
    try:
        # Prepare headers
        headers = {
            'Content-Type': 'application/json'
        }
        
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        # Prepare payload
        payload = {
            'data': data,
            'timestamp': datetime.utcnow().isoformat(),
            'format': 'excel'
        }
        
        # Make API request
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return {
                'status': 'success',
                'api_url': api_url,
                'response': response.json(),
                'timestamp': datetime.utcnow().isoformat()
            }
        else:
            return {
                'status': 'error',
                'api_url': api_url,
                'status_code': response.status_code,
                'error': response.text,
                'timestamp': datetime.utcnow().isoformat()
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'api_url': api_url,
            'error': f'Request failed: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            'status': 'error',
            'api_url': api_url,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }


def write_data_to_excel(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to write data to Excel via API.
    
    Args:
        data: Data to write to Excel
        
    Returns:
        Dict with operation result
    """
    # You can configure the API URL and key via environment variables
    api_url = "https://your-excel-api-endpoint.com/upload"
    api_key = None  # Set your API key here if needed
    
    return upload_dict_to_excel(data, api_url, api_key) 