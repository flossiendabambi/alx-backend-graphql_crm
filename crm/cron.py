import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    # Setup GraphQL client
    transport = RequestsHTTPTransport(
        url='http://localhost:8000/graphql',
        verify=False,
        retries=3,
    )

    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Optional: Run a query to check if the server is alive
    try:
        query = gql("""
        query {
            hello
        }
        """)
        result = client.execute(query)
        hello_response = result.get("hello", "No response")
    except Exception as e:
        hello_response = f"Error: {e}"

    # Format timestamp
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_message = f"{timestamp} CRM is alive. GraphQL hello: {hello_response}\n"

    # Append to heartbeat log
    with open("/tmp/crm_heartbeat_log.txt", "a") as log_file:
        log_file.write(log_message)

def update_low_stock():
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    mutation = gql("""
    mutation {
        updateLowStockProducts {
            updatedProducts {
                name
                stock
            }
            message
        }
    }
    """)

    try:
        result = client.execute(mutation)
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
        with open("/tmp/low_stock_updates_log.txt", "a") as f:
            f.write(f"\n{timestamp} - {result['updateLowStockProducts']['message']}\n")
            for product in result['updateLowStockProducts']['updatedProducts']:
                f.write(f"  - {product['name']}: {product['stock']}\n")
    except Exception as e:
        with open("/tmp/low_stock_updates_log.txt", "a") as f:
            f.write(f"\n{timestamp} - ERROR: {e}\n")