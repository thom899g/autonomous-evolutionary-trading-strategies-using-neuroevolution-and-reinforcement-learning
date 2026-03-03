"""
Firebase client for persistent state management and real-time data streaming.
Centralizes all Firebase interactions with proper error handling.
"""
import firebase_admin
from firebase_admin import credentials, firestore, db
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import json

class FirebaseClient:
    """Singleton Firebase client with connection management"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._app = None
            self._firestore_client = None
            self._realtime_db = None
            self._connected = False
    
    def initialize(self, credential_path: str, database_url: str) -> bool:
        """Initialize Firebase connection with error handling"""
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(credential_path)
                self._app = firebase_admin.initialize_app(cred, {
                    'databaseURL': database_url
                })
                logging.info("Firebase app initialized")
            
            self._firestore_client = firestore.client()
            self._realtime_db = db.reference()
            self._connected = True
            
            # Test connection
            self._test_connection()
            logging.info("Firebase connection established successfully")
            return True
            
        except FileNotFoundError as e:
            logging.error(f"Firebase credentials file not found: {e}")
            return False
        except ValueError as e:
            logging.error(f"Invalid Firebase configuration: {e}")
            return False
        except Exception as e:
            logging.error(f"Failed to initialize Firebase: {e}")
            return False
    
    def _test_connection(self) -> None:
        """Test Firebase connection by writing a test document"""
        test_ref = self._firestore_client.collection('connection_tests').document('test')
        test_ref.set({
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'connected'
        })
        test_ref.delete()  # Clean up test document
    
    def save_strategy(self, strategy_id: str, strategy_data: Dict[str, Any]) -> bool:
        """Save evolved strategy to Firestore with validation"""
        try:
            if not self._connected:
                logging.error("Firebase not connected")
                return False
            
            # Validate strategy data
            required_fields = ['architecture', 'parameters', 'performance_metrics', 'generation']
            for field in required_fields:
                if field not in strategy_data:
                    logging.error(f"Missing required field in strategy: {field}")
                    return False
            
            # Add metadata
            strategy_data['last_updated'] = datetime.utcnow().isoformat()
            strategy_data['status'] = 'active'
            
            # Save to Firestore
            doc_ref = self._firestore_client.collection('evolved_strategies').document(strategy_id)
            doc_ref.set(strategy_data)
            
            # Also update realtime database for quick access
            realtime_ref = self._realtime_db.child('active_strategies').child(strategy_id)
            realtime_ref.set({
                'id': strategy_id,
                'performance': strategy_data.get('performance_metrics', {}),
                'updated_at': strategy_data['last_updated