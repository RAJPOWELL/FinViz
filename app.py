from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import uuid
import pdfkit
from insights import generate_insights

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


def preprocess_data(filepath):
    df = pd.read_csv(filepath)
    df.dropna(inplace=True)
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df.sort_values('Date', inplace=True)
    return df


def generate_charts(df):
    charts = {}

    if 'Date' in df.columns:
        if 'Revenue' in df.columns:
            fig = px.line(df, x='Date', y='Revenue', title='Revenue Over Time')
            charts['revenue_line'] = fig.to_html(full_html=False)

            fig = px.area(df, x='Date', y='Revenue', title='Cumulative Revenue Growth')
            charts['revenue_area'] = fig.to_html(full_html=False)

        if 'Profit' in df.columns:
            fig = px.line(df, x='Date', y='Profit', title='Profit Over Time', line_shape='spline')
            charts['profit_line'] = fig.to_html(full_html=False)

        if 'Revenue' in df.columns and 'Expense' in df.columns:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['Date'], y=df['Revenue'], mode='lines', name='Revenue'))
            fig.add_trace(go.Scatter(x=df['Date'], y=df['Expense'], mode='lines', name='Expense'))
            fig.update_layout(title='Revenue vs Expense Over Time')
            charts['rev_vs_exp'] = fig.to_html(full_html=False)

    if 'Category' in df.columns and 'Expense' in df.columns:
        pie_df = df.groupby('Category')['Expense'].sum().reset_index()
        fig = px.pie(pie_df, names='Category', values='Expense', title='Expenses by Category')
        charts['expenses_pie'] = fig.to_html(full_html=False)

        fig = px.bar(pie_df, x='Category', y='Expense', title='Top Expense Categories')
        charts['expenses_bar'] = fig.to_html(full_html=False)

    if df.select_dtypes(include='number').shape[1] > 1:
        corr = df.select_dtypes(include='number').corr()
        fig = px.imshow(corr, text_auto=True, title='Correlation Heatmap')
        charts['heatmap'] = fig.to_html(full_html=False)

    if 'Date' in df.columns and 'Revenue' in df.columns:
        df['Month'] = df['Date'].dt.to_period('M').astype(str)
        monthly_rev = df.groupby('Month')['Revenue'].sum().reset_index()
        fig = px.bar(monthly_rev, x='Month', y='Revenue', title='Monthly Revenue Trend')
        charts['monthly_revenue'] = fig.to_html(full_html=False)

    return charts


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    file_id = str(uuid.uuid4())
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}.csv")
    file.save(filepath)
    return redirect(url_for('dashboard', file_id=file_id))


@app.route('/dashboard/<file_id>')
def dashboard(file_id):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}.csv")
    df = preprocess_data(filepath)
    charts = generate_charts(df)
    insights = generate_insights(df)
    return render_template('dashboard.html', charts=charts, insights=insights, file_id=file_id)


@app.route('/download/<file_id>')
def download(file_id):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}.csv")
    df = preprocess_data(filepath)
    charts = generate_charts(df)
    insights = generate_insights(df)
    rendered = render_template('pdf_report.html', charts=charts, insights=insights)
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}.pdf")
    pdfkit.from_string(rendered, pdf_path)
    return send_file(pdf_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=False)
