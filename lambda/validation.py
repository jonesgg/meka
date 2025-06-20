"""
Validation module for incoming assessment data.
"""

import json
from jsonschema import validate, ValidationError
from typing import Dict, Any
from datetime import datetime

# Schema definition matching API Gateway schema
ASSESSMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "metadata": {
            "type": "object",
            "description": "Metadata about the assessment submission",
            "properties": {
                "date_sent": {
                    "type": "string",
                    "format": "date-time",
                    "description": "ISO 8601 timestamp of when the assessment was submitted"
                },
                "source": {
                    "type": "string",
                    "description": "Source of the assessment submission",
                    "default": "web"
                },
                "version": {
                    "type": "string",
                    "description": "Version of the assessment form",
                    "default": "1.0"
                }
            },
            "required": ["date_sent"],
            "additionalProperties": False
        },
        "first_name": {
            "type": "string",
            "description": "Name of the person",
            "minLength": 1,
            "maxLength": 35
        },
        "last_name": {
            "type": "string",
            "description": "Name of the person",
            "minLength": 1,
            "maxLength": 35
        },
        "email": {
            "type": "string",
            "format": "email",
            "description": "User email address",
            "minLength": 1,
            "maxLength": 100
        },
        "phone_number": {
            "type": "string",
            "description": "Contact phone number",
            "pattern": "^\\+?[1-9]\\d{1,14}$",
            "minLength": 10
        },
        "assessment_data": {
            "type": "object",
            "description": "Assessment responses",
            "properties": {
                "business_goals_and_financials": {
                    "type": "object",
                    "properties": {
                        "company_name": {"type": "string", "minLength": 1},
                        "company_industry": {
                            "type": "string",
                            "enum": [
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
                            ]
                        },
                        "number_of_employees": {"type": "number", "minimum": 0},
                        "current_business_value": {"type": "number", "minimum": 0},
                        "target_sale_price": {"type": "number", "minimum": 0},
                        "last_year_revenue": {"type": "number", "minimum": 0},
                        "last_year_profit": {"type": "number", "minimum": 0},
                        "current_year_estimated_revenue": {"type": "number", "minimum": 0},
                        "current_year_estimated_profit": {"type": "number", "minimum": 0},
                        "planned_exit_timeline": {
                            "type": "string",
                            "enum": ["0-1 year", "1-2 years", "3-5 years", "5+ years"]
                        },
                        "would_accept_offer": {
                            "type": "string",
                            "enum": ["yes", "no"]
                        },
                        "business_readiness": {
                            "type": "string",
                            "enum": [
                                "business would fall apart without me",
                                "business would struggle some but remain functioning",
                                "business would run well/independently with strong management"
                            ]
                        }
                    },
                    "required": [
                        "company_name",
                        "company_industry",
                        "number_of_employees",
                        "current_business_value",
                        "target_sale_price",
                        "last_year_revenue",
                        "last_year_profit",
                        "current_year_estimated_revenue",
                        "current_year_estimated_profit",
                        "planned_exit_timeline",
                        "would_accept_offer",
                        "business_readiness"
                    ],
                    "additionalProperties": False
                },
                "business_performance_and_transferability": {
                    "type": "object",
                    "properties": {
                        "financial_statements": {"type": "integer", "minimum": 1, "maximum": 6},
                        "profitability": {"type": "integer", "minimum": 1, "maximum": 6},
                        "customer_base": {"type": "integer", "minimum": 1, "maximum": 6},
                        "sales_growth": {"type": "integer", "minimum": 1, "maximum": 6},
                        "brand_value": {"type": "integer", "minimum": 1, "maximum": 6},
                        "marketing": {"type": "integer", "minimum": 1, "maximum": 6},
                        "market_position": {"type": "integer", "minimum": 1, "maximum": 6},
                        "customer_relationships": {"type": "integer", "minimum": 1, "maximum": 6},
                        "growth_strategy": {"type": "integer", "minimum": 1, "maximum": 6},
                        "revenue_streams": {"type": "integer", "minimum": 1, "maximum": 6},
                        "management_capability": {"type": "integer", "minimum": 1, "maximum": 6},
                        "leadership_roles": {"type": "integer", "minimum": 1, "maximum": 6},
                        "succession_planning": {"type": "integer", "minimum": 1, "maximum": 6},
                        "employee_turnover": {"type": "integer", "minimum": 1, "maximum": 6},
                        "business_processes": {"type": "integer", "minimum": 1, "maximum": 6},
                        "it_systems": {"type": "integer", "minimum": 1, "maximum": 6},
                        "operations_continuity": {"type": "integer", "minimum": 1, "maximum": 6},
                        "technology_systems": {"type": "integer", "minimum": 1, "maximum": 6},
                        "proprietary_tech": {"type": "integer", "minimum": 1, "maximum": 6},
                        "operational_processes": {"type": "integer", "minimum": 1, "maximum": 6},
                        "scalability": {"type": "integer", "minimum": 1, "maximum": 6},
                        "supplier_contracts": {"type": "integer", "minimum": 1, "maximum": 6},
                        "operating_expenses": {"type": "integer", "minimum": 1, "maximum": 6},
                        "risk_management": {"type": "integer", "minimum": 1, "maximum": 6},
                        "business_resilience": {"type": "integer", "minimum": 1, "maximum": 6},
                        "legal_contracts": {"type": "integer", "minimum": 1, "maximum": 6}
                    },
                    "required": [
                        "financial_statements",
                        "profitability",
                        "customer_base",
                        "sales_growth",
                        "brand_value",
                        "marketing",
                        "market_position",
                        "customer_relationships",
                        "growth_strategy",
                        "revenue_streams",
                        "management_capability",
                        "leadership_roles",
                        "succession_planning",
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
                    ],
                    "additionalProperties": False
                },
                "personal_readiness_for_business_owners": {
                    "type": "object",
                    "properties": {
                        "personal_identity": {"type": "integer", "minimum": 1, "maximum": 6},
                        "financial_plan": {"type": "integer", "minimum": 1, "maximum": 6},
                        "physical_health": {"type": "integer", "minimum": 1, "maximum": 6},
                        "energy_level": {"type": "integer", "minimum": 1, "maximum": 6},
                        "estate_plan": {"type": "integer", "minimum": 1, "maximum": 6},
                        "legal_protections": {"type": "integer", "minimum": 1, "maximum": 6},
                        "future_vision": {"type": "integer", "minimum": 1, "maximum": 6},
                        "family_communication": {"type": "integer", "minimum": 1, "maximum": 6},
                        "professional_advisors": {"type": "integer", "minimum": 1, "maximum": 6},
                        "process_confidence": {"type": "integer", "minimum": 1, "maximum": 6}
                    },
                    "required": [
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
                    ],
                    "additionalProperties": False
                }
            },
            "required": [
                "business_goals_and_financials",
                "business_performance_and_transferability", 
                "personal_readiness_for_business_owners"
            ],
            "additionalProperties": False
        }
    },
    "required": ["metadata", "first_name", "last_name", "email", "phone_number", "assessment_data"],
    "additionalProperties": False
}

def validate_assessment_data(data: Dict[Any, Any]) -> Dict[str, Any]:
    """
    Validates the incoming assessment data against the schema.
    Also ensures metadata.date_sent is present with current timestamp if not provided.
    
    Args:
        data: Dictionary containing the assessment data
        
    Returns:
        Dict: Validated and potentially enriched data
        
    Raises:
        ValidationError: If the data doesn't match the schema
    """
    # Create a copy of the data to avoid modifying the input
    validated_data = data.copy()
    
    # Ensure metadata exists
    if 'metadata' not in validated_data:
        validated_data['metadata'] = {}
    
    # Ensure date_sent exists
    if 'date_sent' not in validated_data['metadata']:
        validated_data['metadata']['date_sent'] = datetime.utcnow().isoformat()
    
    # Set default values for optional metadata fields
    if 'source' not in validated_data['metadata']:
        validated_data['metadata']['source'] = 'web'
    if 'version' not in validated_data['metadata']:
        validated_data['metadata']['version'] = '1.0'
    
    # Validate against schema
    validate(instance=validated_data, schema=ASSESSMENT_SCHEMA)
    
    return validated_data 