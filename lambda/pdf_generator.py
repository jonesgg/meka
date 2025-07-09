"""
PDF generation module for creating beautiful business assessment reports using HTML/CSS.
"""

import os
from datetime import datetime
from typing import Dict, Any
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def format_currency(value: float) -> str:
    """Format a number as currency."""
    return f"${value:,.2f}" if value is not None else "$0.00"


def format_percentage(value: float) -> str:
    """Format a number as percentage."""
    return f"{value:.1f}%" if value is not None else "0.0%"


def format_number(value: float) -> str:
    """Format a number with commas."""
    return f"{value:,.0f}" if value is not None else "0"


def create_bar_chart(data: Dict[str, Any]) -> str:
    """Create a bar chart showing assessment scores and return as base64 string."""
    # Set matplotlib to use Agg backend for server environments
    plt.switch_backend('Agg')
    
    # Extract scores
    calc_data = data.get('assessment_calculations', {})
    business_score = calc_data.get('company_transferability_score', 0)
    personal_score = calc_data.get('personal_readiness_score', 0)
    
    # Create figure with clean styling
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor('white')
    
    # Data for the bar chart
    categories = ['Business\nTransferability', 'Personal\nReadiness']
    scores = [business_score, personal_score]
    colors = ['#007bff', '#6c757d']
    
    # Create bars
    bars = ax.bar(categories, scores, color=colors, alpha=0.8, width=0.6)
    
    # Customize the chart
    ax.set_ylim(0, 100)
    ax.set_ylabel('Score (%)', fontsize=12, color='#000000', fontweight='600')
    ax.set_title('Assessment Scores Overview', fontsize=14, color='#000000', fontweight='700', pad=20)
    
    # Style the axes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#e0e0e0')
    ax.spines['bottom'].set_color('#e0e0e0')
    ax.tick_params(colors='#666666')
    ax.grid(axis='y', alpha=0.3, color='#e0e0e0')
    
    # Add value labels on bars
    for bar, score in zip(bars, scores):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{score:.1f}%', ha='center', va='bottom',
                fontsize=12, fontweight='600', color='#000000')
    
    # Add benchmark line at 75%
    ax.axhline(y=75, color='#28a745', linestyle='--', alpha=0.7, linewidth=2)
    ax.text(0.02, 77, 'Excellent (75%+)', fontsize=10, color='#28a745', fontweight='600')
    
    plt.tight_layout()
    
    # Convert to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return image_base64


