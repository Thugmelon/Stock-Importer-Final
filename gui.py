"""
GUI for the stock importer app

Used customtkinter in this instead of just tkinter to try it out.
Used help from guide vids on youtube (will list or explain in vid)

(PUT NOTES FOR EVERY FUNCTION JUST IN CASE)

Make sure to have proper exception handling and unit tests too (not required other than to handle invalid
input when it comes to exception handling but the unit tests I just want to see if I can get them right finally.)

GET API TO WORK SOMEHOW 
"""
import customtkinter as ctk
from typing import Dict
import logging
import yfinance as yf
from datetime import datetime
from models import Stock, Portfolio
from storage import StorageManager
from auth import CredentialManager
from config import THEME, LOGIN_WINDOW_SIZE, MAIN_WINDOW_SIZE

logger = logging.getLogger(__name__)

class LoginWindow:
    """Login window for user authentication."""

    def __init__(self) -> None:
        """Initialize login window."""
        self._root = ctk.CTk()
        self._root.geometry(LOGIN_WINDOW_SIZE)
        self._root.title("Stock Portfolio Login")

        # Center the window
        screen_width = self._root.winfo_screenwidth()
        screen_height = self._root.winfo_screenheight()
        x = (screen_width - 500) // 2  # 500 is window width
        y = (screen_height - 350) // 2  # 350 is window height
        self._root.geometry(f"+{x}+{y}")

        self._setup_ui()
        self._load_saved_credentials()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Main frame
        frame = ctk.CTkFrame(self._root)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Title
        title = ctk.CTkLabel(
            frame,
            text="Stock Portfolio Login",
            font=(THEME["font_family"], THEME["title_size"])
        )
        title.pack(pady=20)

        # Username
        self._username_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Username",
            width=200
        )
        self._username_entry.pack(pady=10)

        # Password
        self._password_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Password",
            show="*",
            width=200
        )
        self._password_entry.pack(pady=10)

        # Remember me checkbox
        self._remember_var = ctk.StringVar(value="off")
        remember_me = ctk.CTkCheckBox(
            frame,
            text="Remember Me",
            variable=self._remember_var,
            onvalue="on",
            offvalue="off"
        )
        remember_me.pack(pady=10)

        # Login button
        login_button = ctk.CTkButton(
            frame,
            text="Login",
            command=self._handle_login,
            width=200
        )
        login_button.pack(pady=20)

        # Status message
        self._status_label = ctk.CTkLabel(
            frame,
            text="",
            text_color=THEME["colors"]["error"]
        )
        self._status_label.pack(pady=10)

    def _handle_login(self) -> None:
        """Handle login button click."""
        username = self._username_entry.get().strip()
        password = self._password_entry.get()

        if CredentialManager.verify_credentials(username, password):
            if self._remember_var.get() == "on":
                CredentialManager.save_credentials(username, password)

            self._root.destroy()
            main_app = MainWindow()
            main_app.run()
        else:
            self._status_label.configure(text="Invalid credentials")

    def _load_saved_credentials(self) -> None:
        """Load saved credentials if available."""
        try:
            username, password = CredentialManager.load_credentials()
            self._username_entry.insert(0, username)
            self._password_entry.insert(0, password)
            self._remember_var.set("on")
        except FileNotFoundError:
            pass

    def run(self) -> None:
        """Run the login window."""
        self._root.mainloop()

