import os
from typing import Any, Optional, Callable
import httpx

# Constants
PAYSTACK_API_BASE = "https://api.paystack.co"


def get_paystack_secret_key() -> tuple[str, str]:
    secret_key = os.getenv("PAYSTACK_SECRET_KEY")
    api_base = os.getenv("PAYSTACK_API_BASE", PAYSTACK_API_BASE)

    if not secret_key:
        raise ValueError("Environment variable PAYSTACK_SECRET_KEY is not set.")
    return secret_key, api_base


class PaystackService:
    """Service for interacting with Paystack APIs."""
    
    def __init__(self, get_secret_key: Callable[[], tuple[str, str]]):
        """Initialize the Paystack service with the required API key.
        
        Args:
            secret_key: Your Paystack secret key
            api_base: The base URL for Paystack API (defaults to standard endpoint)
        """
        secret_key, api_base = get_secret_key()

        self.api_base_url = api_base
        self.secret_key = secret_key
        
    async def make_request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any] | None:
        url = f"{self.api_base_url}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    timeout=30.0,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error making Paystack API request: {e}")
                return None
    
    async def verify_transaction(self, reference: str) -> dict[str, Any] | None:
        """Verify a transaction using its reference code.
        
        Args:
            reference: The transaction reference to verify
            
        Returns:
            Transaction verification details or None if request failed
        """
        endpoint = f"/transaction/verify/{reference}"
        return await self.make_request("GET", endpoint)
    
    async def fetch_transaction(self, transaction_id: int) -> dict[str, Any] | None:
        """Fetch details of a transaction by ID.
        
        Args:
            transaction_id: The ID of the transaction to fetch
            
        Returns:
            Transaction details or None if request failed
        """
        endpoint = f"/transaction/{transaction_id}"
        return await self.make_request("GET", endpoint)
    
    # TODO: Add a tool to list transactions
    
    
def format_transaction(data: dict) -> str:
    if not data or "data" not in data or not data["status"]:
        return "No valid transaction data available."
    
    transaction = data["data"]
    
    return f"""
Transaction Details:
ID: {transaction.get('id', 'N/A')}
Reference: {transaction.get('reference', 'N/A')}
Amount: {transaction.get('amount', 0)/100:.2f} {transaction.get('currency', 'NGN')}
Status: {transaction.get('status', 'N/A')}
Channel: {transaction.get('channel', 'N/A')}
Paid At: {transaction.get('paid_at', 'N/A')}
Created At: {transaction.get('created_at', 'N/A')}
Customer:
  Email: {transaction.get('customer', {}).get('email', 'N/A')}
  Name: {transaction.get('customer', {}).get('first_name', '')} {transaction.get('customer', {}).get('last_name', '')}
""" 