def create_bell_curve_chart(data: Dict[str, Any]) -> str:
    """Create a bell curve chart with standard deviation markers and return as base64 string."""
    # Set matplotlib to use Agg backend for server environments
    plt.switch_backend('Agg')
    
    # Extract scores
    calc_data = data.get('assessment_calculations', {})
    business_score = calc_data.get('company_transferability_score', 0)
    personal_score = calc_data.get('personal_readiness_score', 0)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor('white')
    
    # Bell curve parameters (assuming mean=50, std=15 for assessment scores)
    mean = 50
    std = 15
    x = np.linspace(0, 100, 1000)
    y = (1/(std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean) / std) ** 2)
    
    # Plot the bell curve
    ax.plot(x, y, color='#007bff', linewidth=2, alpha=0.8)
    ax.fill_between(x, y, alpha=0.2, color='#007bff')
    
    # Add standard deviation markers
    std_positions = [mean - 2*std, mean - std, mean, mean + std, mean + 2*std]
    std_labels = ['-2σ', '-1σ', 'μ', '+1σ', '+2σ']
    
    for pos, label in zip(std_positions, std_labels):
        if 0 <= pos <= 100:
            y_val = (1/(std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((pos - mean) / std) ** 2)
            ax.axvline(x=pos, color='#6c757d', linestyle='--', alpha=0.6)
            ax.text(pos, y_val + 0.002, label, ha='center', va='bottom',
                   fontsize=10, color='#666666', fontweight='600')
    
    # Mark user scores
    for score, label, color in [(business_score, 'Business', '#007bff'), 
                                (personal_score, 'Personal', '#28a745')]:
        if 0 <= score <= 100:
            y_val = (1/(std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((score - mean) / std) ** 2)
            ax.plot(score, y_val, 'o', color=color, markersize=8, markeredgecolor='white', markeredgewidth=2)
            ax.annotate(f'{label}\n{score:.1f}%', 
                       xy=(score, y_val), xytext=(score, y_val + 0.008),
                       ha='center', va='bottom', fontsize=10, fontweight='600', color=color,
                       arrowprops=dict(arrowstyle='->', color=color, alpha=0.7))
    
    # Customize the chart
    ax.set_xlim(0, 100)
    ax.set_xlabel('Assessment Score (%)', fontsize=12, color='#000000', fontweight='600')
    ax.set_ylabel('Probability Density', fontsize=12, color='#000000', fontweight='600')
    ax.set_title('Score Distribution Analysis', fontsize=14, color='#000000', fontweight='700', pad=20)
    
    # Style the axes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#e0e0e0')
    ax.spines['bottom'].set_color('#e0e0e0')
    ax.tick_params(colors='#666666')
    ax.grid(axis='x', alpha=0.3, color='#e0e0e0')
    
    plt.tight_layout()
    
    # Convert to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return image_base64


def get_css_styles():
    """Return the CSS styles for the PDF report with black/white/blue color scheme."""
    return """
    @page {
        size: A4;
        margin: 0.5in;
    }
    
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
            'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
            sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        line-height: 1.6;
        color: #000000;
        margin: 0;
        padding: 0;
        background: #ffffff;
    }
    
    .header {
        background: linear-gradient(135deg, #000000 0%, #333333 100%);
        color: white;
        padding: 2rem;
        margin-bottom: 30px;
        border-radius: 12px;
    }
    
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 2rem;
    }
    
    .header-logo {
        flex: 0 0 auto;
    }
    
    .logo-text {
        font-size: 2rem;
        font-weight: 700;
        color: white;
        margin: 0;
    }
    
    .header-title {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        text-align: right;
    }
    
    .header h1 {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }
    
    .title-accent-line {
        width: 80px;
        height: 4px;
        background: #007bff;
        margin-top: 0.5rem;
        border-radius: 2px;
    }
    
    .company-info {
        background: #ffffff;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 25px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    .company-info h2 {
        margin: 0 0 15px 0;
        color: #000000;
        font-size: 24px;
        font-weight: 700;
    }
    
    .info-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 15px;
    }
    
    .info-item {
        background: #f8f9fa;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    
    .info-item strong {
        color: #000000;
        display: block;
        margin-bottom: 5px;
        font-weight: 600;
    }
    
    .section {
        margin-bottom: 40px;
        page-break-inside: avoid;
    }
    
    .section h2 {
        color: #000000;
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 3px solid #007bff;
    }
    
    .score-summary {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 25px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    .score-summary h3 {
        margin: 0 0 15px 0;
        color: #000000;
        font-size: 20px;
        font-weight: 600;
    }
    
    .percentage {
        font-size: 48px;
        font-weight: 700;
        color: #007bff;
        margin: 0;
    }
    
    .data-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 25px;
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        border: 1px solid #e0e0e0;
    }
    
    .data-table thead {
        background: linear-gradient(135deg, #000000 0%, #333333 100%);
        color: white;
    }
    
    .data-table th {
        padding: 15px;
        text-align: left;
        font-weight: 600;
        font-size: 16px;
    }
    
    .data-table td {
        padding: 12px 15px;
        border-bottom: 1px solid #f0f0f0;
    }
    
    .data-table tbody tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    
    .score {
        font-weight: 700;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 14px;
    }
    
    .score.high {
        background-color: #e7f3ff;
        color: #0056b3;
    }
    
    .score.medium {
        background-color: #f8f9fa;
        color: #666666;
    }
    
    .score.low {
        background-color: #f8f9fa;
        color: #333333;
    }
    
    .page-break {
        page-break-before: always;
    }
    
    .timestamp {
        text-align: center;
        color: #666666;
        font-size: 12px;
        margin-top: 30px;
        padding-top: 20px;
        border-top: 1px solid #e0e0e0;
    }
    
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
        margin-bottom: 25px;
    }
    
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    .metric-card h4 {
        margin: 0 0 10px 0;
        color: #000000;
        font-size: 16px;
        font-weight: 600;
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #007bff;
        margin-bottom: 5px;
    }
    
    .metric-label {
        color: #666666;
        font-size: 14px;
    }
    
    .charts-section {
        margin-top: 40px;
        page-break-inside: avoid;
    }
    
    .charts-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 30px;
        margin-top: 20px;
    }
    
    .chart-container {
        background: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        text-align: center;
    }
    
    .chart-container h3 {
        color: #000000;
        font-size: 18px;
        font-weight: 600;
        margin: 0 0 15px 0;
    }
    
    .chart-container img {
        max-width: 100%;
        height: auto;
        border-radius: 8px;
    }
    """


def get_score_class(score: int) -> str:
    """Get CSS class based on score value."""
    if score >= 5:
        return "score-excellent"
    elif score >= 4:
        return "score-good"
    elif score >= 3:
        return "score-fair"
    else:
        return "score-poor"


def get_business_question(metric_name: str) -> str:
    """Get the full question text for business performance metrics."""
    
    question_map = {
        "Financial Statements": "How audited, current, & due diligence-ready are your financial statements?",
        "Profitability": "How clear & consistent are your profitability & cash flow trends?",
        "Customer Base": "How diversified is your customer base to reduce revenue risk?",
        "Sales Growth": "How consistent is your sales growth over the past three years?",
        "Brand Value": "How clear & customer-recognized is your brand's unique value proposition?",
        "Marketing": "How effective & measurable are your documented marketing campaigns?",
        "Market Position": "How strong is your market position compared to competitors?",
        "Customer Relationships": "How documented are customer relationships for annual revenue retention?",
        "Growth Strategy": "How clear is your documented growth strategy for new markets/segments?",
        "Revenue Streams": "How well-identified are potential new revenue streams?",
        "Management Capability": "How capable is your management team of running the business independently?",
        "Leadership Roles": "How clearly documented are leadership roles & responsibilities?",
        "Succession Planning": "How robust is your succession plan for key leadership positions?",
        "Employee Turnover": "How low is employee turnover & high are morale & competency?",
        "Business Processes": "How well-documented & automated are core business processes?",
        "IT Systems": "How secure, scalable, & licensed are your IT systems?",
        "Operations Continuity": "How seamlessly can operations continue during an ownership transition?",
        "Technology Systems": "How current, secure, & licensed are your technology systems?",
        "Proprietary Tech": "How valuable are proprietary tech or innovations to your competitive advantage?",
        "Operational Processes": "How optimized are key operational processes for cost-effectiveness?",
        "Scalability": "How scalable are operations to handle increased demand?",
        "Supplier Contracts": "How favorable, documented, & transferable are supplier contracts?",
        "Operating Expenses": "How optimized are your operating expenses for profitability?",
        "Risk Management": "How comprehensive is your documented risk management plan?",
        "Business Resilience": "How resilient is your business to market or industry volatility?",
        "Legal Contracts": "How current & documented are all legal contracts? No Legal Issues?"
    }
    
    return question_map.get(metric_name, metric_name)


def get_business_feedback(metric_name: str, score: int) -> tuple:
    """Get both improvement and maintenance feedback for business performance metrics."""
    
    feedback_map = {
        "Financial Statements": {
            "improve": "Implement monthly financial reporting with profit and cash flow tracking to CPA standards. Get quarterly audited financial statements and maintain clean books.",
            "maintain": "Continue your strong financial documentation practices. Consider upgrading to more advanced financial analytics and forecasting tools."
        },
        "Profitability": {
            "improve": "Conduct a detailed profitability analysis by product/service line. Focus on high-margin offerings and reduce or eliminate low-margin activities.",
            "maintain": "Maintain your strong profit margins. Look for opportunities to expand high-margin services and optimize pricing strategies."
        },
        "Customer Base": {
            "improve": "Develop a sales strategy to target new customer segments and reduce reliance on top customers. Diversify your customer portfolio to reduce concentration risk.",
            "maintain": "Continue building strong customer relationships. Consider loyalty programs and regular customer satisfaction surveys to maintain your strong base."
        },
        "Sales Growth": {
            "improve": "Create a 3-year growth plan with clear market/product targets within 3 months. Focus on new customer acquisition and expansion of existing accounts.",
            "maintain": "Maintain your strong sales growth trajectory. Document your successful sales processes and consider expanding to new markets."
        },
        "Brand Value": {
            "improve": "Conduct customer surveys to refine UVP and launch a branding campaign to improve marketing consistency and brand recognition.",
            "maintain": "Continue investing in brand development and marketing. Consider trademark protection and brand extension opportunities."
        },
        "Marketing": {
            "improve": "Develop a comprehensive marketing plan with clear ROI tracking and digital marketing campaigns to increase visibility.",
            "maintain": "Maintain your effective marketing approach. Consider expanding successful campaigns and exploring new marketing channels."
        },
        "Market Position": {
            "improve": "Conduct a market analysis to identify and strengthen competitive positioning. Develop unique value propositions that differentiate your business.",
            "maintain": "Continue strengthening your market position. Monitor competitors and stay ahead of industry trends."
        },
        "Customer Relationships": {
            "improve": "Analyze sales trends, implement customer retention programs, and invest in sales training to improve relationship management.",
            "maintain": "Maintain excellent customer relationships. Consider customer advisory boards and expanded service offerings."
        },
        "Growth Strategy": {
            "improve": "Develop a 3-year growth plan targeting 15%+ revenue increase with actionable plans in place within 2 months.",
            "maintain": "Continue executing your strong growth strategy. Consider strategic partnerships or acquisition opportunities."
        },
        "Revenue Streams": {
            "improve": "Pilot two new revenue streams and document potential impact on business. Focus on recurring revenue opportunities.",
            "maintain": "Diversify revenue streams further and test new service offerings while maintaining current strengths."
        },
        "Management Capability": {
            "improve": "Provide management training for 30+ days without owner input. Create clear management structure and delegation systems.",
            "maintain": "Continue developing management capabilities. Consider leadership development programs and succession planning."
        },
        "Leadership Roles": {
            "improve": "Create an org chart and detailed role descriptions, storing them in a shared system accessible to all key roles.",
            "maintain": "Continue strong leadership development. Document processes and consider cross-training for critical roles."
        },
        "Succession Planning": {
            "improve": "Develop a succession plan with backup roles identified for all key roles and review it annually.",
            "maintain": "Maintain and regularly update your succession plan. Provide ongoing leadership development opportunities."
        },
        "Employee Turnover": {
            "improve": "Conduct employee satisfaction surveys and address concerns with retention incentives and improved company culture.",
            "maintain": "Continue your strong employee retention. Consider employee development programs and recognition initiatives."
        },
        "Business Processes": {
            "improve": "Document and automate key business processes. Create standard operating procedures for all critical functions.",
            "maintain": "Continue optimizing business processes. Look for automation opportunities and process improvement initiatives."
        },
        "IT Systems": {
            "improve": "Conduct an IT security audit, upgrade to licensed SaaS platforms, and ensure 99.9%+ uptime and backup plans.",
            "maintain": "Maintain strong IT infrastructure. Consider cloud migration and advanced security measures for continued reliability."
        },
        "Operations Continuity": {
            "improve": "Develop and test business continuity plan to ensure operational continuity in various disruption scenarios.",
            "maintain": "Continue strong operational processes. Regularly test and update business continuity plans."
        },
        "Technology Systems": {
            "improve": "Update systems, obtain licenses, and pursue SOC 2 compliance within 12 months for improved operational efficiency.",
            "maintain": "Continue investing in technology upgrades. Consider advanced automation and integration opportunities."
        },
        "Proprietary Tech": {
            "improve": "Identify and patent proprietary tech, linking it to revenue contributions to increase competitive advantage.",
            "maintain": "Continue protecting and developing proprietary technology. Consider licensing opportunities."
        },
        "Operational Processes": {
            "improve": "Map key processes and implement cost-saving measures to achieve 10-15% efficiency gains through streamlined operations.",
            "maintain": "Continue optimizing operational processes. Look for opportunities to scale and improve efficiency further."
        },
        "Scalability": {
            "improve": "Invest in scalable tools and processes to handle 20-30% demand increase without adding significant costs/investment.",
            "maintain": "Continue building scalable systems. Plan for growth capacity and infrastructure improvements."
        },
        "Supplier Contracts": {
            "improve": "Negotiate multi-year supplier contracts with cost savings and ensure diversified supplier base to reduce risk.",
            "maintain": "Continue managing strong supplier relationships. Consider strategic partnerships and contract optimization."
        },
        "Operating Expenses": {
            "improve": "Conduct an expense audit to identify 10%+ cost savings and implement a cost management plan covering key risks.",
            "maintain": "Continue efficient expense management. Look for opportunities to reinvest savings into growth initiatives."
        },
        "Risk Management": {
            "improve": "Develop a risk management plan covering key risks, reviewed every 6 months with mitigation strategies in place.",
            "maintain": "Continue strong risk management practices. Consider expanding risk assessment to new business areas."
        },
        "Business Resilience": {
            "improve": "Stress-test financials for volatility and build reserves to stabilize revenue during market downturns.",
            "maintain": "Maintain strong business resilience. Continue building reserves and diversifying revenue sources."
        },
        "Legal Contracts": {
            "improve": "Review all contracts with a lawyer to ensure they are current and dispute-free, with proper legal protections in place.",
            "maintain": "Continue maintaining excellent legal compliance. Regular contract reviews and legal updates are recommended."
        }
    }
    
    if metric_name in feedback_map:
        return (feedback_map[metric_name]["improve"], feedback_map[metric_name]["maintain"])
    
    return ("Work on improving this area to increase business transferability.", "Continue your strong performance in this area.")


def get_personal_question(metric_name: str) -> str:
    """Get the full question text for personal readiness metrics."""
    
    question_map = {
        "Personal Identity": "How clear is your personal identity beyond being a business owner?",
        "Financial Plan": "How secure is your personal financial plan post-sale?",
        "Physical Health": "How strong is your physical health heading into next phase of life?",
        "Energy Level": "How is your level of energy for the sale process?",
        "Estate Plan": "How current is your personal estate plan for post-sale?",
        "Legal Protections": "How clear are your legal protections for sale proceeds?",
        "Future Vision": "How clear is your vision for life after the sale?",
        "Family Communication": "How open are you with family about the sale's impact?",
        "Professional Advisors": "How well do you leverage professional advisors?",
        "Process Confidence": "How confident are you in navigating the process with potential buyers?"
    }
    
    return question_map.get(metric_name, metric_name)


def get_personal_feedback(metric_name: str, score: int) -> tuple:
    """Get both improvement and maintenance feedback for personal readiness metrics."""
    
    feedback_map = {
        "Personal Identity": {
            "improve": "Explore new hobbies or volunteer work to build identity outside the business. Meet with financial advisor to create a post-sale budget and investment plan.",
            "maintain": "Continue developing your personal identity outside the business. Consider mentoring others or expanding personal interests."
        },
        "Financial Plan": {
            "improve": "Meet with financial advisor to create detailed post-sale budget and investment plan covering all personal financial goals.",
            "maintain": "Continue working with your financial advisor. Review and update your financial plan regularly as circumstances change."
        },
        "Physical Health": {
            "improve": "Start a 30-minute daily exercise routine and schedule a comprehensive health checkup to ensure you're prepared for life's next phase.",
            "maintain": "Continue maintaining excellent physical health. Consider preventive care and stress management techniques."
        },
        "Energy Level": {
            "improve": "Establish a consistent sleep schedule and monitor energy levels. Consider lifestyle changes to boost daily energy and vitality.",
            "maintain": "Continue maintaining high energy levels. Consider stress management and work-life balance optimization."
        },
        "Estate Plan": {
            "improve": "Hire an estate planning lawyer to draft or update your estate plan within 3 months, including will, trusts, and tax planning.",
            "maintain": "Continue maintaining your estate plan. Review and update it regularly, especially after major life changes."
        },
        "Legal Protections": {
            "improve": "Consult a lawyer to set up a trust for sale proceeds protection and ensure all legal structures are properly in place.",
            "maintain": "Continue maintaining strong legal protections. Regular legal reviews ensure continued compliance and protection."
        },
        "Future Vision": {
            "improve": "Write a 1-year post-sale action plan with 3+ personal goals and create a vision board for your future aspirations.",
            "maintain": "Continue developing your post-sale vision. Consider expanding your goals and exploring new opportunities."
        },
        "Family Communication": {
            "improve": "Schedule a family meeting to discuss sale plans and impacts. Ensure all family members understand and support the transition.",
            "maintain": "Continue maintaining excellent family communication. Regular family meetings help ensure continued alignment."
        },
        "Professional Advisors": {
            "improve": "Hire a business broker and schedule monthly advisor meetings with CPA, lawyer, and broker to ensure proper guidance.",
            "maintain": "Continue working with your professional advisor team. Consider expanding your network for additional expertise."
        },
        "Process Confidence": {
            "improve": "Take a course to familiarize yourself with the sale process, or start negotiating with an experienced business broker for guidance.",
            "maintain": "Continue building confidence in the sale process. Stay informed about market conditions and sale strategies."
        }
    }
    
    if metric_name in feedback_map:
        return (feedback_map[metric_name]["improve"], feedback_map[metric_name]["maintain"])
    
    return ("Focus on improving your preparation in this personal area.", "Continue your strong preparation in this personal area.")


def generate_html_report(data: Dict[str, Any]) -> str:
    """Generate HTML content for the PDF report."""
    
    # Extract data sections
    bg_data = data.get('assessment_data', {}).get('business_goals_and_financials', {})
    bp_data = data.get('assessment_data', {}).get('business_performance_and_transferability', {})
    pr_data = data.get('assessment_data', {}).get('personal_readiness_for_business_owners', {})
    calc_data = data.get('assessment_calculations', {})
    
    # Generate report date
    report_date = datetime.utcnow().strftime('%B %d, %Y')
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>3X Assessment Report</title>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <div class="header-logo">
                    <div class="logo-text">MEKA DEAL FLOW</div>
                </div>
                <div class="header-title">
                    <h1>3X Assessment</h1>
                    <div class="title-accent-line"></div>
                </div>
            </div>
        </div>
        
        <div class="company-info">
            <h2>{bg_data.get('company_name', 'N/A')}</h2>
            <p style="color: #666666; margin-bottom: 15px; font-size: 14px;">Report generated on {report_date}</p>
            <div class="info-grid">
                <div class="info-item">
                    <strong>Owner</strong>
                    {data.get('first_name', '')} {data.get('last_name', '')}
                </div>
                <div class="info-item">
                    <strong>Industry</strong>
                    {bg_data.get('company_industry', 'N/A')}
                </div>
                <div class="info-item">
                    <strong>Email</strong>
                    {data.get('email', 'N/A')}
                </div>
                <div class="info-item">
                    <strong>Phone</strong>
                    {data.get('phone_number', 'N/A')}
                </div>
                <div class="info-item">
                    <strong>Employees</strong>
                    {format_number(bg_data.get('number_of_employees', 0))}
                </div>
                <div class="info-item">
                    <strong>Exit Timeline</strong>
                    {bg_data.get('planned_exit_timeline', 'N/A')}
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Executive Summary</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <h4>Company Transferability Score</h4>
                    <div class="metric-value">{format_percentage(calc_data.get('company_transferability_score', 0))}</div>
                    <div class="metric-label">Overall business readiness for transfer</div>
                </div>"""
    
    # Only show personal readiness score if personal readiness data exists
    if pr_data:
        html_content += f"""
                <div class="metric-card">
                    <h4>Personal Readiness Score</h4>
                    <div class="metric-value">{format_percentage(calc_data.get('personal_readiness_score', 0))}</div>
                    <div class="metric-label">Owner readiness for business exit</div>
                </div>"""
    
    html_content += f"""
                <div class="metric-card">
                    <h4>Estimated Business Value</h4>
                    <div class="metric-value">{format_currency(calc_data.get('current_value_information_provided', 0))}</div>
                    <div class="metric-label">Based on provided information</div>
                </div>
                <div class="metric-card">
                    <h4>Value Range (High)</h4>
                    <div class="metric-value">{format_currency(calc_data.get('range_of_value_high', 0))}</div>
                    <div class="metric-label">Optimistic valuation potential</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Financial Performance</h2>
            <div class="metrics-grid" style="grid-template-columns: repeat(3, 1fr);">
                <div class="metric-card">
                    <h4>Last Year Revenue</h4>
                    <div class="metric-value">{format_currency(bg_data.get('last_year_revenue', 0))}</div>
                    <div class="metric-label">Previous year performance</div>
                </div>
                <div class="metric-card">
                    <h4>Current Year Revenue (Est.)</h4>
                    <div class="metric-value">{format_currency(bg_data.get('current_year_estimated_revenue', 0))}</div>
                    <div class="metric-label">Projected current year</div>
                </div>
                <div class="metric-card">
                    <h4>Last Year Profit</h4>
                    <div class="metric-value">{format_currency(bg_data.get('last_year_profit', 0))}</div>
                    <div class="metric-label">Net profit achieved</div>
                </div>
            </div>
            <div class="metrics-grid" style="grid-template-columns: repeat(3, 1fr); margin-top: 20px;">
                <div class="metric-card">
                    <h4>Current Year Profit (Est.)</h4>
                    <div class="metric-value">{format_currency(bg_data.get('current_year_estimated_profit', 0))}</div>
                    <div class="metric-label">Projected current year profit</div>
                </div>
                <div class="metric-card">
                    <h4>Years in Business</h4>
                    <div class="metric-value">{bg_data.get('years_in_business', 'N/A')}</div>
                    <div class="metric-label">Business experience</div>
                </div>
                <div class="metric-card">
                    <h4>Number of Employees</h4>
                    <div class="metric-value">{format_number(bg_data.get('number_of_employees', 0))}</div>
                    <div class="metric-label">Current workforce size</div>
                </div>
            </div>
            
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Financial Metric</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Current Business Value (Self-Reported)</td>
                        <td>{format_currency(bg_data.get('current_business_value', 0))}</td>
                    </tr>
                    <tr>
                        <td>Target Sale Price</td>
                        <td>{format_currency(bg_data.get('target_sale_price', 0))}</td>
                    </tr>
                    <tr>
                        <td>Revenue per Employee</td>
                        <td>{format_currency(calc_data.get('revenue_per_employee', 0))}</td>
                    </tr>
                    <tr>
                        <td>Two-Year Average Revenue</td>
                        <td>{format_currency(calc_data.get('two_year_average_revenue', 0))}</td>
                    </tr>
                    <tr>
                        <td>Two-Year Average Profit</td>
                        <td>{format_currency(calc_data.get('two_year_average_profit', 0))}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <div class="page-break"></div>
        
        <div class="section">
            <h2>Industry Analysis & Valuation</h2>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                        <th>Industry Benchmark</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>EBITDA Multiple</td>
                        <td>{calc_data.get('ebitda_multiple', 0):.1f}x</td>
                        <td>Industry Standard</td>
                    </tr>
                    <tr>
                        <td>EBITDA Margin</td>
                        <td>{format_percentage(calc_data.get('ebitda_margin', 0))}</td>
                        <td>Industry Average</td>
                    </tr>
                    <tr>
                        <td>Last Year Profit Margin</td>
                        <td>{format_percentage(calc_data.get('last_year_profit_percentage', 0) * 100)}</td>
                        <td>Company Performance</td>
                    </tr>
                    <tr>
                        <td>Current Year Profit Margin (Est.)</td>
                        <td>{format_percentage(calc_data.get('current_year_profit_percentage', 0) * 100)}</td>
                        <td>Company Performance</td>
                    </tr>
                </tbody>
            </table>
            
            <h3>Valuation Range</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Valuation Method</th>
                        <th>Amount</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Conservative Value (Low)</td>
                        <td>{format_currency(calc_data.get('range_of_value_low', 0))}</td>
                    </tr>
                    <tr>
                        <td>Current Value (Based on Data)</td>
                        <td>{format_currency(calc_data.get('current_value_information_provided', 0))}</td>
                    </tr>
                    <tr>
                        <td>Optimistic Value (High)</td>
                        <td>{format_currency(calc_data.get('range_of_value_high', 0))}</td>
                    </tr>
                    <tr style="background: #f0fff4;">
                        <td><strong>Value Opportunity</strong></td>
                        <td><strong>{format_currency(calc_data.get('exit_planning_value_opportunity', 0))}</strong></td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <div class="page-break"></div>
        
        <div class="section">
            <h2>Business Performance & Transferability Assessment</h2>
            <div class="score-summary">
                <h3>Overall Score</h3>
                <div class="percentage">{format_percentage(calc_data.get('company_transferability_score', 0))}</div>
            </div>
    """
    
    # Organize business performance metrics by score ranges
    all_bp_metrics = [
        ('Financial Statements', bp_data.get('financial_statements', 0)),
        ('Profitability', bp_data.get('profitability', 0)),
        ('Operating Expenses', bp_data.get('operating_expenses', 0)),
        ('Customer Base', bp_data.get('customer_base', 0)),
        ('Customer Relationships', bp_data.get('customer_relationships', 0)),
        ('Sales Growth', bp_data.get('sales_growth', 0)),
        ('Brand Value', bp_data.get('brand_value', 0)),
        ('Marketing', bp_data.get('marketing', 0)),
        ('Market Position', bp_data.get('market_position', 0)),
        ('Management Capability', bp_data.get('management_capability', 0)),
        ('Leadership Roles', bp_data.get('leadership_roles', 0)),
        ('Succession Planning', bp_data.get('succession_planning', 0)),
        ('Employee Turnover', bp_data.get('employee_turnover', 0)),
        ('Business Processes', bp_data.get('business_processes', 0)),
        ('IT Systems', bp_data.get('it_systems', 0)),
        ('Operations Continuity', bp_data.get('operations_continuity', 0)),
        ('Technology Systems', bp_data.get('technology_systems', 0)),
        ('Proprietary Tech', bp_data.get('proprietary_tech', 0)),
        ('Operational Processes', bp_data.get('operational_processes', 0)),
        ('Scalability', bp_data.get('scalability', 0)),
        ('Risk Management', bp_data.get('risk_management', 0)),
        ('Business Resilience', bp_data.get('business_resilience', 0)),
        ('Legal Contracts', bp_data.get('legal_contracts', 0)),
        ('Supplier Contracts', bp_data.get('supplier_contracts', 0)),
        ('Growth Strategy', bp_data.get('growth_strategy', 0)),
        ('Revenue Streams', bp_data.get('revenue_streams', 0)),
    ]
    
    # Separate into improvement needed vs performing well
    needs_improvement = [(name, score) for name, score in all_bp_metrics if score <= 3]
    performing_well = [(name, score) for name, score in all_bp_metrics if score >= 4]
    
    # Sort each group by score
    needs_improvement.sort(key=lambda x: x[1])
    performing_well.sort(key=lambda x: x[1], reverse=True)
    
    # Areas that need improvement (Scores 1-3)
    if needs_improvement:
        html_content += '''
            <div style="background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);">
                <h3 style="color: #000000; margin: 0 0 15px 0;">🔴 Areas That Need Improvement (Scores 1-3)</h3>
                <p style="margin: 0 0 15px 0; color: #666666;">These areas require immediate attention to increase your business transferability and exit readiness.</p>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Business Areas Requiring Immediate Attention</th>
                        </tr>
                    </thead>
                    <tbody>
        '''
        
        for metric_name, score in needs_improvement:
            question = get_business_question(metric_name)
            improve_feedback, _ = get_business_feedback(metric_name, score)
            score_class = get_score_class(score)
            
            html_content += f'''
                <tr>
                    <td style="border-bottom: 2px solid #f0f0f0; padding: 15px;">
                        <h4 style="margin: 0 0 8px 0; color: #000000; font-size: 14px;">{question}</h4>
                        <div style="color: #666666; font-size: 13px; margin-bottom: 12px;">
                            <strong>Your Score: <span class="score {score_class}">{score}/6</span></strong>
                        </div>
                        <div style="padding: 10px; background: #ffffff; border-left: 3px solid #007bff; border-radius: 4px; border: 1px solid #e0e0e0;">
                            <strong style="color: #000000; font-size: 12px;">🔧 IMPROVEMENTS TO CONSIDER:</strong><br>
                            <span style="font-size: 11px; color: #666666;">{improve_feedback}</span>
                        </div>
                    </td>
                </tr>
            '''
        
        html_content += '''
                    </tbody>
                </table>
            </div>
        '''
    
    # Areas performing well (Scores 4-6)
    if performing_well:
        html_content += '''
            <div style="background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);">
                <h3 style="color: #000000; margin: 0 0 15px 0;">🟢 Areas Performing Well (Scores 4-6)</h3>
                <p style="margin: 0 0 15px 0; color: #666666;">These areas are performing well. Here are ways to continue improving them further.</p>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Business Areas Performing Well - Continue Improving</th>
                        </tr>
                    </thead>
                    <tbody>
        '''
        
        for metric_name, score in performing_well:
            question = get_business_question(metric_name)
            improve_feedback, _ = get_business_feedback(metric_name, score)
            score_class = get_score_class(score)
            
            html_content += f'''
                <tr>
                    <td style="border-bottom: 2px solid #f0f0f0; padding: 15px;">
                        <h4 style="margin: 0 0 8px 0; color: #000000; font-size: 14px;">{question}</h4>
                        <div style="color: #666666; font-size: 13px; margin-bottom: 12px;">
                            <strong>Your Score: <span class="score {score_class}">{score}/6</span></strong>
                        </div>
                        <div style="padding: 10px; background: #ffffff; border-left: 3px solid #007bff; border-radius: 4px; border: 1px solid #e0e0e0;">
                            <strong style="color: #000000; font-size: 12px;">🔧 HOW TO STAY ON TRACK:</strong><br>
                            <span style="font-size: 11px; color: #666666;">{improve_feedback}</span>
                        </div>
                    </td>
                </tr>
            '''
        
        html_content += '''
                    </tbody>
                </table>
            </div>
        '''
    
    # Personal Readiness Section
    html_content += f"""
                </tbody>
            </table>
        </div>
    """
    
    # Organize personal readiness metrics by score ranges (only include provided fields)
    all_pr_metrics = []
    pr_field_mapping = {
        'personal_identity': 'Personal Identity',
        'physical_health': 'Physical Health',
        'financial_plan': 'Financial Plan',
        'family_communication': 'Family Communication',
        'future_vision': 'Future Vision',
        'professional_advisors': 'Professional Advisors',
        'estate_plan': 'Estate Plan',
        'energy_level': 'Energy Level',
        'process_confidence': 'Process Confidence',
        'legal_protections': 'Legal Protections'
    }
    
    # Only include fields that are actually provided in the data
    for field_name, display_name in pr_field_mapping.items():
        if field_name in pr_data:
            score = pr_data[field_name]
            all_pr_metrics.append((display_name, score))
    
    # Only show personal readiness section if there are personal readiness metrics provided
    if all_pr_metrics:
        html_content += f"""
        
        <div class="page-break"></div>
        
        <div class="section">
            <h2>Personal Readiness Assessment</h2>
            <div class="score-summary">
                <h3>Overall Score</h3>
                <div class="percentage">{format_percentage(calc_data.get('personal_readiness_score', 0))}</div>
            </div>
        """
        
        # Separate into improvement needed vs performing well
        pr_needs_improvement = [(name, score) for name, score in all_pr_metrics if score <= 3]
        pr_performing_well = [(name, score) for name, score in all_pr_metrics if score >= 4]
        
        # Sort each group by score
        pr_needs_improvement.sort(key=lambda x: x[1])
        pr_performing_well.sort(key=lambda x: x[1], reverse=True)
    
        # Personal areas that need improvement (Scores 1-3)
        if pr_needs_improvement:
            html_content += '''
                <div style="background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);">
                    <h3 style="color: #000000; margin: 0 0 15px 0;">🔴 Personal Areas That Need Improvement (Scores 1-3)</h3>
                    <p style="margin: 0 0 15px 0; color: #666666;">These personal areas require attention to improve your readiness for a successful business exit.</p>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Personal Areas Requiring Attention</th>
                            </tr>
                        </thead>
                        <tbody>
            '''
            
            for metric_name, score in pr_needs_improvement:
                question = get_personal_question(metric_name)
                improve_feedback, _ = get_personal_feedback(metric_name, score)
                score_class = get_score_class(score)
                
                html_content += f'''
                    <tr>
                        <td style="border-bottom: 2px solid #f0f0f0; padding: 15px;">
                            <h4 style="margin: 0 0 8px 0; color: #000000; font-size: 14px;">{question}</h4>
                            <div style="color: #666666; font-size: 13px; margin-bottom: 12px;">
                                <strong>Your Score: <span class="score {score_class}">{score}/6</span></strong>
                            </div>
                            <div style="padding: 10px; background: #ffffff; border-left: 3px solid #007bff; border-radius: 4px; border: 1px solid #e0e0e0;">
                                <strong style="color: #000000; font-size: 12px;">🔧 IMPROVEMENTS TO CONSIDER:</strong><br>
                                <span style="font-size: 11px; color: #666666;">{improve_feedback}</span>
                            </div>
                        </td>
                    </tr>
                '''
            
            html_content += '''
                        </tbody>
                    </table>
                </div>
            '''
        
        # Personal areas performing well (Scores 4-6)
        if pr_performing_well:
            html_content += '''
                <div style="background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);">
                    <h3 style="color: #000000; margin: 0 0 15px 0;">🟢 Personal Areas Performing Well (Scores 4-6)</h3>
                    <p style="margin: 0 0 15px 0; color: #666666;">These personal areas are performing well. Here are ways to continue improving them further.</p>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Personal Areas Performing Well - Continue Improving</th>
                            </tr>
                        </thead>
                        <tbody>
            '''
            
            for metric_name, score in pr_performing_well:
                question = get_personal_question(metric_name)
                improve_feedback, _ = get_personal_feedback(metric_name, score)
                score_class = get_score_class(score)
                
                html_content += f'''
                    <tr>
                        <td style="border-bottom: 2px solid #f0f0f0; padding: 15px;">
                            <h4 style="margin: 0 0 8px 0; color: #000000; font-size: 14px;">{question}</h4>
                            <div style="color: #666666; font-size: 13px; margin-bottom: 12px;">
                                <strong>Your Score: <span class="score {score_class}">{score}/6</span></strong>
                            </div>
                            <div style="padding: 10px; background: #ffffff; border-left: 3px solid #007bff; border-radius: 4px; border: 1px solid #e0e0e0;">
                                <strong style="color: #000000; font-size: 12px;">🔧 IMPROVEMENTS TO CONSIDER:</strong><br>
                                <span style="font-size: 11px; color: #666666;">{improve_feedback}</span>
                            </div>
                        </td>
                    </tr>
                '''
            
            html_content += '''
                        </tbody>
                    </table>
                </div>
            '''
        
        # Close the personal readiness section
        html_content += "</div>"
    
    # Business readiness info
    html_content += f"""
            <h3 style="color: #000000; margin-top: 30px;">Business Goals & Exit Planning</h3>
            <div style="background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; margin: 20px 0;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div style="background: #ffffff; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0;">
                        <h4 style="margin: 0 0 10px 0; color: #000000; font-size: 14px;">🎯 Exit Timeline</h4>
                        <p style="margin: 0; color: #666666; font-size: 13px;"><strong>Planned Exit:</strong> {bg_data.get('planned_exit_timeline', 'N/A')}</p>
                        <p style="margin: 5px 0 0 0; color: #666666; font-size: 12px;">When you plan to exit your business</p>
                    </div>
                    <div style="background: #ffffff; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0;">
                        <h4 style="margin: 0 0 10px 0; color: #000000; font-size: 14px;">💼 Business Readiness</h4>
                        <p style="margin: 0; color: #666666; font-size: 13px;"><strong>Current State:</strong> {bg_data.get('business_readiness', 'N/A')}</p>
                        <p style="margin: 5px 0 0 0; color: #666666; font-size: 12px;">How the business would function without you</p>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div style="background: #ffffff; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0;">
                        <h4 style="margin: 0 0 10px 0; color: #000000; font-size: 14px;">🤝 Offer Acceptance</h4>
                        <p style="margin: 0; color: #666666; font-size: 13px;"><strong>Would Accept Offer:</strong> {bg_data.get('would_accept_offer', 'N/A').title()}</p>
                        <p style="margin: 5px 0 0 0; color: #666666; font-size: 12px;">Your willingness to accept a purchase offer</p>
                    </div>
                    <div style="background: #ffffff; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0;">
                        <h4 style="margin: 0 0 10px 0; color: #000000; font-size: 14px;">💰 Target Price</h4>
                        <p style="margin: 0; color: #666666; font-size: 13px;"><strong>Target Sale Price:</strong> {format_currency(bg_data.get('target_sale_price', 0))}</p>
                        <p style="margin: 5px 0 0 0; color: #666666; font-size: 12px;">Your desired sale price for the business</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="page-break"></div>
        
        <div class="section">
            <h2>Next Steps & Action Plan</h2>
            <div style="background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; margin: 20px 0;">
                <h3 style="color: #000000; margin: 0 0 15px 0;">🎯 Recommended Actions Based on Your Scores</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div style="background: #ffffff; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0;">
                        <h4 style="margin: 0 0 10px 0; color: #000000; font-size: 14px;">🏢 Business Transferability Focus</h4>
                        <p style="margin: 0; color: #666666; font-size: 13px;"><strong>Your Score:</strong> {format_percentage(calc_data.get('company_transferability_score', 0))}</p>
                        <p style="margin: 10px 0 0 0; color: #666666; font-size: 12px;">
                            {'🟢 Excellent! Your business shows strong transferability. Focus on maintaining and optimizing your current strengths.' if calc_data.get('company_transferability_score', 0) >= 75 else 
                             '🟡 Good progress! Focus on the improvement areas identified above to increase your business value.' if calc_data.get('company_transferability_score', 0) >= 50 else 
                             '🔴 Significant work needed. Prioritize the critical improvement areas to make your business more transferable.'}
                        </p>
                    </div>
                    <div style="background: #ffffff; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0;">
                        <h4 style="margin: 0 0 10px 0; color: #000000; font-size: 14px;">👤 Personal Readiness Focus</h4>
                        <p style="margin: 0; color: #666666; font-size: 13px;"><strong>Your Score:</strong> {format_percentage(calc_data.get('personal_readiness_score', 0))}</p>
                        <p style="margin: 10px 0 0 0; color: #666666; font-size: 12px;">
                            {'🟢 Excellent! You are personally ready for a successful exit. Continue your preparation.' if calc_data.get('personal_readiness_score', 0) >= 75 else 
                             '🟡 Good preparation! Address the personal areas above to feel fully confident about your exit.' if calc_data.get('personal_readiness_score', 0) >= 50 else 
                             '🔴 Important personal work needed. Focus on the improvement areas to ensure a successful transition.'}
                        </p>
                    </div>
                </div>
                <div style="background: #ffffff; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0; border-left: 4px solid #007bff;">
                    <h4 style="margin: 0 0 10px 0; color: #000000; font-size: 14px;">📋 Priority Actions</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #666666; font-size: 12px;">
                        <li>Review all items marked as "needs improvement" above</li>
                        <li>Create a timeline for addressing critical gaps</li>
                        <li>Consider working with professional advisors for complex areas</li>
                        <li>Schedule regular reviews to track progress</li>
                        <li>Focus on the highest-impact improvements first</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="page-break"></div>
        
        <div class="charts-section">
            <h2>Assessment Analytics</h2>
            <div class="charts-grid">
                <div class="chart-container">
                    <h3>Score Comparison</h3>
                    <img src="data:image/png;base64,{create_bar_chart(data)}" alt="Assessment Scores Bar Chart">
                </div>
                <div class="chart-container">
                    <h3>Performance Distribution</h3>
                    <img src="data:image/png;base64,{create_bell_curve_chart(data)}" alt="Score Distribution Bell Curve">
                </div>
            </div>
        </div>
        
        <div class="timestamp">
            Report generated on {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}
        </div>
    </body>
    </html>
    """
    
    return html_content


def add_assessment_sections_reportlab(story, assessment_data, styles, heading_style, subheading_style):
    """
    Add assessment sections to the ReportLab story.
    
    Args:
        story: ReportLab story list
        assessment_data: Assessment data dictionary
        styles: ReportLab styles
        heading_style: Custom heading style
        subheading_style: Custom subheading style
    """
    # Business Goals and Financials
    bg_data = assessment_data.get('business_goals_and_financials', {})
    if bg_data:
        story.append(Paragraph("Business Information", heading_style))
        
        # Create table data for business info
        business_info = [
            ['Field', 'Value'],
            ['Company Name', bg_data.get('company_name', 'N/A')],
            ['Industry', bg_data.get('company_industry', 'N/A')],
            ['Years in Business', str(bg_data.get('years_in_business', 'N/A'))],
            ['Last Year Revenue', format_currency(bg_data.get('last_year_revenue', 0))],
            ['Last Year Profit', format_currency(bg_data.get('last_year_profit', 0))],
            ['Business Readiness', bg_data.get('business_readiness', 'N/A')],
            ['Would Accept Offer', bg_data.get('would_accept_offer', 'N/A').title()],
        ]
        
        # Create table
        table = Table(business_info, colWidths=[2.5*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
    
    # Company Transferability Assessment
    ct_data = assessment_data.get('company_transferability', {})
    if ct_data:
        story.append(Paragraph("Company Transferability Assessment", heading_style))
        
        # Create table for assessment metrics
        metrics_data = [['Metric', 'Score', 'Question']]
        
        for field_name, score in ct_data.items():
            if isinstance(score, (int, float)) and field_name != 'overall_score':
                question = get_business_question(field_name)
                metrics_data.append([field_name.replace('_', ' ').title(), f"{score}/6", question])
        
        if len(metrics_data) > 1:  # If we have data beyond the header
            metrics_table = Table(metrics_data, colWidths=[2*inch, 1*inch, 3*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            story.append(metrics_table)
            story.append(Spacer(1, 20))
    
    # Personal Readiness Assessment
    pr_data = assessment_data.get('personal_readiness', {})
    if pr_data:
        story.append(Paragraph("Personal Readiness Assessment", heading_style))
        
        # Create table for personal readiness metrics
        pr_metrics_data = [['Metric', 'Score', 'Question']]
        
        for field_name, score in pr_data.items():
            if isinstance(score, (int, float)) and field_name != 'overall_score':
                question = get_personal_question(field_name)
                pr_metrics_data.append([field_name.replace('_', ' ').title(), f"{score}/6", question])
        
        if len(pr_metrics_data) > 1:  # If we have data beyond the header
            pr_metrics_table = Table(pr_metrics_data, colWidths=[2*inch, 1*inch, 3*inch])
            pr_metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            story.append(pr_metrics_table)
            story.append(Spacer(1, 20))


def generate_pdf_report(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a professional PDF report from the assessment data using ReportLab.
    
    Args:
        data: Complete assessment data with calculations
        
    Returns:
        Dict with PDF file information and status
    """
    try:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        # Get company name for filename if available
        company_name = data.get('assessment_data', {}).get('business_goals_and_financials', {}).get('company_name', 'Assessment')
        # Clean company name for filename
        safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"assessment_report_{safe_company_name}_{timestamp}.pdf"
        
        temp_file_path = f"/tmp/{filename}"
        
        # Create PDF document
        doc = SimpleDocTemplate(temp_file_path, pagesize=A4, 
                              leftMargin=0.75*inch, rightMargin=0.75*inch,
                              topMargin=1*inch, bottomMargin=1*inch)
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Create custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.black
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.black
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=15,
            textColor=colors.black
        )
        
        # Build PDF content
        story = []
        
        # Add title page
        story.append(Paragraph("MEKA Business Assessment Report", title_style))
        story.append(Spacer(1, 20))
        
        # Add organization info
        if 'organization' in data:
            story.append(Paragraph(f"<b>Organization:</b> {data['organization']}", styles['Normal']))
        
        if 'first_name' in data and 'last_name' in data:
            story.append(Paragraph(f"<b>Contact:</b> {data['first_name']} {data['last_name']}", styles['Normal']))
        
        if 'email' in data:
            story.append(Paragraph(f"<b>Email:</b> {data['email']}", styles['Normal']))
        
        # Add timestamp
        story.append(Paragraph(f"<b>Generated:</b> {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}", styles['Normal']))
        story.append(Spacer(1, 40))
        
        # Add executive summary
        calc_data = data.get('assessment_calculations', {})
        business_score = calc_data.get('company_transferability_score', 0)
        personal_score = calc_data.get('personal_readiness_score', 0)
        
        story.append(Paragraph("Executive Summary", heading_style))
        story.append(Paragraph(f"<b>Business Transferability Score:</b> {business_score:.1f}%", styles['Normal']))
        story.append(Paragraph(f"<b>Personal Readiness Score:</b> {personal_score:.1f}%", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Add assessment sections
        if 'assessment_data' in data:
            add_assessment_sections_reportlab(story, data['assessment_data'], styles, heading_style, subheading_style)
        
        # Add charts
        story.append(PageBreak())
        story.append(Paragraph("Assessment Analytics", heading_style))
        
        # Add bar chart
        try:
            chart_data = create_bar_chart(data)
            chart_image = Image(BytesIO(base64.b64decode(chart_data)), width=6*inch, height=4*inch)
            story.append(chart_image)
            story.append(Spacer(1, 20))
        except Exception as e:
            story.append(Paragraph(f"Chart generation error: {str(e)}", styles['Normal']))
        
        # Add bell curve chart
        try:
            curve_data = create_bell_curve_chart(data)
            curve_image = Image(BytesIO(base64.b64decode(curve_data)), width=6*inch, height=4*inch)
            story.append(curve_image)
        except Exception as e:
            story.append(Paragraph(f"Distribution chart error: {str(e)}", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        # Get file size
        file_size = os.path.getsize(temp_file_path)
        
        result = {
            'filename': filename,
            'file_path': temp_file_path,
            'file_size': file_size,
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