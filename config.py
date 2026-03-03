"""
Configuration and environment management for the Evolutionary Trading System.
Centralizes all configuration to prevent scattered environment variables.
"""
import os
from typing import Dict, Any
from dataclasses import dataclass
import logging

@dataclass
class TradingConfig:
    """Centralized configuration for trading system parameters"""
    # Firebase Configuration
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase_credentials.json")
    FIREBASE_DATABASE_URL: str = os.getenv("FIREBASE_DATABASE_URL", "")
    
    # Trading Parameters
    INITIAL_CAPITAL: float = 100000.0
    MAX_POSITION_SIZE: float = 0.1  # 10% of capital per trade
    MAX_DRAWDOWN_THRESHOLD: float = 0.2  # 20% max drawdown
    
    # Neuroevolution Parameters
    POPULATION_SIZE: int = 50
    MUTATION_RATE: float = 0.15
    ELITE_COUNT: int = 5
    
    # RL Parameters
    RL_EPISODES: int = 1000
    RL_LEARNING_RATE: float = 0.001
    RL_DISCOUNT_FACTOR: float = 0.99
    
    # Data Parameters
    DATA_WINDOW_SIZE: int = 100
    FEATURE_COUNT: int = 10
    
    # Risk Management
    STOP_LOSS_PERCENT: float = 0.02  # 2% stop loss
    TAKE_PROFIT_PERCENT: float = 0.04  # 4% take profit
    MAX_LEVERAGE: int = 3
    
    # Validation
    VALIDATION_SPLIT: float = 0.2
    MIN_BACKTEST_PERIOD: int = 30  # days
    
    # Logging
    LOG_LEVEL: str = "INFO"

config = TradingConfig()

def validate_config() -> bool:
    """Validate critical configuration parameters"""
    errors = []
    
    # Check Firebase configuration
    if not os.path.exists(config.FIREBASE_CREDENTIALS_PATH):
        errors.append(f"Firebase credentials not found at {config.FIREBASE_CREDENTIALS_PATH}")
    
    if not config.FIREBASE_DATABASE_URL:
        errors.append("FIREBASE_DATABASE_URL environment variable not set")
    
    # Validate trading parameters
    if config.INITIAL_CAPITAL <= 0:
        errors.append("INITIAL_CAPITAL must be positive")
    
    if config.MAX_POSITION_SIZE <= 0 or config.MAX_POSITION_SIZE > 1:
        errors.append("MAX_POSITION_SIZE must be between 0 and 1")
    
    if config.POPULATION_SIZE < 10:
        errors.append("POPULATION_SIZE must be at least 10 for genetic diversity")
    
    if errors:
        for error in errors:
            logging.error(f"Config Validation Error: {error}")
        return False
    
    logging.info("Configuration validated successfully")
    return True