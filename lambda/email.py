"""
Email module for sending PDF reports via AWS SES.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import boto3
from botocore.exceptions import ClientError


class EmailSender:
    """Handles email sending via AWS SES."""
    
    def __init__(self, region: str = "us-east-1"):
        self.ses_client = boto3.client('ses', region_name=region)
        self.region = region
    
    def send_pdf_email(self, 
                      to_email: str,
                      pdf_file_path: str,
                      subject: Optional[str] = None,
                      body: Optional[str] = None,
                      from_email: Optional[str] = None) -> Dict[str, Any]:
        """
        Send PDF report via email using AWS SES.
        
        Args:
            to_email: Recipient email address
            pdf_file_path: Path to PDF file
            subject: Email subject (will generate if not provided)
            body: Email body (will generate if not provided)
            from_email: Sender email (must be verified in SES)
            
        Returns:
            Dict with email sending result
        """
        try:
            # Use default from email if not provided
            if not from_email:
                from_email = os.environ.get('SES_FROM_EMAIL', 'noreply@yourdomain.com')
            
            # Generate subject if not provided
            if not subject:
                timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
                subject = f"Data Processing Report - {timestamp}"
            
            # Generate body if not provided
            if not body:
                body = self._generate_email_body()
            
            # Read PDF file
            with open(pdf_file_path, 'rb') as f:
                pdf_content = f.read()
            
            # Prepare email
            email_result = self._send_email_with_attachment(
                from_email=from_email,
                to_email=to_email,
                subject=subject,
                body=body,
                attachment_name=os.path.basename(pdf_file_path),
                attachment_content=pdf_content
            )
            
            return {
                'status': 'success',
                'message_id': email_result.get('MessageId'),
                'to_email': to_email,
                'from_email': from_email,
                'subject': subject,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except FileNotFoundError:
            return {
                'status': 'error',
                'error': f'PDF file not found: {pdf_file_path}',
                'timestamp': datetime.utcnow().isoformat()
            }
        except ClientError as e:
            return {
                'status': 'error',
                'error': str(e),
                'error_code': e.response['Error']['Code'],
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _send_email_with_attachment(self, 
                                   from_email: str,
                                   to_email: str,
                                   subject: str,
                                   body: str,
                                   attachment_name: str,
                                   attachment_content: bytes) -> Dict[str, Any]:
        """Send email with PDF attachment using SES."""
        
        # Create MIME message
        import email
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.application import MIMEApplication
        
        # Create message container
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        
        # Add body
        msg.attach(MIMEText(body, 'plain'))
        
        # Add PDF attachment
        pdf_attachment = MIMEApplication(attachment_content, _subtype='pdf')
        pdf_attachment.add_header('Content-Disposition', 'attachment', filename=attachment_name)
        msg.attach(pdf_attachment)
        
        # Send email via SES
        response = self.ses_client.send_raw_email(
            Source=from_email,
            Destinations=[to_email],
            RawMessage={'Data': msg.as_string()}
        )
        
        return response
    
    def _generate_email_body(self) -> str:
        """Generate default email body."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        body = f"""
Hello,

Your assessment has been generated and is attached to this email.

Best regards,
Data Processing System
        """.strip()
        
        return body
