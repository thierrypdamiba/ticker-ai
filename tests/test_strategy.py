import pytest
import pandas as pd
import numpy as np
from trading_bot.strategy import MomentumStrategy  # Assuming strategy.py exists

# Mock data for testing
@pytest.fixture
def mock_data():
    data = {
        'close': [10, 12, 11, 13, 15, 14, 16, 18, 17, 19],
        'volume': [100, 110, 90, 120, 130, 100, 140, 150, 120, 160]
    }
    return pd.DataFrame(data)

def test_momentum_strategy_initialization():
    strategy = MomentumStrategy(fast_period=5, slow_period=10)
    assert strategy.fast_period == 5
    assert strategy.slow_period == 10

def test_generate_signals_buy(mock_data):
    strategy = MomentumStrategy(fast_period=3, slow_period=6)
    signals = strategy.generate_signals(mock_data)
    # Check if a buy signal is generated when fast MA > slow MA
    # In this mock data, this should happen around index 6
    assert signals.iloc[6] == 1  # Assuming 1 represents a buy signal

def test_generate_signals_sell(mock_data):
    strategy = MomentumStrategy(fast_period=3, slow_period=6)
    signals = strategy.generate_signals(mock_data)
    # Check if a sell signal is generated when fast MA < slow MA
    # In this mock data, this should happen around index 3
    assert signals.iloc[3] == -1  # Assuming -1 represents a sell signal

def test_generate_signals_no_signal(mock_data):
    strategy = MomentumStrategy(fast_period=3, slow_period=6)
    signals = strategy.generate_signals(mock_data)
    # Check if no signal is generated when fast MA == slow MA (or close enough)
    # In this mock data, there should be periods with no signal (0)
    assert 0 in signals.values

def test_generate_signals_empty_data():
    strategy = MomentumStrategy(fast_period=3, slow_period=6)
    empty_data = pd.DataFrame()
    signals = strategy.generate_signals(empty_data)
    assert signals.empty

def test_generate_signals_insufficient_data():
    strategy = MomentumStrategy(fast_period=5, slow_period=10)
    # Create data with less rows than slow_period
    short_data = pd.DataFrame({'close': [1, 2, 3, 4, 5, 6, 7, 8, 9]})
    signals = strategy.generate_signals(short_data)
    assert all(signals.isna()) # Expect all NaN values due to insufficient data

def test_backtest(mock_data):
    strategy = MomentumStrategy(fast_period=3, slow_period=6)
    signals = strategy.generate_signals(mock_data)
    initial_capital = 1000
    results = strategy.backtest(mock_data, signals, initial_capital)

    # Basic checks:
    assert isinstance(results, pd.DataFrame)
    assert 'position' in results.columns
    assert 'profit' in results.columns
    assert results['profit'].iloc[-1] != 0 # Check if profit is not zero

def test_backtest_no_signals(mock_data):
    strategy = MomentumStrategy(fast_period=3, slow_period=6)
    # Create a series of zeros for no signals
    no_signals = pd.Series(np.zeros(len(mock_data)), index=mock_data.index)
    initial_capital = 1000
    results = strategy.backtest(mock_data, no_signals, initial_capital)

    # Check that the profit is zero when there are no signals
    assert results['profit'].iloc[-1] == 0

def test_backtest_empty_data():
    strategy = MomentumStrategy(fast_period=3, slow_period=6)
    empty_data = pd.DataFrame()
    signals = pd.Series()
    initial_capital = 1000
    with pytest.raises(ValueError):
        strategy.backtest(empty_data, signals, initial_capital)

def test_backtest_insufficient_capital(mock_data):
    strategy = MomentumStrategy(fast_period=3, slow_period=6)
    signals = strategy.generate_signals(mock_data)
    initial_capital = 0
    with pytest.raises(ValueError):
        strategy.backtest(mock_data, signals, initial_capital)