#Integrate the LLM Agent for resposes 
import os 
from groq import Groq
from dotenv import load_dotenv
import json

class LLMAgent:
    def __init__(self):
        load_dotenv()
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"),)

    # Updated llm_agent.py - generate_recommendations function

    def generate_recommendations(self, kpis, business_profile=None):
        """
        Generate recommendations with business profile context
        
        Args:
            kpis (dict): KPI metrics
            business_profile (dict, optional): Business profile from entry questions
        """
        
        # Build business context if profile provided
        profile_context = ""
        if business_profile:
            profile_context = f"""
            
            📋 BUSINESS PROFILE CONTEXT:
            • Business Name: {business_profile.get('business_name', 'N/A')}
            • Industry: {business_profile.get('industry', 'N/A')}
            • Business Type: {business_profile.get('business_type', 'N/A')}
            • Primary Goal: {business_profile.get('primary_goal', 'N/A')}
            • Seeking Funding: {business_profile.get('seeking_funding', 'N/A')}
            • Monthly Revenue Range: {business_profile.get('monthly_revenue', 'N/A')}
            • Top Concerns: {', '.join(business_profile.get('concerns', []))}
            
            ⚠️ IMPORTANT: Tailor your recommendations based on:
            - Their industry type
            - Their primary goal
            - Their funding needs
            - Their specific concerns
            """
        
        business_info = f"""
        BUSINESS KPI SUMMARY     
        {profile_context}

            # 🧩BASIC METRICS
            • Total Revenue: {kpis['total_revenue']}
            • Total Cost: {kpis['total_cost']}
            • Net Profit: {kpis['net_profit']}
            • Profit Margin: {kpis['profit_margin']}%
            • Gross Profit: {kpis['gross_profit']}

            # 💼 ADVANCED FINANCIALS
            • EBITDA: {kpis['ebitda']}
            • Operating Profit: {kpis['operating_profit']}
            • Burn Rate: {kpis['burn_rate']}
            • Runway (Months): {kpis['runway_months']}
            • Break-even Point: {kpis['break_even_point']}
            • ROI: {kpis['roi']}%
            • Revenue Growth Rate: {kpis['revenue_growth_rate']}%
            • Expense Ratio: {kpis['expense_ratio']}%

            # 🧾 PRODUCT ANALYSIS
            • Best Performing Product: {kpis['best_product']}
            • Worst Performing Product: {kpis['worst_product']}

            # 💰 EXPENSE DETAILS
            • Expense Breakdown: {kpis['expense_breakdown']}
            • Highest Expense Category: {kpis['highest_expense']}

            # 📈 BUSINESS TRENDS
            • Monthly Revenue Trend: {kpis['monthly_revenue']}
            • Monthly Profit Trend: {kpis['monthly_profit']}
            • Growth Trajectory: {kpis['growth_trajectory']}
            • Seasonal Analysis: {kpis['seasonal_analysis']}

            # 💹 INVESTMENT READINESS
            • Scalability Score: {kpis['scalability_score']}
            • Risk Score: {kpis['risk_score']}
            • IPO Readiness: {kpis['ipo_readiness']}
            • Shark Tank Score: {kpis['shark_tank_score']}
            • Expansion Recommendation: {kpis['expansion_recommendation']}

            # 🧠 ADDITIONAL INSIGHTS
            • Customer Acquisition Cost: {kpis['customer_acquisition_cost']}
            • Average Revenue per Booking: {kpis['avg_revenue_per_booking']}
            • Operating Efficiency: {kpis['operating_efficiency']}%
            • Cash Flow Health: {kpis['cash_flow_health']}
            • Market Position: {kpis['market_position']}
            """
        
        #LLM prompt that guide it 
        prompt = f"""
        You are an elite startup advisor, financial analyst, and business strategist with deep expertise in reading business KPIs and identifying strategic actions.

        Your job: Generate an extremely detailed, realistic, and data-backed business report using the KPI data and business profile below.

        ⚙️ OUTPUT FORMAT — STRICTLY JSON ONLY (no markdown, no extra text):

        {{
        "executive_summary": {{
            "overview": "Comprehensive yet concise summary of current business health and trajectory",
            "business_stage": "Which stage this business seems to be in (early, growth, maturity, decline)",
            "confidence_score": "0-100 (based on how financially and operationally strong the business looks)"
        }},

        "metric_diagnostics": {{
            "financial_performance": [
                {{
                    "metric": "Revenue Growth Rate",
                    "value": "{kpis.get('revenue_growth_rate', 0)}",
                    "assessment": "Excellent / Good / Weak / Declining",
                    "analysis": "Explain why it's in this condition based on data trends or ratios",
                    "impact": "Explain how this affects profit, sustainability, or scaling",
                    "improvement_plan": "3-step plan to fix or enhance this metric"
                }},
                ...
            ],
            "operational_efficiency": [
                {{
                    "metric": "Burn Rate",
                    "value": "{kpis.get('burn_rate', 0)}",
                    "assessment": "Sustainable / High / Critical",
                    "analysis": "Explain how the burn rate affects runway and funding needs",
                    "impact": "Impact on cash flow and long-term survival",
                    "recommendation": "Specific strategies to reduce burn rate or improve unit economics"
                }}
            ],
            "market_and_scalability": [
                {{
                    "metric": "Scalability Score",
                    "value": "{kpis.get('scalability_score', 0)}",
                    "analysis": "How ready the business is to scale given operations and margins",
                    "recommendation": "Explain how to prepare for next growth phase"
                }}
            ]
        }},

        "strategic_recommendations": {{
            "short_term_actions": [
                "Precise 3-6 actionable improvements for next quarter (data-driven, realistic)"
            ],
            "mid_term_strategies": [
                "Operational or marketing changes to strengthen growth trajectory"
            ],
            "long_term_plan": [
                "Strategic goals for 12+ months to reach investment-readiness or IPO readiness"
            ]
        }},

        "business_context_analysis": {{
            "profile_summary": "{business_profile if business_profile else 'No profile provided'}",
            "contextual_insights": "Analyze how the business’s goals, funding needs, and concerns affect recommendations.",
            "industry_comparison": "Comment how this business stands vs typical industry performance patterns"
        }},

        "alerts_and_risks": {{
            "financial_alerts": [
                "Major cost or cash flow warnings with quantitative reasons"
            ],
            "growth_alerts": [
                "Risks to market share, expansion, or scaling readiness"
            ],
            "operational_risks": [
                "Any inefficiencies, over-dependencies, or low-performing segments"
            ]
        }},

        "conclusion": {{
            "final_diagnosis": "Holistic narrative combining KPIs + context + strategy readiness",
            "priority_focus_areas": ["Top 3 things to fix or continue immediately"],
            "positive_highlights": ["Metrics or behaviors that indicate strength"]
        }}
        }}

        🧩 DATA INPUTS:
        {business_info}

        📋 CONTEXT (if provided):
        {profile_context}

        ⚠️ CRITICAL RULES:
        - Output must be extremely detailed (at least 10,000 characters total).
        - Every insight should be specific, logical, and backed by metric evidence.
        - Avoid repeating generic lines like “reduce cost” or “increase marketing”.
        - Include interrelations (e.g., “high burn rate despite high growth means scaling too fast”).
        - Always provide a clear reasoning chain (“because X, therefore Y, suggesting Z”).
        - The report should sound like it was written by a consulting firm such as McKinsey or Bain.

        Ensure your output is **valid JSON only**, no markdown or commentary outside JSON.
        """


        #Return the result 
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system" , "content": "You are a highly skilled business analyst."},
                {"role": "user" , "content": prompt}
            ],
            model="llama-3.1-8b-instant"
        )
        return response.choices[0].message.content
