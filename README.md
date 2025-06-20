# AWS API Gateway + Lambda + DynamoDB + SES Terraform Project

This Terraform project creates a complete serverless data processing pipeline on AWS with:
- **API Gateway**: REST API with POST endpoint
- **Lambda Function**: Comprehensive data processing pipeline
- **DynamoDB**: NoSQL database for data storage
- **SES**: Email service for sending PDF reports

## Architecture

```
Client → API Gateway → Lambda Function → [Calculations → Excel → DynamoDB → PDF → Email]
```

## Lambda Processing Pipeline

The Lambda function orchestrates a complete data processing pipeline:

1. **Calculations** (`calculations.py`): Performs business logic and calculations on incoming data
2. **Excel Export** (`excel.py`): Writes data to Excel
3. **DynamoDB Storage** (`dynamodb.py`): Stores processed data in DynamoDB
4. **PDF Generation** (`pdf_generator.py`): Creates PDF reports from processed data
5. **Email Sending** (`email.py`): Sends PDF reports via AWS SES

## Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform installed (version >= 1.0)
- Python 3.9+ (for Lambda function)
- SES email addresses verified (for email functionality)

## Quick Start

1. **Clone and navigate to the project directory**
   ```bash
   cd /path/to/your/project
   ```

2. **Configure your AWS credentials**
   ```bash
   aws configure
   ```

3. **Copy and customize the variables file**
   ```bash
   cp terraform/terraform.tfvars.example terraform/terraform.tfvars
   # Edit terraform/terraform.tfvars with your preferred values
   ```

4. **Verify SES email addresses** (required for email functionality)
   ```bash
   # Verify your sender email
   aws ses verify-email-identity --email-address your-sender@domain.com
   
   # Verify your recipient email
   aws ses verify-email-identity --email-address your-recipient@domain.com
   ```

5. **Build the Lambda function**
   ```bash
   chmod +x build_lambda.sh
   ./build_lambda.sh
   ```

6. **Initialize Terraform**
   ```bash
   cd terraform
   terraform init
   ```

7. **Plan the deployment**
   ```bash
   terraform plan
   ```

8. **Deploy the infrastructure**
   ```bash
   terraform apply
   ```

9. **Get the API endpoint URL**
   ```bash
   terraform output api_gateway_url
   ```

## Usage

### Making API Calls

Once deployed, you can make POST requests to your API endpoint:

```bash
curl -X POST https://your-api-gateway-url/dev/data \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "financial_data": {
      "revenue": 50000,
      "expenses": 30000,
      "profit": 20000
    },
    "analytics_data": {
      "page_views": 1000,
      "conversions": 50,
      "bounce_rate": 0.25
    }
  }'
```

### Example Response

```json
{
  "message": "Data processing pipeline completed",
  "record_id": "550e8400-e29b-41d4-a716-446655440000",
  "overall_status": "success",
  "successful_steps": 5,
  "total_steps": 5,
  "results": {
    "record_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2024-01-15T10:30:00.000Z",
    "steps": {
      "calculations": {
        "status": "success",
        "data": { /* processed data with calculations */ }
      },
      "excel": {
        "status": "success",
        "filename": "data_report_20240115_103000.csv",
      },
      "dynamodb": {
        "status": "success",
        "record_id": "550e8400-e29b-41d4-a716-446655440000"
      },
      "pdf_generation": {
        "status": "success",
        "filename": "data_report_20240115_103000.pdf",
      },
      "email": {
        "status": "success",
        "message_id": "0000018a12345678-12345678-1234-1234-1234-123456789012-000000"
      }
    }
  },
  "original_data": { /* original request data */ }
}
```

## Project Structure

```
.
├── terraform/
│   ├── main.tf                 # Main Terraform configuration
│   ├── variables.tf            # Variable definitions
│   ├── outputs.tf              # Output definitions
│   └── terraform.tfvars.example # Example variable values
├── lambda/
│   ├── lambda_function.py      # Main Lambda orchestrator
│   ├── calculations.py         # Business logic & calculations
│   ├── excel.py                # Excel/CSV operations
│   ├── dynamodb.py             # DynamoDB operations
│   ├── pdf_generator.py        # PDF generation
│   ├── email.py                # SES email operations
│   └── requirements.txt        # Python dependencies
├── build_lambda.sh             # Lambda packaging script
├── .gitignore                  # Git ignore file
└── README.md                   # This file
```

## Lambda Modules

### Calculations Module (`calculations.py`)
- Processes incoming data and performs calculations
- Supports financial metrics, analytics, and generic calculations
- Generates summaries and metadata

### Excel Module (`excel.py`)
- Writes data to CSV format (Excel-compatible)
- Supports Microsoft Graph API integration (placeholder)

### DynamoDB Module (`dynamodb.py`)
- Stores processed data with metadata

### PDF Generator Module (`pdf_generator.py`)
- Creates PDF reports from processed data

### Email Module (`email.py`)
- Sends PDF reports via AWS SES
- Supports attachments and HTML emails
- Includes email verification utilities

## Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `aws_region` | AWS region for deployment | `us-east-1` |
| `project_name` | Name of the project | `meka-api` |
| `environment` | Environment name | `dev` |
| `ses_from_email` | SES sender email | `noreply@yourdomain.com` |
| `default_recipient_email` | Default recipient email | `reports@yourdomain.com` |

## Environment Variables

The Lambda function uses these environment variables:
- `DYNAMODB_TABLE`: DynamoDB table name
- `SES_FROM_EMAIL`: Email address to send from
- `DEFAULT_RECIPIENT_EMAIL`: Default recipient email

## Cleanup

To destroy all resources:

```bash
cd terraform
terraform destroy
```

## Security Considerations

- IAM policies follow least privilege principle
- SES emails must be verified before sending
- Consider adding API Gateway authentication for production

## Monitoring

- Lambda logs are available in CloudWatch
- API Gateway metrics in CloudWatch
- DynamoDB metrics in CloudWatch
- SES sending statistics in CloudWatch

## Troubleshooting

### Common Issues

1. **Lambda deployment fails**: Ensure `lambda_function.zip` exists in the root directory
2. **Permission denied**: Check AWS credentials and IAM permissions
3. **API Gateway timeout**: Increase Lambda timeout if needed (currently 60 seconds)
4. **SES email not sent**: Verify email addresses in SES console

### SES Setup

1. **Verify sender email**:
   ```bash
   aws ses verify-email-identity --email-address your-sender@domain.com
   ```

2. **Verify recipient email**:
   ```bash
   aws ses verify-email-identity --email-address your-recipient@domain.com
   ```

3. **Check SES sending limits**:
   ```bash
   aws ses get-send-quota
   ```

### Logs

- Lambda logs: CloudWatch Logs
- API Gateway logs: CloudWatch Logs (if enabled)
- DynamoDB metrics: CloudWatch
- SES sending statistics: CloudWatch

## Extending the Project

### Adding New Calculations
Edit `lambda/calculations.py` to add new calculation types and business logic.

### Custom PDF Templates
Modify `lambda/pdf_generator.py` to add new PDF templates and formatting.

### Additional Data Sources
Extend the Lambda function to integrate with other AWS services or external APIs.

### Microsoft Graph Integration
Uncomment and configure the Microsoft Graph API integration in `lambda/excel.py`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.
