import os
import yfinance as yf
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy, session

#Getting base directory
basedir = os.path.abspath(os.path.dirname(__file__))

#Initializng Flask and SqlAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Creating Stock Model
class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) #Name of the stock
    ticker = db.Column(db.String(10), nullable=False) #Stock symbol
    shares = db.Column(db.Integer, nullable=False) #Number of shares owned
    price = db.Column(db.Float, nullable=False) #Price of stock
    
    def __repr__(self):
        return f'<Stock {self.ticker}>'

def getStockInformation(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            'name': info.get('longName', 'N/A'),
            'ticker': info.get('symbol', 'N/A'),
            'price': info.get('currentPrice', 0.0),
            'shares': 0  # Default to 0 shares for new stocks
        }
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None


@app.route('/')
def index():
    stocks = Stock.query.all()
    return render_template('index.html', stocks=stocks)


@app.route('/add', methods=['POST'])
def add_stock():
    ticker = request.form['ticker'].upper()
    shares = request.form['shares']

    if not ticker or not shares:
        return redirect('/')
    
    stock_data = getStockInformation(ticker)
    # If stock data is found, add it to the database
    if stock_data['ticker'] is None or stock_data['ticker'] == 'N/A':
        return redirect('/')

    newStock = Stock(
        ticker=stock_data['ticker'],
        shares=shares,
        price=stock_data['price'],
        name= stock_data['name']
    )
    db.session.add(newStock)
    db.session.commit()
    
    return redirect('/')

@app.route('/delete/<int:stock_id>', methods=['POST'])
def delete_stock(stock_id):
    stock = db.session.get(Stock, stock_id)
    
    if stock:
        db.session.delete(stock)
        db.session.commit()
    return redirect('/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)