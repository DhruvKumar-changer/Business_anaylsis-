#Integrate the LLM Agent for resposes 
import os 
from groq import Groq
from dotenv import load_dotenv

class LLMAgent:
    def __init__(self):
        load_dotenv()
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"),)

    def generate_recommendations(self , kpis):
        business_info = f"""
        BUSINESS KPI SUMMARY     

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
        You are an highly expert business performance analyst and startup mentor.

        Analyze the following KPI data and create a detailed, structured business performance report.

        **Instructions:**
        1. Output strictly in **JSON format**.
        2. Use **simple, friendly language** (no jargon).
        3. Structure the report as follows:

        {
        "metrics_analysis": {
            "metric_name": {
            "value": number,
            "status": "Good / Average / Poor",
            "meaning": "Short simple explanation of this metric",
            "reason": "Why it is in this condition",
            "proof": "Data-based justification (like trends, ratios, etc.)",
            "suggestion": "How to improve or maintain this metric"
            },
            ...
        },

        "summary": {
            "business_health": "Brief summary of how the business is performing overall",
            "key_strengths": ["List of top performing areas"],
            "key_weaknesses": ["List of weak areas that need attention"]
        },

        "alerts": {
            "financial_alerts": ["Any major cost, loss or declining trend warnings"],
            "growth_alerts": ["Any risk to future scalability or market share"]
        },

        "what_is_going_well": {
            "positive_trends": ["Metrics or patterns that show success"],
            "recommend_to_continue": ["Practices that should be continued or scaled"]
        },

        "future_advice": {
            "short_term": ["Immediate next 3 months actions"],
            "long_term": ["6-12 month business strategy improvements"]
        },

        "conclusion": {
            "final_assessment": "1 paragraph summarizing the overall condition, growth stage, and future readiness of the business",
            "confidence_score": "0-100 (how healthy the business seems overall)"
        }
        }

        4. Use the KPI values below to generate your analysis:
        {business_info}

        Make the report extremely insightful, actionable, and easy to read.
        If something looks dangerous or risky, mention it clearly in the alerts section.
        Ensure the response is strictly valid JSON — no explanations, no markdown.

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
