terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# DynamoDB Table
resource "aws_dynamodb_table" "data_table" {
  name           = "${var.project_name}-data-table"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Lambda to access DynamoDB
resource "aws_iam_policy" "lambda_dynamodb_policy" {
  name        = "${var.project_name}-lambda-dynamodb-policy"
  description = "Policy for Lambda to access DynamoDB"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = aws_dynamodb_table.data_table.arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# IAM Policy for Lambda to send emails via SES
resource "aws_iam_policy" "lambda_ses_policy" {
  name        = "${var.project_name}-lambda-ses-policy"
  description = "Policy for Lambda to send emails via SES"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail",
          "ses:VerifyEmailIdentity",
          "ses:GetSendQuota"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attach policies to Lambda role
resource "aws_iam_role_policy_attachment" "lambda_dynamodb_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_dynamodb_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambda_ses_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_ses_policy.arn
}

# Lambda Function
resource "aws_lambda_function" "api_lambda" {
  filename         = "../lambda_function.zip"
  function_name    = "${var.project_name}-api-lambda"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.9"
  timeout         = 60  # Increased timeout for complex processing
  memory_size     = 512  # Increased memory for PDF generation

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.data_table.name
      SES_FROM_EMAIL = var.ses_from_email
      DEFAULT_RECIPIENT_EMAIL = var.default_recipient_email
    }
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# API Gateway REST API
resource "aws_api_gateway_rest_api" "api" {
  name        = "${var.project_name}-api"
  description = "API Gateway for ${var.project_name}"

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# API Gateway Resource
resource "aws_api_gateway_resource" "api_resource" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "data"
}

# API Gateway Request Validator
resource "aws_api_gateway_request_validator" "api_validator" {
  name                        = "${var.project_name}-request-validator"
  rest_api_id                 = aws_api_gateway_rest_api.api.id
  validate_request_body       = true
  validate_request_parameters = false
}

# API Gateway Method
resource "aws_api_gateway_method" "api_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.api_resource.id
  http_method   = "POST"
  authorization = "NONE"
  
  request_validator_id = aws_api_gateway_request_validator.api_validator.id
  
  request_models = {
    "application/json" = aws_api_gateway_model.api_model.name
  }
}

# API Gateway Model (JSON Schema for validation)
resource "aws_api_gateway_model" "api_model" {
  rest_api_id  = aws_api_gateway_rest_api.api.id
  name         = "${var.project_name}-request-model"
  description  = "Request model for data processing API"
  content_type = "application/json"

  schema = jsonencode({
    type = "object"
    properties = {
      metadata = {
        type = "object"
        description = "Metadata about the assessment submission"
        properties = {
          date_sent = {
            type = "string"
            format = "date-time"
            description = "ISO 8601 timestamp of when the assessment was submitted"
          }
          source = {
            type = "string"
            description = "Source of the assessment submission"
            default = "web"
          }
          version = {
            type = "string"
            description = "Version of the assessment form"
            default = "1.0"
          }
        }
        required = ["date_sent"]
        additionalProperties = false
      }
      first_name = {
        type = "string"
        description = "Name of the person"
        minLength = 1
        maxLength = 35
      }
      last_name = {
        type = "string"
        description = "Name of the person"
        minLength = 1
        maxLength = 35
      }
      email = {
        type = "string"
        format = "email"
        description = "User email address"
        minLength = 1
        maxLength = 100
      }
      phone_number = {
        type = "string"
        description = "Contact phone number"
        pattern = "^\\+?[1-9]\\d{1,14}$"
        minLength = 10
      }
      assessment_data = {
        type = "object"
        description = "Assessment responses"
        properties = {

          business_goals_and_financials = {
            type = "object"
            description = "Assessment responses"
            properties = {
              company_industry = {
                type = "string"
                enum = [
                  "Retail",
                  "Restaurants",
                  "Construction",
                  "Manufacturing",
                  "Professional Services",
                  "Healthcare (Non-Medical)",
                  "E-commerce",
                  "Wholesale/Distribution",
                  "Auto Repair",
                  "Beauty/Personal Care",
                  "IT Services",
                  "Other"
                ],
                description = "Company Industry"
              }
              planned_exit_timeline = {
                type = "string",
                enum = [
                  "0-1 year",
                  "1-2 years",
                  "3-5 years",
                  "5+ years",
                ],
                description = "How soon do you plan to exit? or sell your company?"
              }
              would_accept_offer = {
                type = "string",
                enum = [
                  "yes",
                  "no",
                ],
                description = "If you received an acceptable offer in next 30-45 days, would you consider?"
              }
              business_readiness = {
                type = "string",
                enum = [
                  "business would fall apart without me",
                  "business would struggle some but remain functioning",
                  "business would run well/independently with strong management",
                ],
                description = "how would your business perform if you left tomorrow?"
              }
              company_name = {
                type = "string"
                minLength = 1
                description = "Company Name"
              }
              number_of_employees = {
                type = "number"
                minimum = 0
                description = "Number of Employees"
              }
              current_business_value = {
                type = "number"
                minimum = 0
                description = "What do you think your business is worth currently? (Most businesses"
              }
              target_sale_price = {
                type = "number"
                minimum = 0
                description = "What Price do you want your company to sell for at exit?"
              }
              last_year_revenue = {
                type = "number"
                minimum = 0
                description = "What was your Total Revenue for Last Year?"
              }
              last_year_profit = {
                type = "number"
                minimum = 0
                description = "What was your Total Profit for Last Year?"
              }
              current_year_estimated_revenue = {
                type = "number"
                minimum = 0
                description = "What is your Estimated Total Revenue for This Year?"
              }
              current_year_estimated_profit = {
                type = "number"
                minimum = 0
                description = "What is your Estimated Total Profit for This Year?"
              }
            }
            required = [
              "company_name",
              "company_industry",
              "planned_exit_timeline",
              "would_accept_offer",
              "business_readiness",
              "number_of_employees",
              "current_business_value",
              "target_sale_price",
              "last_year_revenue",
              "last_year_profit",
              "current_year_estimated_revenue",
              "current_year_estimated_profit"
            ]
            additionalProperties = false
          }

          business_performance_and_transferability = {
            type = "object"
            description = "Assessment responses"
            properties = {
              financial_statements = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How audited, current, & due diligence-ready are your financial statements?"
              }
              profitability_trends = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How clear & consistent are your profitability & cash flow trends?"
              }
              business_valuation = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How credible & recent is your business valuation?"
              }
              customer_base_diversity = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How diversified is your customer base to reduce revenue risk?"
              }
              customer_contracts = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How documented, current, & transferable are customer contracts?"
              }
              sales_growth = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How consistent is your sales growth over the past three years?"
              }
              brand_value = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How clear & customer-recognized is your brand's unique value"
              }
              marketing_effectiveness = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How effective & measurable are your documented marketing"
              }
              market_position = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How strong is your market position compared to competitors?"
              }
              customer_relationships = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How documented are customer relationships for annual revenue"
              }
              growth_strategy = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How clear is your documented growth strategy for new markets?"
              }
              revenue_streams = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How well-identified are potential new revenue streams?"
              }
              management_capability = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How capable is your management team of running the business"
              }
              leadership_roles = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How clearly documented are leadership roles & responsibilities?"
              }
              succession_plan = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How robust is your succession plan for key leadership positions?"
              }
              employee_turnover = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How low is employee turnover & high are morale & competency?"
              }
              business_processes = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How well-documented & automated are core business processes?"
              }
              it_systems = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How secure, scalable, & licensed are your IT systems?"
              }
              operations_continuity = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How seamlessly can operations continue during an ownership"
              }
              technology_systems = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How current, secure, & licensed are your technology systems?"
              }
              proprietary_tech = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How valuable are proprietary tech or innovations to your advantage?"
              }
              operational_processes = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How optimized are key operational processes for cost-effectiveness?"
              }
              scalability = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How scalable are operations to handle increased demand?"
              }
              supplier_contracts = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How favorable, documented, & transferable are supplier contracts?"
              }
              operating_expenses = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How optimized are your operating expenses for profitability?"
              }
              risk_management = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How comprehensive is your documented risk management plan?"
              }
              business_resilience = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How resilient is your business to market or industry volatility?"
              }
              legal_contracts = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How current & documented are all legal contracts? No Legal Issues?"
              }
            }
            required = [
              "financial_statements",
              "profitability_trends",
              "business_valuation",
              "customer_base_diversity",
              "customer_contracts",
              "sales_growth",
              "brand_value",
              "marketing_effectiveness",
              "market_position",
              "customer_relationships",
              "growth_strategy",
              "revenue_streams",
              "management_capability",
              "leadership_roles",
              "succession_plan",
              "employee_turnover",
              "business_processes",
              "it_systems",
              "operations_continuity",
              "technology_systems",
              "proprietary_tech",
              "operational_processes",
              "scalability",
              "supplier_contracts",
              "operating_expenses",
              "risk_management",
              "business_resilience",
              "legal_contracts"
            ]
            additionalProperties = false
          }

          personal_readiness_for_business_owners = {
            type = "object"
            description = "Assessment responses"
            properties = {
              personal_identity = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How clear is your personal identity beyond being a business owner?"
              }
              financial_plan = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How secure is your personal financial plan post-sale?"
              }
              physical_health = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How strong is your physical health heading into next phase of life?"
              }
              energy_level = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How is your level of energy for the sale process?"
              }
              estate_plan = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How current is your personal estate plan for post-sale?"
              }
              legal_protections = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How clear are your legal protections for sale proceeds?"
              }
              future_vision = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How clear is your vision for life after the sale?"
              }
              family_communication = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How open are you with family about the sale's impact?"
              }
              professional_advisors = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How well do you leverage professional advisors?"
              }
              process_confidence = {
                type = "integer"
                minimum = 1
                maximum = 6
                description = "How confident are you in navigating the process with potential"
              }
            }
            required = [
              "personal_identity",
              "financial_plan",
              "physical_health",
              "energy_level",
              "estate_plan",
              "legal_protections",
              "future_vision",
              "family_communication",
              "professional_advisors",
              "process_confidence"
            ]
            additionalProperties = false
          }

        }
        additionalProperties = false
      }
    }
    required = ["metadata", "first_name", "last_name", "email", "phone_number", "assessment_data"]
    additionalProperties = false
  })
}

# API Gateway Integration
resource "aws_api_gateway_integration" "api_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.api_resource.id
  http_method             = aws_api_gateway_method.api_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.api_lambda.invoke_arn
}

# Lambda Permission for API Gateway
resource "aws_lambda_permission" "api_gateway_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "api_deployment" {
  depends_on = [
    aws_api_gateway_integration.api_integration,
  ]

  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = var.environment

  lifecycle {
    create_before_destroy = true
  }
}

# Outputs
output "api_gateway_url" {
  description = "URL of the API Gateway endpoint"
  value       = "${aws_api_gateway_deployment.api_deployment.invoke_url}/data"
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.data_table.name
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.api_lambda.function_name
} 