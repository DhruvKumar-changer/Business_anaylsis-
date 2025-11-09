# Entry-level questions for business onboarding

class BusinessQuestions:
    """
    Handles entry-level business questions before analysis
    """
    
    @staticmethod
    def get_questions():
        """
        Returns a structured list of questions to ask users
        
        Returns:
            dict: Questions categorized by type
        """
        return {
            "basic_info": [
                {
                    "id": "q1",
                    "question": "What is your business name?",
                    "field": "business_name",
                    "type": "text",
                    "required": True,
                    "placeholder": "e.g., Sharma Electronics"
                },
                {
                    "id": "q2",
                    "question": "Which industry does your business belong to?",
                    "field": "industry",
                    "type": "select",
                    "required": True,
                    "options": [
                        "E-commerce",
                        "Retail",
                        "SaaS/Software",
                        "Manufacturing",
                        "Services",
                        "Food & Beverage",
                        "Healthcare",
                        "Education",
                        "Real Estate",
                        "Other"
                    ]
                },
                {
                    "id": "q3",
                    "question": "What type of business is this?",
                    "field": "business_type",
                    "type": "select",
                    "required": True,
                    "options": [
                        "Startup (0-2 years)",
                        "Growing Business (2-5 years)",
                        "Established Business (5+ years)"
                    ]
                }
            ],
            
            "financial_goals": [
                {
                    "id": "q4",
                    "question": "What is your primary goal?",
                    "field": "primary_goal",
                    "type": "select",
                    "required": True,
                    "options": [
                        "Increase Revenue",
                        "Reduce Costs",
                        "Improve Profit Margins",
                        "Prepare for Funding/IPO",
                        "Scale Operations",
                        "General Health Check"
                    ]
                },
                {
                    "id": "q5",
                    "question": "Are you looking for external funding?",
                    "field": "seeking_funding",
                    "type": "select",
                    "required": True,
                    "options": [
                        "Yes - Angel/Seed Round",
                        "Yes - Series A/B",
                        "Yes - IPO Preparation",
                        "No - Self-funded"
                    ]
                }
            ],
            
            "operational_details": [
                {
                    "id": "q6",
                    "question": "How many products/services do you offer?",
                    "field": "product_count",
                    "type": "number",
                    "required": False,
                    "placeholder": "e.g., 10"
                },
                {
                    "id": "q7",
                    "question": "What is your current monthly revenue (approximate)?",
                    "field": "monthly_revenue",
                    "type": "select",
                    "required": False,
                    "options": [
                        "Less than ₹1 Lakh",
                        "₹1-5 Lakhs",
                        "₹5-10 Lakhs",
                        "₹10-50 Lakhs",
                        "₹50 Lakhs - 1 Crore",
                        "More than ₹1 Crore"
                    ]
                },
                {
                    "id": "q8",
                    "question": "What are your biggest concerns?",
                    "field": "concerns",
                    "type": "multiselect",
                    "required": False,
                    "options": [
                        "High operational costs",
                        "Low profit margins",
                        "Cash flow problems",
                        "Slow growth",
                        "Market competition",
                        "Customer retention"
                    ]
                }
            ],
            
            "data_upload": [
                {
                    "id": "q9",
                    "question": "Upload your business data (CSV file)",
                    "field": "data_file",
                    "type": "file",
                    "required": True,
                    "accept": ".csv",
                    "help_text": "Upload a CSV file with columns: Date, Product_Name, Revenue, Costs, etc."
                }
            ]
        }
    
    @staticmethod
    def validate_answers(answers):
        """
        Validate user answers
        
        Args:
            answers (dict): User's answers to questions
            
        Returns:
            tuple: (is_valid, error_message)
        """
        required_fields = [
            "business_name",
            "industry",
            "business_type",
            "primary_goal",
            "seeking_funding"
        ]
        
        for field in required_fields:
            if field not in answers or not answers[field]:
                return False, f"Missing required field: {field}"
        
        return True, None
    
    @staticmethod
    def create_business_profile(answers):
        """
        Create a business profile from answers
        
        Args:
            answers (dict): User's answers
            
        Returns:
            dict: Structured business profile
        """
        return {
            "business_name": answers.get("business_name"),
            "industry": answers.get("industry"),
            "business_type": answers.get("business_type"),
            "primary_goal": answers.get("primary_goal"),
            "seeking_funding": answers.get("seeking_funding"),
            "product_count": answers.get("product_count"),
            "monthly_revenue": answers.get("monthly_revenue"),
            "concerns": answers.get("concerns", [])
        }


# ========== USAGE EXAMPLE ==========
if __name__ == "__main__":
    questions = BusinessQuestions.get_questions()
    
    print("=" * 60)
    print("BUSINESS ONBOARDING QUESTIONS")
    print("=" * 60)
    
    for category, qs in questions.items():
        print(f"\n📋 {category.upper().replace('_', ' ')}:")
        for q in qs:
            print(f"   {q['id']}: {q['question']}")
    
    # Example validation
    sample_answers = {
        "business_name": "Tech Startup",
        "industry": "SaaS/Software",
        "business_type": "Startup (0-2 years)",
        "primary_goal": "Prepare for Funding/IPO",
        "seeking_funding": "Yes - Series A/B"
    }
    
    is_valid, error = BusinessQuestions.validate_answers(sample_answers)
    print(f"\n✅ Validation: {is_valid}")
    if error:
        print(f"❌ Error: {error}")
    
    profile = BusinessQuestions.create_business_profile(sample_answers)
    print(f"\n👤 Business Profile Created:")
    for key, value in profile.items():
        print(f"   {key}: {value}")