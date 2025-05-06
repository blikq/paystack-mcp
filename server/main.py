import argparse
import os
import uvicorn

from paystack_service import PaystackService, get_paystack_secret_key
from paystack_tools import create_paystack_mcp_server
from server import create_starlette_app



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    args = parser.parse_args()
    

    try:
        paystack_service = PaystackService(get_paystack_secret_key)
        mcp = create_paystack_mcp_server(paystack_service)
        service_name = "Paystack transactions"
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set the PAYSTACK_SECRET_KEY environment variable.")
        print("Example: export PAYSTACK_SECRET_KEY=sk_test_your_key_here")
        exit(1)
    
    # Get the MCP server from the FastMCP instance
    mcp_server = mcp._mcp_server  # noqa: WPS437
    
    # Bind SSE request handling to MCP server
    starlette_app = create_starlette_app(mcp_server, debug=True)
    
    print(f"Starting MCP {service_name} server on http://{args.host}:{args.port}")
    uvicorn.run(starlette_app, host=args.host, port=args.port)