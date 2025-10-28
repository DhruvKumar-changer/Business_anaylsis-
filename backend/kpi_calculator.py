#KPI Metrics calculations

import pandas as pd
import numpy as np 

class KPICalculator:

    def __init__(self,dataframe):
        self.df = dataframe

    #All KPI Functions that plays an important role in the Anylasis
    
    #-------------------------------Basic Metrics--------------------------------------#

    # 1. Total Revenue (Refer: Sum Of Revenue column )
    def calculate_total_revenue(self):
        return self.df['Revenue'].sum()

    # 2. Total Cost (Refer: Sum of all cost columns)
    def calculate_total_cost(self):
        cog = self.df["Costs_Of_Goods"].sum()
        market = self.df["Marketing_Cost"].sum()
        logistic = self.df["Logistic_Cost"].sum()
        other = self.df["Other_Cost"].sum()
        return cog + market + logistic + other
    
    # 3. Net Profit (Refer: Revenue - Total Cost)
    def calculate_net_profit(self):
        sales = self.calculate_total_revenue()
        costs = self.calculate_total_cost()
        return sales - costs

    # 4. Profit Margin % (Refer: (Profit/Revenue) × 100)
    def calculate_profit_margin(self):
        sales = self.calculate_total_revenue()
        profit = self.calculate_net_profit()
        if sales == 0:
            return 0
        return (profit/sales)*100

    # 5. Gross Profit (Refer: Revenue - Direct Costs only)
    def calculate_gross_profit(self):
        sales = self.calculate_total_revenue()
        cog = self.df["Costs_Of_Goods"].sum()
        return sales - cog
    
    #----------------------------ADVANCED FINANCIAL METRICS-------------------------#

    # 6. EBITDA (Refer: Earnings Before Interest, Tax, Depreciation, Amortization)
    # Simplified: Operating Profit (assume no interest/tax in data)
    def calculate_ebitda(self):              #(Earnings Before Interest, Tax, Depreciation, Amortization)
        gross = self.calculate_gross_profit()
        operating = self.df["Costs_Of_Goods"].sum() + self.df["Marketing_Cost"].sum() + self.df["Logistic_Cost"].sum()
        return gross - operating

    # 7. Operating Profit (Refer: Gross Profit - Operating Expenses)
    def calculate_operating_profit(self):      #(Gross Profit - Operating Expenses)
        gross = self.calculate_gross_profit()
        operating = self.df["Operating_Expenses"].sum()
        return gross - operating

    # 8. Monthly Burn Rate (Refer: Average monthly expenses)
    def calculate_burn_rate(self): #(Monthly expenses average)
        total_costs = self.calculate_total_cost()
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        days = (self.df['Date'].max() - self.df['Date'].min()).days
        months = days/30.44 if days >0 else 1
        return round(total_costs/months,2)

    # 9. Runway (Refer: Months company can survive with current cash)
    # Assume current_cash passed separately or use profit as indicator
    def calculate_runway(self, current_cash=50000): #(Months remaining with current cash)
        burn = self.calculate_burn_rate()
        if burn <=0:
            return "Infinite (No Expenses)"
        return round(current_cash/burn , 2)

    # 10. Break-even Point (Refer: Revenue needed where profit = 0)
    def calculate_break_even_point(self): #(When profit = 0)
        total_expenses = self.calculate_total_cost()
        # current expenses of the business is the break-even revenue
        return round (total_expenses , 2)

    # 11. ROI % (Refer: Return on Investment)
    def calculate_roi(self,initial_investment=100000): #(Return on Investment %)
        profit = self.calculate_net_profit()
        return round((profit/initial_investment)*100 , 2)

    # 12. Revenue Growth Rate % (Refer: Month-on-month growth)
    def calculate_revenue_growth_rate(self): #(Month-on-month growth rate %)
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df['Month'] = self.df['Date'].dt.to_period('M')
        monthly = self.df.groupby('Month')['Revenue'].sum()
        if len(monthly) <2:
            return 0 
        first_month = monthly.iloc[0]
        last_month = monthly.iloc[-1]
        growth = ((last_month - first_month)/first_month)*100
        return round(growth,2)

    # 13. Expense Ratio % (Refer: Expenses as % of Revenue)
    def calculate_expense_ratio(self): #(Expenses as the % of Revenue %)
        revenue = self.calculate_total_revenue()
        expenses = self.calculate_total_cost()
        if revenue == 0:
            return 0 
        return round((expenses/revenue)*100,2)

    #--------------------------------PRODUCT ANALYSIS-------------------------------#

    # 14. Room-wise Analysis (Refer: every product type performance)
    def product_wise_analysis(self): #(peroformance of every single product)
        products = {} 
        #initialize  the loop for every  single product 
        for product in self.df["Product_Name"].unique():
            #filter the product
            product_df = self.df[self.df["Product_Name"] == product]
            #revenue of the product
            revenue = product_df['Revenue'].sum()
            #Cost of the product
            cost = (product_df["Costs_Of_Goods"].sum() + product_df["Marketing_Cost"].sum())
            #profit(revenue - cost)
            profit =  revenue - cost
            #store in dictionary
            products[product] = {
                'revenue' : revenue,
                'cost' : cost,
                'profit' : profit
            }
        return products

    #  15. Best Performing product (Refer: Highest profit room type)
    def best_performing_product(self):
        analysis = self.product_wise_analysis()
        #findout the max profit product
        best = max(analysis.items(), key=lambda x:x[1]['profit'])
        return {'product':best[0], 'profit':best[1]['profit']}

    # 16. Worst Performing product (Refer: Lowest/negative profit)
    def worst_performing_product(self): 
        analysis = self.product_wise_analysis()
        #findout the min profit product 
        worst = min(analysis.items(), key= lambda x: x[1] ['profit'])
        return {'product':worst[0], 'profit': worst[1] ['profit']}

    
    # #--------------------------------EXPENSE BREAKDOWN------------------------------#
    
    # 17. Expense Breakdown % (Refer: Each category as % of total)
    def expense_breakdown(self): #(Category-wise expenses)    
        total = self.calculate_total_cost()
        if total == 0 :
            return {}
        return {
        "Costs_Of_Goods" : round((self.df["Costs_Of_Goods"].sum() / total) * 100,2),
        "Marketing_Cost" : round((self.df["Marketing_Cost"].sum() / total) * 100,2),
        "Logistic_Cost " : round((self.df["Logistic_Cost"].sum() / total) * 100,2),
        "Other_Cost"     : round((self.df["Other_Cost"].sum() / total) * 100,2)
        }

    # 18. Highest Expense Category (Refer: Which costs most)
    def highest_expense_category(self): #Which costs most 
        breakdown = self.expense_breakdown()
        if not breakdown:
            return None
        highest = max(breakdown.items(), key= lambda x:x[1])
        return {'category':highest[0], 'percentage':highest[1]}
    
    # #----------------------------------TREND ANALYSIS-------------------------------#
    
    # 19. Monthly Revenue Trend (Refer: Revenue per month)
    def monthly_revenue_trend(self): #revenue per month
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df['Month'] = self.df['Date'].dt.to_period('M')
        monthly = self.df.groupby('Month')["Revenue"].sum()
        return {str(k): round(v, 2) for k, v in monthly.items()}
    
    # 20. Monthly Profit Trend (Refer: Profit per month)
    def monthly_profit_trend(self): #profit per month
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df['Month'] = self.df['Date'].dt.to_period('M')

        monthly_revenue = self.df.groupby('Month')['Revenue'].sum()
        monthly_expenses = self.df.groupby('Month')[
            ["Costs_Of_Goods","Marketing_Cost","Logistic_Cost","Other_Cost"]].sum().sum(axis=1)
        
        monthly_profit = monthly_revenue -monthly_expenses
        return {str(k):round(v,2) for k ,v in monthly_profit.items()}
        
    # 21. Growth Trajectory (Refer: Is business growing or declining?)
    def growth_trajectory(self): #(Increasing/Decreasing) means is business growing or declining?
        trend = self.monthly_revenue_trend()
        #convert the trend values into list
        values = list(trend.values())
        #average of the first half
        first_half = values[:len(values)//2] 
        first_avg = sum(first_half ) / len(first_half)
        #average of the second half
        second_half = values[len(values)//2:] 
        second_avg = sum(second_half ) / len(second_half)
        #logic
        if second_avg > first_avg * 1.1:    #more than the 10%
            return "Strong Growth"
        elif second_avg > first_avg :    
            return "Moderate Growth"
        elif second_avg < first_avg * 0.9:    #less than the 10%
            return "Declining"
        else:
            return "Stable"

    # 22. Seasonal Analysis (Refer: Quarter-wise performance)
    def seasonal_analysis(self): #(Quarter-wise performance)
        self.df["Date"] = pd.to_datetime(self.df['Date'])
        self.df["Quarter"] = self.df["Date"].dt.quarter
        quartly = self.df.groupby("Quarter")['Revenue'].sum()
        return {f'Q{k}': round(v,2) for k,v in quartly.items()}
    
    
    # #--------------------------------INVESTMENT READINESS---------------------------#
    
    # 23. Scalability Score 0-100 (Refer: Can business scale?)
    def calculate_scalability_score(self): #(0-100) means can business scale 
        growth = self.calculate_revenue_growth_rate()
        margin = self.calculate_profit_margin()
        exp_ratio = self.calculate_expense_ratio()
        
        score = 0
        #growth
        if growth >20 : score +=30
        elif growth > 10 : score +=20
        elif growth >0 : score +=10
        #margin
        if margin >20 : score +=30
        elif margin > 10 : score +=20
        elif margin >0 : score +=10
        #expense_ratio 
        if exp_ratio <70 : score += 40
        elif  exp_ratio <85 : score +=25
        else : score+= 10

        return min(score,100)

    # 24. Risk Score 0-100 (Refer: Investment risk - lower is better)
    def calculate_risk_score(self):  #(0-100) means Investment risk - Lower is better 
        margin = self.calculate_profit_margin()
        burn = self.calculate_burn_rate()
        revenue = self.calculate_total_revenue()

        risk = 50 #initial base risk
        #margin
        if margin < 0 : risk += 30 # Loss making
        elif margin < 10 : risk +=15
        else : risk -=10
        #burn 
        if burn > revenue/2 : risk +=20  #High Risk
        #trajectory 
        trajectory = self.growth_trajectory()
        if trajectory == "Declining" : risk+=20
        elif trajectory == "Strong Growth" : risk -=15

        return max(0,min(risk ,100))

    # 25. IPO Readiness 0-100 (Refer: Ready for public offering?)
    def calculate_ipo_readiness(self): #(0-100) means is it ready for the public offering
        #Factors Depends : probability , growth ,scale
        profit = self.calculate_profit_margin()
        revenue =  self.calculate_total_revenue()
        growth = self.calculate_revenue_growth_rate()

        score = 0 
        #on the bases of the profit and revenue
        if profit >0 and revenue > 10000000 : score +=40   #1cr revenue
        if profit >0 and revenue > 5000000 : score +=25   
        elif profit >0 : score +=10 
        #on the basis of the growth 
        if growth > 50 : score +=30
        elif growth  > 25 : score +=20
        elif growth > 10 : score +=10
        #conclusion
        trajectory = self.growth_trajectory()
        if trajectory == "Strong Growth" : score +=30
        elif trajectory == "Moderate Growth" : score +=15

        return min(score,100)

    # 26. Shark Tank Score 0-100 (Refer: Would sharks invest?)
    def calculate_shark_tank_score(self):  #(0-100) means Would sharks invest?
        margin = self.calculate_profit_margin() 
        growth = self.calculate_revenue_growth_rate()
        scalability = self.calculate_scalability_score()
        risk = self.calculate_risk_score()

        score = 0 
        #Profitability 
        if margin >20: score +=25
        elif margin >10 : score +=15
        elif margin >0 : score +=5
        #Growth 
        if growth > 30 : score +=25
        elif growth > 15 : score +=15
        #Scalability
        score += scalability *0.3
        #Low risk bonus
        if risk <40 : score +=20
        
        return min(int(score),100)

    #  27. Expansion Recommendation (Refer: Should expand?)
    def expansion_recommendation(self): #(Yes/No with reasons) means should expand 
        margin = self.calculate_profit_margin() 
        growth = self.calculate_revenue_growth_rate()
        profit = self.calculate_profit_margin()
        risk = self.calculate_risk_score()

        reasons = []
        #less profit
        if profit <=0:
            return {
                'recommendation':'No',
                'reasons': ['Comapany is not profitable yet',
                            'Focus on acheving profitability first']                          
            }
        #good margin
        if margin > 15:
            reasons.append(f'Healty profit margin of {margin}%')
        #nice growth
        if growth > 20 :
            reasons.append(f'Strong revenue growth of {growth}%')
        #low risk
        if risk < 50:
            reasons.append('Low risk profile')
        #trajectory indicator
        trajectory = self.growth_trajectory()
        if trajectory in ['Strong Growth','Moderate Growth']:
            reasons.append(f'{trajectory} trajectory indicates market demand')
        #logic
        if len(reasons) >= 3:
            return {'recommendation':'YES', 'reasons':reasons}
        elif len(reasons) >=1:
            return {'recommendation':'MAYBE', 'reasons':reasons +
                    ['Monitor and work more for 2-3 more quarters for  expandation']}
        else:
            return { 'recommendation':'NO' , 'reasons': ['Improve and focus on the profitability and growth metrics first']}

    #-------------------------------ADDITIONAL METRICS----------------------------#
        
    # 28. Customer Acquisition Cost (CAC) (Refer: Marketing / New Customers)
    def calculate_cac(self):
        marketing = self.df["Marketing_Cost"].sum()
        units_sold = self.df["Units_sold"].sum()
        if units_sold == 0:
            return 0
        return round(marketing/units_sold,2)

     # 29. Average Revenue Per Booking (Refer: Revenue / Total Units_sold)
    def calculate_avg_revenue_per_booking(self):
        revenue = self.calculate_total_revenue()
        units_sold  = self.df["Units_sold"].sum()
        if units_sold == 0 :
            return 0 
        return round(revenue / units_sold, 2)

    # 30. Operating Efficiency Ratio (Refer: Operating Profit / Revenue)
    def calculate_operating_efficiency(self):
        revenue = self.calculate_total_revenue()
        operating_efficiency = self.calculate_operating_profit()
        if revenue == 0:
            return 0
        return round((operating_efficiency/revenue)*100,2)

    # 31. Cash Flow Health (Refer: Positive/Negative/Neutral)
    def cash_flow_health(self):
        profit = self.calculate_net_profit()
        burn = self.calculate_burn_rate()

        if profit > burn *2:
            return "Excellent Flow"
        if profit > burn:
            return "Good"
        if profit > 0 :
            return "Fair"
        else:
            return "Poor - Negative Cash Flow"
        
    # 32. Market Position Indicator (Refer: Based on growth & profitability)
    def market_position_indicator(self):
        growth = self.calculate_revenue_growth_rate()
        margin = self.calculate_profit_margin()

        if growth > 30 and margin > 20:
            return "Market Leader"
        if growth > 15 and margin > 10:
            return "Strong Compititor"
        if growth > 10 and margin > 0:
            return "Growing Player"
        else:
            return "Struggling/Emerging means low position"



    #----------------------------------FINAL MASTER FUNCTION------------------------------#

    # Get ALL KPIs (Refer: Complete report calling all the fucntions)
    def get_all_kpis(self):
        return {
            # Basic
            'total_revenue': self.calculate_total_revenue(),
            'total_cost': self.calculate_total_cost(),
            'net_profit': self.calculate_net_profit(),
            'profit_margin': self.calculate_profit_margin(),
            'gross_profit': self.calculate_gross_profit(),
            
            # Advanced Financial
            'ebitda': self.calculate_ebitda(),
            'operating_profit': self.calculate_operating_profit(),
            'burn_rate': self.calculate_burn_rate(),
            'runway_months': self.calculate_runway(),
            'break_even_point': self.calculate_break_even_point(),
            'roi': self.calculate_roi(),
            'revenue_growth_rate': self.calculate_revenue_growth_rate(),
            'expense_ratio': self.calculate_expense_ratio(),
            
            # Product Analysis
            'product_wise_analysis': self.product_wise_analysis(),
            'best_product': self.best_performing_product(),
            'worst_product': self.worst_performing_product(),
            
            # Expense
            'expense_breakdown': self.expense_breakdown(),
            'highest_expense': self.highest_expense_category(),
            
            # Trends
            'monthly_revenue': self.monthly_revenue_trend(),
            'monthly_profit': self.monthly_profit_trend(),
            'growth_trajectory': self.growth_trajectory(),
            'seasonal_analysis': self.seasonal_analysis(),
            
            # Investment
            'scalability_score': self.calculate_scalability_score(),
            'risk_score': self.calculate_risk_score(),
            'ipo_readiness': self.calculate_ipo_readiness(),
            'shark_tank_score': self.calculate_shark_tank_score(),
            'expansion_recommendation': self.expansion_recommendation(),
            
            # Bonus
            'customer_acquisition_cost': self.calculate_cac(),
            'avg_revenue_per_booking': self.calculate_avg_revenue_per_booking(),
            'operating_efficiency': self.calculate_operating_efficiency(),
            'cash_flow_health': self.cash_flow_health(),
            'market_position': self.market_position_indicator()
        }