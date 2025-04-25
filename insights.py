import pandas as pd

def generate_insights(df):
    insights = []

    if 'Revenue' in df.columns:
        total_revenue = df['Revenue'].sum()
        avg_revenue = df['Revenue'].mean()
        max_revenue = df['Revenue'].max()
        min_revenue = df['Revenue'].min()
        insights.append(f"Total Revenue: ${total_revenue:,.2f}")
        insights.append(f"Average Revenue: ${avg_revenue:,.2f}")
        insights.append(f"Max Revenue: ${max_revenue:,.2f}")
        insights.append(f"Min Revenue: ${min_revenue:,.2f}")

        if 'Date' in df.columns:
            df_sorted = df.sort_values('Date')
            revenue_growth = df_sorted['Revenue'].iloc[-1] - df_sorted['Revenue'].iloc[0]
            insights.append(f"Revenue Growth (Start to End): ${revenue_growth:,.2f}")

    if 'Expense' in df.columns:
        total_expense = df['Expense'].sum()
        avg_expense = df['Expense'].mean()
        max_expense = df['Expense'].max()
        min_expense = df['Expense'].min()
        insights.append(f"Total Expenses: ${total_expense:,.2f}")
        insights.append(f"Average Expense: ${avg_expense:,.2f}")
        insights.append(f"Max Expense: ${max_expense:,.2f}")
        insights.append(f"Min Expense: ${min_expense:,.2f}")

        if 'Category' in df.columns:
            top_expense_category = df.groupby('Category')['Expense'].sum().idxmax()
            insights.append(f"Top Expense Category: {top_expense_category}")

    if 'Profit' in df.columns:
        total_profit = df['Profit'].sum()
        avg_profit = df['Profit'].mean()
        profit_margin = (total_profit / total_revenue) * 100 if 'Revenue' in df.columns and total_revenue != 0 else 0
        insights.append(f"Total Profit: ${total_profit:,.2f}")
        insights.append(f"Average Profit: ${avg_profit:,.2f}")
        insights.append(f"Profit Margin: {profit_margin:.2f}%")

    if 'Date' in df.columns:
        df['Month'] = df['Date'].dt.to_period('M')
        monthly_revenue = df.groupby('Month')['Revenue'].sum()
        highest_month = monthly_revenue.idxmax()
        insights.append(f"Month with Highest Revenue: {highest_month}")

    return insights
