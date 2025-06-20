"""
Business assessment calculations module.
Processes validated assessment data and adds calculated fields.
"""

import json
from datetime import datetime
from typing import Dict, Any


def calculate_assessment_scores(assessment_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes validated assessment data and returns the same object with additional calculated fields.
    
    Args:
        assessment_data: Complete validated assessment data including all sections
        
    Returns:
        Dict: Original assessment data with additional calculated fields
    """
    # Create a copy of the original data to avoid modifying the input
    enriched_data = assessment_data.copy()
    
    # Extract the assessment sections for easier access
    business_goals = assessment_data['assessment_data']['business_goals_and_financials']
    business_performance = assessment_data['assessment_data']['business_performance_and_transferability']
    personal_readiness = assessment_data['assessment_data']['personal_readiness_for_business_owners']

    # Initialize calculated fields section
    assessment_calculations = {}

    # Industry-specific EBITDA multiples and margins
    industry = business_goals['company_industry']
    industry_data = {
        'Retail': {'multiple': 4.1, 'margin': 15.0},
        'Restaurants': {'multiple': 3.6, 'margin': 12.5},
        'Construction': {'multiple': 4.3, 'margin': 18.0},
        'Manufacturing': {'multiple': 4.6, 'margin': 19.2},
        'Professional Services': {'multiple': 4.5, 'margin': 26.7},
        'Healthcare (Non-Medical)': {'multiple': 5.0, 'margin': 22.2},
        'E-commerce': {'multiple': 4.8, 'margin': 20.3},
        'Wholesale/Distribution': {'multiple': 4.2, 'margin': 14.9},
        'Auto Repair': {'multiple': 3.8, 'margin': 17.7},
        'Beauty/Personal Care': {'multiple': 3.7, 'margin': 15.4},
        'IT Services': {'multiple': 5.3, 'margin': 25.6},
        'Other': {'multiple': 4.1, 'margin': 17.5}
    }
    
    selected_industry = industry_data.get(industry, industry_data['Other'])
    assessment_calculations['ebitda_multiple'] = selected_industry['multiple']
    assessment_calculations['ebitda_margin'] = selected_industry['margin']

    # Financial calculations with division by zero protection
    assessment_calculations['revenue_per_employee'] = (
        business_goals['last_year_revenue'] / business_goals['number_of_employees'] 
        if business_goals['number_of_employees'] > 0 else 0
    )
    assessment_calculations['last_year_profit_percentage'] = (
        business_goals['last_year_profit'] / business_goals['last_year_revenue'] 
        if business_goals['last_year_revenue'] > 0 else 0
    )
    assessment_calculations['current_year_profit_percentage'] = (
        business_goals['current_year_estimated_profit'] / business_goals['current_year_estimated_revenue'] 
        if business_goals['current_year_estimated_revenue'] > 0 else 0
    )
    assessment_calculations['two_year_average_revenue'] = (
        business_goals['current_year_estimated_revenue'] + business_goals['last_year_revenue']
    ) / 2
    assessment_calculations['two_year_average_profit'] = (
        business_goals['current_year_estimated_profit'] + business_goals['last_year_profit']
    ) / 2
    assessment_calculations['two_year_average_self_reported_multiple'] = (
        assessment_calculations['two_year_average_revenue'] / assessment_calculations['two_year_average_profit'] 
        if assessment_calculations['two_year_average_profit'] > 0 else 0
    )
    assessment_calculations['range_of_value_low'] = assessment_calculations['two_year_average_profit'] * 3
    assessment_calculations['current_value_information_provided'] = (
        assessment_calculations['two_year_average_profit'] * assessment_calculations['ebitda_margin'] / 100
    )
    assessment_calculations['range_of_value_high'] = (
        assessment_calculations['two_year_average_profit'] * assessment_calculations['ebitda_multiple'] * 1.4
    )
    assessment_calculations['profit_gap_surplus'] = (
        (business_goals['current_year_estimated_revenue'] * assessment_calculations['last_year_profit_percentage']) - 
        (business_goals['current_year_estimated_revenue'] * assessment_calculations['ebitda_margin'] / 100)
    )
    assessment_calculations['exit_planning_value_opportunity'] = (
        assessment_calculations['range_of_value_high'] - assessment_calculations['current_value_information_provided']
    )
    
    # Calculate percentage scores for assessment sections (0-100%)
    # Business Performance and Transferability Score (26 fields, each 1-6 scale)
    business_performance_values = [value for value in business_performance.values() if isinstance(value, int)]
    business_performance_total = sum(business_performance_values)
    business_performance_max_possible = len(business_performance_values) * 6  # Max score if all 6s
    assessment_calculations['company_transferability_score'] = round(
        (business_performance_total / business_performance_max_possible * 100) if business_performance_max_possible > 0 else 0, 1
    )
    
    # Personal Readiness Score (10 fields, each 1-6 scale)
    personal_readiness_values = [value for value in personal_readiness.values() if isinstance(value, int)]
    personal_readiness_total = sum(personal_readiness_values)
    personal_readiness_max_possible = len(personal_readiness_values) * 6  # Max score if all 6s
    assessment_calculations['personal_readiness_score'] = round(
        (personal_readiness_total / personal_readiness_max_possible * 100) if personal_readiness_max_possible > 0 else 0, 1
    )

    # Add calculated fields to the enriched data
    enriched_data['assessment_calculations'] = assessment_calculations
    
    return enriched_data
