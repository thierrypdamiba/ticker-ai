import logging
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """
    Represents a trading position for a specific asset.
    """
    symbol: str
    quantity: float
    average_price: float


class PositionManager:
    """
    Manages trading positions, tracking quantity and P&L.
    """

    def __init__(self):
        """
        Initializes the PositionManager with an empty position dictionary.
        """
        self.positions: Dict[str, Position] = {}

    def open_position(self, symbol: str, quantity: float, price: float) -> None:
        """
        Opens a new position or adds to an existing position.

        Args:
            symbol: The trading symbol (e.g., "BTCUSD").
            quantity: The quantity of the asset to buy (positive) or sell (negative).
            price: The price at which the asset was bought or sold.
        """
        if symbol in self.positions:
            existing_position = self.positions[symbol]
            total_quantity = existing_position.quantity + quantity
            total_value = (existing_position.quantity * existing_position.average_price) + (quantity * price)

            if total_quantity == 0:
                del self.positions[symbol]
                logger.info(f"Closed position for {symbol}")
            else:
                new_average_price = total_value / total_quantity
                self.positions[symbol] = Position(symbol=symbol, quantity=total_quantity, average_price=new_average_price)
                logger.info(f"Updated position for {symbol}: Quantity={total_quantity}, Avg Price={new_average_price}")

        else:
            if quantity == 0:
                logger.warning(f"Cannot open position with zero quantity for {symbol}")
                return
            self.positions[symbol] = Position(symbol=symbol, quantity=quantity, average_price=price)
            logger.info(f"Opened new position for {symbol}: Quantity={quantity}, Avg Price={price}")

    def close_position(self, symbol: str, price: float) -> Optional[float]:
        """
        Closes an existing position and calculates the P&L.

        Args:
            symbol: The trading symbol.
            price: The price at which the asset was sold.

        Returns:
            The profit or loss from closing the position, or None if the position doesn't exist.
        """
        if symbol not in self.positions:
            logger.warning(f"Cannot close position for {symbol}: No position exists.")
            return None

        position = self.positions[symbol]
        profit_loss = (price - position.average_price) * position.quantity
        del self.positions[symbol]
        logger.info(f"Closed position for {symbol}: Profit/Loss={profit_loss}")
        return profit_loss

    def get_position(self, symbol: str) -> Optional[Position]:
        """
        Retrieves the position for a given symbol.

        Args:
            symbol: The trading symbol.

        Returns:
            The Position object if it exists, otherwise None.
        """
        return self.positions.get(symbol)

    def calculate_profit_loss(self, symbol: str, current_price: float) -> Optional[float]:
        """
        Calculates the unrealized profit or loss for a given symbol based on the current price.

        Args:
            symbol: The trading symbol.
            current_price: The current market price of the asset.

        Returns:
            The unrealized profit or loss, or None if the position doesn't exist.
        """
        position = self.get_position(symbol)
        if not position:
            logger.warning(f"No position found for {symbol} to calculate P&L.")
            return None

        profit_loss = (current_price - position.average_price) * position.quantity
        return profit_loss

    def get_all_positions(self) -> Dict[str, Position]:
        """
        Returns all currently open positions.

        Returns:
            A dictionary containing all open positions.
        """
        return self.positions