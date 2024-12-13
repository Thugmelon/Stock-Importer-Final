"""
Data storage module for the stock importer application.

Only have this handle reading and writing portfolio data to CSV files.
Add exceptions too just in case
This module is basically just for logging.
"""
import csv
from typing import Dict, List
import logging
from datetime import datetime
from models import Stock, Portfolio
from config import STOCKS_FILE

logger = logging.getLogger(__name__)

class StorageManager:
    """Manages data persistence for the application."""
    
    @staticmethod
    def save_portfolio(portfolio: Portfolio) -> None:
        """
        Save portfolio data to CSV file.
        
        Args:
            portfolio: Portfolio instance to save
        """
        try:
            with open(STOCKS_FILE, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Ticker", "Quantity", "Price", "Last Updated"])
                
                for stock in portfolio.get_holdings().values():
                    writer.writerow([
                        stock.ticker,
                        stock.quantity,
                        stock.price,
                        stock.last_updated.isoformat()
                    ])
            logger.info("Portfolio saved successfully")
        except Exception as e:
            logger.error(f"Error saving portfolio: {e}")
            raise
    
    @staticmethod
    def load_portfolio() -> Portfolio:
        """
        Load portfolio data from CSV file.
        
        Returns:
            Portfolio instance with loaded data
        """
        portfolio = Portfolio()
        
        try:
            with open(STOCKS_FILE, mode="r", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        stock = Stock(
                            ticker=row["Ticker"],
                            quantity=int(row["Quantity"]),
                            price=float(row["Price"]),
                            last_updated=datetime.fromisoformat(row["Last Updated"])
                        )
                        portfolio.add_stock(stock)
                    except (ValueError, KeyError) as e:
                        logger.error(f"Error parsing row {row}: {e}")
                        continue
                        
            logger.info("Portfolio loaded successfully")
            return portfolio
            
        except FileNotFoundError:
            logger.info("No existing portfolio file found")
            return portfolio
        except Exception as e:
            logger.error(f"Error loading portfolio: {e}")
            raise
