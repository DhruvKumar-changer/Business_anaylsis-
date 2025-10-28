import numpy as np
import pandas as pd
from datetime import datetime,timedelta
import random


date= []
start_date = datetime(2020,1,1)
product_name= []
units_sold= []
price=[]
revenue=[]
costs_of_goods= []
marketing_cost = []
logistic_cost = []
other_cost = []
total_cost = []
net_profit = []
operating_expenses = []
initial_investment = []
current_cash = []

for i in range(121):
     #random dates
     random_days = random.randint(0,365)
     random_dates = start_date + timedelta(days=random_days)
     date.append(random_dates.strftime('%Y-%m-%d'))

     #random product
     products=f"product{i+1}"
     product_name.append(products)
     
     #random units sold 
     units = random.randint(1,10)
     units_sold.append((units))
     
     # random price
     prices = random.randint(5000,100000)
     price.append(prices)

     # revenue = units * prices
     rev = units * prices
     revenue.append(rev)

     # costs_of _gods = in between (50 to 70)% of the revenue
     cog_percentage = random.uniform(0.5,0.7)
     cog = int(rev * cog_percentage)
     costs_of_goods.append(cog)

     #marketing_cost = in between (5 - 15)% of the revenue
     marketing_percentage = random.uniform(0.05,0.015)
     market = round(rev * marketing_percentage)
     marketing_cost.append(market)

     #logictic_cost = in between (3-8)% of the revenue
     logistic_percentage = random.uniform(0.03,0.08)
     logistic = round(rev * logistic_percentage)
     logistic_cost.append(logistic)

     #other_cost = in between (2-5)% of the revenue
     other_percentage = random.uniform(0.02,0.05)
     other = round(rev * other_percentage)
     other_cost.append(other)

     #total_cost = sum of all the cost
     cost = round(cog + market + logistic + other)
     total_cost.append(cost)

     #operating_expenses = in between (10-20)% of the total_cost 
     operating = round(cost * random.uniform(0.1,0.2))
     operating_expenses.append(operating)
     print(operating_expenses)

     #net_profit = revenue - total_cost
     net = round(rev - cost)
     net_profit.append(net)

     #initial_investment = remain fixed and not include in loop 
     investment = 10000000
     initial_investment.append(investment)
     
     #current_cash = remain fixed and not include in loop 
     cash = 50000
     current_cash.append(cash)


df = pd.DataFrame({
     "Date" : date,
     "Product_Name" : product_name,
     "Units_sold" : units_sold,
     "Price" : price,
     "Revenue" : revenue,
     "Costs_Of_Goods" : costs_of_goods,
     "Marketing_Cost" : marketing_cost,
     "Logistic_Cost" : logistic_cost,
     "Other_Cost" : other_cost,
     "Total_Cost" : total_cost,
     "Net_Profit" : net_profit,
     "Operating_Expenses" : operating_expenses,
     "Initial_Investment" : initial_investment,
     "Current_Cash" : current_cash
}
)
df.to_csv("data/sample_business_data.csv", index=False)
print("CSV Created Successfully")


