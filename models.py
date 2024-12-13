"""
Data models for the stock importer application.

This module contains the data structures used to represent stocks and portfolios.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict
import logging
import yfinance as yf

logger = logging.getLogger(__name__)

@dataclass
class Stock:
    """
    Represents a stock holding.

    Attributes:
        ticker: Stock symbol
        quantity: Number of shares
        price: Current price per share
        last_updated: Timestamp of last price update
    """
    ticker: str
    quantity: int
    price: float
    last_updated: datetime = datetime.now()

    @property
    def total_value(self) -> float:
        """Calculate total value of the holding."""
        return self.price * self.quantity

class Portfolio:
    """
    Manages a collection of stock holdings.
    """
    def __init__(self) -> None:
        #Initialize an empty portfolio.
        self._holdings: Dict[str, Stock] = {}

    def add_stock(self, stock: Stock) -> None:
        """
        Add a stock to the portfolio.

        Args:
            stock: Stock instance to add
        """
        if stock.ticker in self._holdings:
            # Update quantity if stock already exists
            existing_stock = self._holdings[stock.ticker]
            existing_stock.quantity += stock.quantity
            existing_stock.price = stock.price
            existing_stock.last_updated = stock.last_updated
        else:
            self._holdings[stock.ticker] = stock

    def remove_stock(self, ticker: str) -> None:
        """
        Remove a stock from the portfolio.

        Args:
            ticker: Stock symbol to remove

        Raises:
            KeyError: If ticker not in portfolio
        """
        if ticker not in self._holdings:
            raise KeyError(f"Stock {ticker} not found in portfolio")
        del self._holdings[ticker]

    def update_prices(self) -> None:
        #Update prices for all stocks in portfolio.
        for ticker in list(self._holdings.keys()):
            try:
                stock = yf.Ticker(ticker)
                info = stock.fast_info

                if hasattr(info, 'last_price') and info.last_price:
                    self._holdings[ticker].price = float(info.last_price)
                else:
                    # Fallback to regular info
                    info = stock.info
                    price = info.get('regularMarketPrice')
                    if price:
                        self._holdings[ticker].price = float(price)
                    else:
                        logger.error(f"Could not update price for {ticker}")
                        continue

                self._holdings[ticker].last_updated = datetime.now()

            except Exception as e:
                logger.error(f"Error updating price for {ticker}: {e}")
                continue

    def get_holdings(self) -> Dict[str, Stock]:
        #Get all holdings in the portfolio.
        return self._holdings.copy()

    def get_total_value(self) -> float:
        #Calculate total value of portfolio
        return sum(stock.total_value for stock in self._holdings.values())