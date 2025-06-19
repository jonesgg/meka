# AWS API Gateway + Lambda + DynamoDB Terraform Project

This Terraform project creates a complete serverless API infrastructure on AWS with:
- **API Gateway**: REST API with POST endpoint
- **Lambda Function**: Processes requests and stores data
- **DynamoDB**: NoSQL database for data storage

## Architecture

```
Client → API Gateway → Lambda Function → DynamoDB
```

## Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform installed (version >= 1.0)
- Python 3.9+ (for Lambda function)

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

4. **Build the Lambda function**
   ```bash
   chmod +x build_lambda.sh
   ./build_lambda.sh
   ```

5. **Initialize Terraform**
   ```bash
   cd terraform
   terraform init
   ```

6. **Plan the deployment**
   ```bash
   terraform plan
   ```

7. **Deploy the infrastructure**
   ```bash
   terraform apply
   ```

8. **Get the API endpoint URL**
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
    "message": "Hello World!"
  }'
```

### Example Response

```json
{
  "message": "Data successfully stored",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "name": "John Doe",
    "email": "john@example.com",
    "message": "Hello World!"
  }
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
│   └── lambda_function.py      # Lambda function code
├── build_lambda.sh             # Lambda packaging script
├── .gitignore                  # Git ignore file
└── README.md                   # This file
```

## Customization

### Lambda Function

The Lambda function (`lambda/lambda_function.py`) can be customized to:
- Add data validation
- Implement business logic
- Call external services
- Transform data before storage

### DynamoDB Schema

The current schema stores:
- `id`: Unique identifier (UUID)
- `data`: The original request data
- `created_at`: Timestamp of creation
- `source`: Source identifier

### API Gateway

The API Gateway is configured with:
- POST method at `/data` endpoint
- CORS headers enabled
- No authentication (can be added as needed)

## Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `aws_region` | AWS region for deployment | `us-east-1` |
| `project_name` | Name of the project | `meka-api` |
| `environment` | Environment name | `dev` |

## Cleanup

To destroy all resources:

```bash
cd terraform
terraform destroy
```

## Security Considerations

- The current setup has no authentication
- Consider adding API Gateway authentication
- Review IAM permissions for production use
- Enable CloudTrail for audit logging

## Monitoring

- Lambda logs are available in CloudWatch
- API Gateway metrics in CloudWatch
- DynamoDB metrics in CloudWatch

## Troubleshooting

### Common Issues

1. **Lambda deployment fails**: Ensure `lambda_function.zip` exists in the root directory
2. **Permission denied**: Check AWS credentials and IAM permissions
3. **API Gateway timeout**: Increase Lambda timeout if needed
4. **Terraform can't find files**: Make sure you're running terraform commands from the `terraform/` directory

### Logs

- Lambda logs: CloudWatch Logs
- API Gateway logs: CloudWatch Logs (if enabled)
- Terraform logs: Check the terminal output

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.
