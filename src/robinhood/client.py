import asyncio
import logging
import os
from typing import Dict, List, Optional, Union

from fast_robinhood import Robinhood
from fast_robinhood.exceptions import APIError, AuthenticationError

logger = logging.getLogger(__name__)


class RobinhoodClient:
    """
    A client for interacting with the Robinhood API.
    """

    def __init__(self):
        """
        Initializes the Robinhood client.  Retrieves credentials from environment variables.
        """
        self.username = os.environ.get("ROBINHOOD_USERNAME")
        self.password = os.environ.get("ROBINHOOD_PASSWORD")
        self.robinhood = Robinhood()
        self.is_logged_in = False

        if not self.username or not self.password:
            logger.error(
                "Robinhood username and password must be set as environment variables."
            )
            raise ValueError(
                "Robinhood credentials not found in environment variables."
            )

    async def login(self) -> bool:
        """
        Logs in to the Robinhood API.

        Returns:
            True if login was successful, False otherwise.
        """
        try:
            await self.robinhood.login(username=self.username, password=self.password)
            self.is_logged_in = True
            logger.info("Successfully logged in to Robinhood.")
            return True
        except AuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            return False
        except APIError as e:
            logger.error(f"API error during login: {e}")
            return False
        except Exception as e:
            logger.exception(f"An unexpected error occurred during login: {e}")
            return False

    async def get_quote(self, symbol: str) -> Optional[Dict]:
        """
        Retrieves a quote for a given stock symbol.

        Args:
            symbol: The stock symbol to retrieve the quote for.

        Returns:
            A dictionary containing the quote data, or None if an error occurred.
        """
        try:
            quote = await self.robinhood.get_quote(symbol)
            logger.debug(f"Retrieved quote for {symbol}: {quote}")
            return quote
        except APIError as e:
            logger.error(f"Failed to retrieve quote for {symbol}: {e}")
            return None
        except Exception as e:
            logger.exception(f"An unexpected error occurred while fetching quote for {symbol}: {e}")
            return None

    async def place_order(
        self,
        symbol: str,
        quantity: int,
        side: str,
        order_type: str,
        price: Optional[float] = None,
    ) -> Optional[Dict]:
        """
        Places an order for a given stock.

        Args:
            symbol: The stock symbol to trade.
            quantity: The number of shares to trade.
            side: "buy" or "sell".
            order_type: "market" or "limit".
            price: The limit price for a limit order (optional).

        Returns:
            A dictionary containing the order confirmation, or None if an error occurred.
        """
        try:
            if side not in ("buy", "sell"):
                raise ValueError("Side must be 'buy' or 'sell'.")
            if order_type not in ("market", "limit"):
                raise ValueError("Order type must be 'market' or 'limit'.")

            if order_type == "limit" and price is None:
                raise ValueError("Price must be specified for limit orders.")

            order = await self.robinhood.place_order(
                symbol, quantity, side, order_type, price=price
            )
            logger.info(f"Placed order: {order}")
            return order
        except APIError as e:
            logger.error(f"Failed to place order: {e}")
            return None
        except ValueError as e:
            logger.error(f"Invalid order parameters: {e}")
            return None
        except Exception as e:
            logger.exception(f"An unexpected error occurred while placing order: {e}")
            return None

    async def get_holdings(self) -> Optional[List[Dict]]:
        """
        Retrieves the user's current holdings.

        Returns:
            A list of dictionaries containing the holdings data, or None if an error occurred.
        """
        try:
            holdings = await self.robinhood.get_holdings()
            logger.debug(f"Retrieved holdings: {holdings}")
            return holdings
        except APIError as e:
            logger.error(f"Failed to retrieve holdings: {e}")
            return None
        except Exception as e:
            logger.exception(f"An unexpected error occurred while fetching holdings: {e}")
            return None

    async def get_account(self) -> Optional[Dict]:
        """
        Retrieves the user's account information.

        Returns:
            A dictionary containing the account data, or None if an error occurred.
        """
        try:
            account = await self.robinhood.get_account()
            logger.debug(f"Retrieved account information: {account}")
            return account
        except APIError as e:
            logger.error(f"Failed to retrieve account information: {e}")
            return None
        except Exception as e:
            logger.exception(f"An unexpected error occurred while fetching account information: {e}")
            return None


async def main():
    """
    Example usage of the RobinhoodClient.
    """
    logging.basicConfig(level=logging.DEBUG)  # Set logging level for testing

    client = RobinhoodClient()
    await client.login()

    if client.is_logged_in:
        quote = await client.get_quote("AAPL")
        if quote:
            print(f"AAPL Quote: {quote}")

        # Example of placing a market buy order (replace with your actual logic)
        # order = await client.place_order(
        #     symbol="AAPL", quantity=1, side="buy", order_type="market"
        # )
        # if order:
        #     print(f"Order placed: {order}")

        holdings = await client.get_holdings()
        if holdings:
            print(f"Holdings: {holdings}")

        account = await client.get_account()
        if account:
            print(f"Account Information: {account}")
    else:
        print("Login failed. Check credentials and try again.")


if __name__ == "__main__":
    asyncio.run(main())