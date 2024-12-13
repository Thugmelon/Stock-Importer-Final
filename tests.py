"""
Putting the unit tests in here.

I still mess these up occasionally and got bad grades on the unit tests in almost every lab so
Hopefully these count but I'm not sure.
I added notes for every test.
"""
import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
import shutil
import logging
from pathlib import Path
from datetime import datetime

# Import your application modules
from models import Stock, Portfolio
from storage import StorageManager
from auth import CredentialManager
from config import DEFAULT_USERNAME, DEFAULT_PASSWORD, CREDENTIALS_FILE

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class TestCredentialManager(unittest.TestCase):
    def setUp(self):
        """Setup test fixture."""
        # Create temporary test directory
        self.test_dir = tempfile.mkdtemp()
        self.test_file = Path(self.test_dir) / "test_credentials.txt"

        # Store original config and patch it
        from config import CREDENTIALS_FILE as original_file
        self.original_cred_file = original_file

        # Patch the config module
        import config
        import sys
        config.CREDENTIALS_FILE = self.test_file

        # Also patch the auth module's reference to the config file
        import auth
        auth.CREDENTIALS_FILE = self.test_file

        # Ensure no existing credentials file
        if self.test_file.exists():
            self.test_file.unlink()

    def tearDown(self):
        """Cleanup test fixture."""
        # Remove test directory and restore config
        try:
            if self.test_file.exists():
                self.test_file.unlink()
            if self.test_dir and Path(self.test_dir).exists():
                shutil.rmtree(self.test_dir)
        finally:
            import config
            config.CREDENTIALS_FILE = self.original_cred_file

    def test_credential_flow(self):
        """Test the complete credential verification flow."""
        logger = logging.getLogger(__name__)

        # Check initial state
        logger.debug("Starting credential flow test")
        logger.debug(f"Test file path: {self.test_file}")
        logger.debug(f"Default username: {DEFAULT_USERNAME}")
        logger.debug(f"File exists before test: {self.test_file.exists()}")

        # Ensure no existing credentials file
        if self.test_file.exists():
            logger.debug("Removing existing credentials file")
            self.test_file.unlink()

        # Verify file doesn't exist
        self.assertFalse(
            self.test_file.exists(),
            "Credentials file should not exist at start of test"
        )

        # 1. Test default credentials when no file exists
        logger.debug("Testing default credentials")
        result = CredentialManager.verify_credentials(DEFAULT_USERNAME, DEFAULT_PASSWORD)
        logger.debug(f"Default credentials verification result: {result}")

        self.assertTrue(
            result,
            "Default credentials should work when no credentials file exists"
        )

        # 2. Test saving new credentials
        logger.debug("Testing credential saving")
        test_user = "test_user"
        test_pass = "test_pass"
        CredentialManager.save_credentials(test_user, test_pass)

        self.assertTrue(
            self.test_file.exists(),
            "Credentials file should exist after saving"
        )

        # 3. Test new credentials work
        logger.debug("Testing saved credentials")
        self.assertTrue(
            CredentialManager.verify_credentials(test_user, test_pass),
            "Saved credentials should work"
        )

        # 4. Test default credentials no longer work
        logger.debug("Testing default credentials after saving new ones")
        self.assertFalse(
            CredentialManager.verify_credentials(DEFAULT_USERNAME, DEFAULT_PASSWORD),
            "Default credentials should not work after saving new ones"
        )

        # 5. Test invalid credentials
        logger.debug("Testing invalid credentials")
        self.assertFalse(
            CredentialManager.verify_credentials("wrong", "wrong"),
            "Invalid credentials should not work"
        )

# Rest of the test classes remain the same...
class TestStock(unittest.TestCase):
    def setUp(self):
        """Setup test fixture."""
        self.stock = Stock("AAPL", 10, 150.0)

    def test_total_value(self):
        """Test total value calculation."""
        self.assertEqual(self.stock.total_value, 1500.0)

    def test_attributes(self):
        """Test stock attributes."""
        self.assertEqual(self.stock.ticker, "AAPL")
        self.assertEqual(self.stock.quantity, 10)
        self.assertEqual(self.stock.price, 150.0)
        self.assertIsInstance(self.stock.last_updated, datetime)

class TestPortfolio(unittest.TestCase):
    def setUp(self):
        """Setup test fixture."""
        self.portfolio = Portfolio()
        self.stock = Stock("AAPL", 10, 150.0)

    def test_add_stock(self):
        """Test adding a stock."""
        self.portfolio.add_stock(self.stock)
        holdings = self.portfolio.get_holdings()
        self.assertIn("AAPL", holdings)
        self.assertEqual(holdings["AAPL"].quantity, 10)

    def test_add_existing_stock(self):
        """Test adding to existing position."""
        self.portfolio.add_stock(self.stock)
        additional = Stock("AAPL", 5, 160.0)
        self.portfolio.add_stock(additional)
        holdings = self.portfolio.get_holdings()
        self.assertEqual(holdings["AAPL"].quantity, 15)
        self.assertEqual(holdings["AAPL"].price, 160.0)

    def test_remove_stock(self):
        """Test removing a stock."""
        self.portfolio.add_stock(self.stock)
        self.portfolio.remove_stock("AAPL")
        self.assertNotIn("AAPL", self.portfolio.get_holdings())

    def test_total_value(self):
        """Test portfolio total value."""
        self.portfolio.add_stock(Stock("AAPL", 10, 150.0))
        self.portfolio.add_stock(Stock("GOOGL", 5, 200.0))
        self.assertEqual(self.portfolio.get_total_value(), 2500.0)

class TestStorageManager(unittest.TestCase):
    def setUp(self):
        """Setup test fixture."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = Path(self.test_dir) / "test_portfolio.csv"

        # Store original file path and patch config
        import config
        self.original_stocks_file = config.STOCKS_FILE
        config.STOCKS_FILE = self.test_file

    def tearDown(self):
        """Cleanup test fixture."""
        shutil.rmtree(self.test_dir)
        import config
        config.STOCKS_FILE = self.original_stocks_file

    def test_save_load_portfolio(self):
        """Test saving and loading portfolio."""
        portfolio = Portfolio()
        portfolio.add_stock(Stock("AAPL", 10, 150.0))
        portfolio.add_stock(Stock("GOOGL", 5, 200.0))

        StorageManager.save_portfolio(portfolio)
        loaded = StorageManager.load_portfolio()

        holdings = loaded.get_holdings()
        self.assertEqual(len(holdings), 2)
        self.assertEqual(holdings["AAPL"].quantity, 10)
        self.assertEqual(holdings["GOOGL"].quantity, 5)

if __name__ == '__main__':
    unittest.main(verbosity=2)