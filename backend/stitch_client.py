"""Stitch MCP server client for data integration."""

import os
import json
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# Stitch MCP configuration
STITCH_MCP_URL = "https://stitch.googleapis.com/mcp"
STITCH_API_KEY = os.getenv("STITCH_API_KEY", "AQ.Ab8RN6K9zPD5iDCtL0W4QrGTYuKkQbch0L_qy_PM1XUMLG4w-w")


class StitchClient:
    """Client for interacting with Stitch MCP server."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Stitch client.
        
        Args:
            api_key: Stitch API key. If not provided, uses STITCH_API_KEY from env.
        """
        self.api_key = api_key or STITCH_API_KEY
        self.base_url = STITCH_MCP_URL
        self.headers = {
            "X-Goog-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str = "", data: Optional[Dict] = None) -> Dict:
        """
        Make a request to Stitch MCP server.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (relative to base URL)
            data: Request payload
            
        Returns:
            Response data as dictionary
        """
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=data)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            print(f"❌ Stitch API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   Response: {e.response.text}")
            raise
    
    def sync_quote(self, quote_data: Dict) -> Dict:
        """
        Sync a quote to Stitch.
        
        Args:
            quote_data: Quote data dictionary with items, total_amount, etc.
            
        Returns:
            Sync result from Stitch
        """
        print(f"📤 Syncing quote to Stitch...")
        print(f"   Quote total: {quote_data.get('total_amount', 0):,}원")
        print(f"   Items count: {len(quote_data.get('items', []))}")
        
        try:
            # Format data for Stitch
            stitch_data = {
                "type": "quote",
                "data": {
                    "total_amount": quote_data.get('total_amount', 0),
                    "items": quote_data.get('items', []),
                    "timestamp": quote_data.get('created_at', None),
                    "requirements": quote_data.get('requirements', '')
                }
            }
            
            result = self._make_request("POST", "sync", stitch_data)
            print(f"✅ Quote synced to Stitch successfully")
            return result
        except Exception as e:
            print(f"❌ Failed to sync quote to Stitch: {e}")
            raise
    
    def get_historical_quotes(self, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Get historical quotes from Stitch.
        
        Args:
            filters: Optional filters for querying quotes
            
        Returns:
            List of quote dictionaries
        """
        print(f"📥 Fetching historical quotes from Stitch...")
        
        try:
            result = self._make_request("GET", "quotes", filters)
            quotes = result.get('quotes', [])
            print(f"✅ Retrieved {len(quotes)} quotes from Stitch")
            return quotes
        except Exception as e:
            print(f"❌ Failed to fetch quotes from Stitch: {e}")
            return []
    
    def test_connection(self) -> bool:
        """
        Test connection to Stitch MCP server.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            print(f"🔍 Testing Stitch MCP connection...")
            print(f"   URL: {self.base_url}")
            print(f"   API Key: {self.api_key[:20]}...")
            
            # Try a simple request
            result = self._make_request("GET", "health")
            print(f"✅ Stitch connection successful")
            return True
        except Exception as e:
            print(f"❌ Stitch connection failed: {e}")
            return False


# Global client instance
stitch_client = None

def get_stitch_client() -> Optional[StitchClient]:
    """Get or create Stitch client instance."""
    global stitch_client
    if stitch_client is None and STITCH_API_KEY:
        try:
            stitch_client = StitchClient()
            print("✅ Stitch client initialized")
        except Exception as e:
            print(f"⚠️  Failed to initialize Stitch client: {e}")
            return None
    return stitch_client