class MainWindow:
    """Main window for the stock portfolio application."""

    def __init__(self) -> None:
        """Initialize the main window."""
        self._root = ctk.CTk()
        self._root.geometry(MAIN_WINDOW_SIZE)
        self._root.title("Stock Portfolio Manager")

        # Center the window
        screen_width = self._root.winfo_screenwidth()
        screen_height = self._root.winfo_screenheight()
        x = (screen_width - 800) // 2  # 800 is window width
        y = (screen_height - 600) // 2  # 600 is window height
        self._root.geometry(f"+{x}+{y}")

        self._portfolio = StorageManager.load_portfolio()
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Main frame
        frame = ctk.CTkFrame(self._root)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Title
        title = ctk.CTkLabel(
            frame,
            text="Stock Portfolio Manager",
            font=(THEME["font_family"], THEME["title_size"])
        )
        title.pack(pady=20)

        # Input section
        input_frame = ctk.CTkFrame(frame)
        input_frame.pack(fill="x", padx=20, pady=10)

        # Ticker input
        ticker_label = ctk.CTkLabel(input_frame, text="Ticker:")
        ticker_label.pack(side="left", padx=5)

        self._ticker_entry = ctk.CTkEntry(input_frame, width=100)
        self._ticker_entry.pack(side="left", padx=5)

        # Quantity input
        quantity_label = ctk.CTkLabel(input_frame, text="Quantity:")
        quantity_label.pack(side="left", padx=5)

        self._quantity_entry = ctk.CTkEntry(input_frame, width=100)
        self._quantity_entry.pack(side="left", padx=5)

        # Buttons frame
        button_frame = ctk.CTkFrame(frame)
        button_frame.pack(fill="x", padx=20, pady=10)

        # Add stock button
        add_button = ctk.CTkButton(
            button_frame,
            text="Add Stock",
            command=self._add_stock,
            width=150
        )
        add_button.pack(side="left", padx=5)

        # Refresh button
        refresh_button = ctk.CTkButton(
            button_frame,
            text="Refresh Prices",
            command=self._refresh_prices,
            width=150
        )
        refresh_button.pack(side="left", padx=5)

        # Status message
        self._status_label = ctk.CTkLabel(
            frame,
            text="",
            text_color=THEME["colors"]["text"]
        )
        self._status_label.pack(pady=10)

        # Portfolio display
        self._setup_portfolio_display(frame)

    def _setup_portfolio_display(self, parent: ctk.CTkFrame) -> None:
        """Set up the portfolio display area."""
        # Create scrollable frame
        self._portfolio_frame = ctk.CTkScrollableFrame(parent)
        self._portfolio_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Headers
        headers = ["Ticker", "Quantity", "Price", "Total Value", ""]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                self._portfolio_frame,
                text=header,
                font=(THEME["font_family"], THEME["normal_size"], "bold")
            )
            label.grid(row=0, column=i, padx=5, pady=5, sticky="w")

        self._update_portfolio_display()

    def _update_portfolio_display(self) -> None:
        """Update the portfolio display."""
        # Clear existing rows (except headers)
        for widget in self._portfolio_frame.winfo_children()[5:]:
            widget.destroy()

        # Add each stock
        for i, (ticker, stock) in enumerate(self._portfolio.get_holdings().items(), 1):
            # Ticker
            ctk.CTkLabel(
                self._portfolio_frame,
                text=ticker
            ).grid(row=i, column=0, padx=5, pady=2)

            # Quantity
            ctk.CTkLabel(
                self._portfolio_frame,
                text=str(stock.quantity)
            ).grid(row=i, column=1, padx=5, pady=2)

            # Price
            ctk.CTkLabel(
                self._portfolio_frame,
                text=f"${stock.price:.2f}"
            ).grid(row=i, column=2, padx=5, pady=2)

            # Total Value
            ctk.CTkLabel(
                self._portfolio_frame,
                text=f"${stock.total_value:.2f}"
            ).grid(row=i, column=3, padx=5, pady=2)

            # Remove button
            ctk.CTkButton(
                self._portfolio_frame,
                text="Remove",
                command=lambda t=ticker: self._remove_stock(t),
                width=80
            ).grid(row=i, column=4, padx=5, pady=2)

    def _add_stock(self) -> None:
        """Add a stock to the portfolio."""
        try:
            ticker = self._ticker_entry.get().strip().upper()
            if not ticker:
                raise ValueError("Please enter a ticker symbol")

            quantity_str = self._quantity_entry.get().strip()
            if not quantity_str:
                raise ValueError("Please enter a quantity")

            quantity = int(quantity_str)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")

            # Show loading message
            self._status_label.configure(
                text="Fetching stock price...",
                text_color=THEME["colors"]["text"]
            )
            self._root.update()

            # Get current price
            price = self._get_stock_price(ticker)

            # Create and add stock
            stock = Stock(ticker=ticker, quantity=quantity, price=price)
            self._portfolio.add_stock(stock)

            # Save and update display
            StorageManager.save_portfolio(self._portfolio)
            self._update_portfolio_display()

            # Clear inputs and show success message
            self._ticker_entry.delete(0, 'end')
            self._quantity_entry.delete(0, 'end')
            self._status_label.configure(
                text=f"Added {quantity} shares of {ticker}",
                text_color=THEME["colors"]["success"]
            )

        except ValueError as e:
            self._status_label.configure(
                text=str(e),
                text_color=THEME["colors"]["error"]
            )
        except Exception as e:
            logger.error(f"Error adding stock: {e}")
            self._status_label.configure(
                text="Error adding stock",
                text_color=THEME["colors"]["error"]
            )

    def _remove_stock(self, ticker: str) -> None:
        """Remove a stock from the portfolio."""
        try:
            self._portfolio.remove_stock(ticker)
            StorageManager.save_portfolio(self._portfolio)
            self._update_portfolio_display()
            self._status_label.configure(
                text=f"Removed {ticker}",
                text_color=THEME["colors"]["success"]
            )
        except Exception as e:
            logger.error(f"Error removing stock: {e}")
            self._status_label.configure(
                text="Error removing stock",
                text_color=THEME["colors"]["error"]
            )

    def _refresh_prices(self) -> None:
        """Refresh all stock prices."""
        try:
            self._status_label.configure(
                text="Updating prices...",
                text_color=THEME["colors"]["text"]
            )
            self._root.update()

            self._portfolio.update_prices()
            StorageManager.save_portfolio(self._portfolio)
            self._update_portfolio_display()

            self._status_label.configure(
                text="Prices updated successfully",
                text_color=THEME["colors"]["success"]
            )
        except Exception as e:
            logger.error(f"Error refreshing prices: {e}")
            self._status_label.configure(
                text="Error updating prices",
                text_color=THEME["colors"]["error"]
            )

    def _get_stock_price(self, ticker: str) -> float:
        """Get the current stock price."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.fast_info

            if hasattr(info, 'last_price') and info.last_price:
                return float(info.last_price)

            # Fallback to regular info
            info = stock.info
            price = info.get('regularMarketPrice')
            if price:
                return float(price)

            raise ValueError(f"Could not get price for {ticker}")

        except Exception as e:
            logger.error(f"Error fetching price for {ticker}: {str(e)}")
            raise ValueError(f"Error fetching price for {ticker}. Please verify the ticker symbol.")

    def run(self) -> None:
        """Run the main window."""
        self._root.mainloop()