"""
Main Lambda function that orchestrates data processing, storage, and reporting.
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any
from jsonschema import ValidationError

# Import our custom modules
from validation import validate_assessment_data
from calculations import calculate_assessment_scores
from excel import write_data_to_excel
from dynamodb import store_data
from pdf_generator import generate_pdf_report
from email import send_pdf_email


def lambda_handler(event, context):
    """
    Main Lambda function handler that orchestrates the entire data processing pipeline.
    
    Flow:
    1. Parse and validate incoming data
    2. Perform calculations
    3. Write to Excel/CSV
    4. Store in DynamoDB
    5. Generate PDF report
    6. Send PDF via email
    """
    try:
        # Parse the request body
        if 'body' not in event:
            return create_response(400, {'error': 'Request body is required'})
        
        # Parse JSON body
        try:
            body = json.loads(event['body'])
        except json.JSONDecodeError:
            return create_response(400, {'error': 'Invalid JSON in request body'})
        
        # Validate required fields
        if not body:
            return create_response(400, {'error': 'Request body cannot be empty'})
        
        # Validate the assessment data
        try:
            validated_data = validate_assessment_data(body)
        except ValidationError as e:
            return create_response(400, {
                'error': 'Invalid assessment data',
                'details': str(e),
                'validation_path': ' -> '.join(str(p) for p in e.path) if e.path else None
            })
        
        # Generate a unique ID for the record
        record_id = str(uuid.uuid4())
        
        # Initialize results tracking
        results = {
            'record_id': record_id,
            'timestamp': datetime.utcnow().isoformat(),
            'steps': {}
        }
        
        # Step 1: Perform calculations on incoming data
        print(f"Processing data for record {record_id}")
        try:
            # This returns the complete enriched data with assessment_calculations
            enriched_data = calculate_assessment_scores(validated_data)
            results['steps']['calculations'] = {
                'status': 'success',
                'data': enriched_data
            }
            print("Calculations completed successfully")
        except Exception as e:
            results['steps']['calculations'] = {
                'status': 'error',
                'error': str(e)
            }
            print(f"Calculations failed: {str(e)}")
        
        # Step 2: Write data to Excel/CSV
        print("Writing data to Excel/CSV")
        try:
            excel_result = write_data_to_excel(
                data=enriched_data,
            )
            results['steps']['excel'] = excel_result
            print("Excel/CSV write completed")
        except Exception as e:
            results['steps']['excel'] = {
                'status': 'error',
                'error': str(e)
            }
            print(f"Excel/CSV write failed: {str(e)}")
        
        # Step 3: Store data in DynamoDB
        print("Storing data in DynamoDB")
        try:
            # Store the complete enriched data (includes original data + assessment_calculations)
            dynamodb_result = store_data(
                table_name=os.environ['DYNAMODB_TABLE'],
                data={
                    **enriched_data,  # This includes all original data + assessment_calculations
                    'id': record_id,
                    'created_at': results['timestamp']
                }
            )
            results['steps']['dynamodb'] = dynamodb_result
            print("DynamoDB storage completed")
        except Exception as e:
            results['steps']['dynamodb'] = {
                'status': 'error',
                'error': str(e)
            }
            print(f"DynamoDB storage failed: {str(e)}")
        
        # Step 4: Generate PDF report
        print("Generating PDF report")
        try:
            pdf_result = generate_pdf_report(
                data=enriched_data,
            )
            results['steps']['pdf_generation'] = pdf_result
            print("PDF generation completed")
        except Exception as e:
            results['steps']['pdf_generation'] = {
                'status': 'error',
                'error': str(e)
            }
            print(f"PDF generation failed: {str(e)}")
        
        # Step 5: Send PDF via email (if PDF was generated successfully)
        if (results['steps'].get('pdf_generation', {}).get('status') == 'success' and 
            'file_path' in results['steps']['pdf_generation']):
            
            print("Sending PDF via email")
            try:
                # Get recipient email from validated data
                recipient_email = validated_data['email']
                
                if recipient_email:
                    email_result = send_pdf_email(
                        to_email=recipient_email,
                        pdf_file_path=results['steps']['pdf_generation']['file_path'],
                        subject=f"Assessment Report - {validated_data['first_name']} {validated_data['last_name']}",
                        from_email=os.environ.get('SES_FROM_EMAIL')
                    )
                    results['steps']['email'] = email_result
                    print("Email sent successfully")
                else:
                    results['steps']['email'] = {
                        'status': 'skipped',
                        'reason': 'No recipient email provided'
                    }
                    print("Email sending skipped - no recipient email")
                    
            except Exception as e:
                results['steps']['email'] = {
                    'status': 'error',
                    'error': str(e)
                }
                print(f"Email sending failed: {str(e)}")
        else:
            results['steps']['email'] = {
                'status': 'skipped',
                'reason': 'PDF generation failed or no file path available'
            }
            print("Email sending skipped - PDF generation failed")
        
        # Determine overall success
        successful_steps = sum(1 for step in results['steps'].values() 
                             if step.get('status') == 'success')
        total_steps = len(results['steps'])
        
        overall_status = 'success' if successful_steps == total_steps else 'partial_success'
        
        # Prepare response
        response_data = {
            'message': 'Assessment processing completed',
            'record_id': record_id,
            'overall_status': overall_status,
            'successful_steps': successful_steps,
            'total_steps': total_steps,
            'results': results
        }
        
        return create_response(200, response_data)
        
    except Exception as e:
        print(f"Unexpected error in lambda_handler: {str(e)}")
        return create_response(500, {
            'error': 'Internal server error',
            'details': str(e),
            'timestamp': datetime.utcnow().isoformat()
        })


def create_response(status_code, body):
    """
    Create a properly formatted API Gateway response.
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': json.dumps(body)
    }
