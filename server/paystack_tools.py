from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from paystack_service import PaystackService, format_transaction


def create_paystack_mcp_server(paystack_service: PaystackService) -> FastMCP:
    """Create and configure a FastMCP server with Paystack transaction tools.
    
    Args:
        paystack_service: Initialized PaystackService instance
        
    Returns:
        Configured FastMCP server
    """
    mcp = FastMCP("paystack-transactions")
    
    @mcp.tool()
    async def verify_transaction(reference: str) -> str:
        """Verify a Paystack transaction using its reference.
        
        Args:
            reference: The unique reference code for the transaction
        """
        data = await paystack_service.verify_transaction(reference)
        
        if not data or not data.get("status"):
            return "Failed to verify transaction. Please check the reference and try again."
        
        return format_transaction(data)
    
    @mcp.tool()
    async def fetch_transaction(transaction_id: int) -> str:
        """Fetch details of a specific Paystack transaction by ID.
        
        Args:
            transaction_id: The numeric ID of the transaction
        """
        data = await paystack_service.fetch_transaction(transaction_id)
        
        if not data or not data.get("status"):
            return "Failed to fetch transaction. Please check the ID and try again."
        
        return format_transaction(data)
    
    @mcp.prompt()
    def get_initial_prompts() -> list[base.Message]:
        return [
            base.UserMessage("You are a helpful assistant that can verify and fetch Paystack transaction details."),
        ]
    
    return mcp 