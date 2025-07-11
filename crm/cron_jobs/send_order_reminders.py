#!/usr/bin/env python3

from datetime import datetime, timedelta
import logging
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Configure logging
log_file = "/tmp/order_reminders_log.txt"
logging.basicConfig(filename=log_file, level=logging.INFO)

# GraphQL client setup
transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
                verify=False,
                    retries=3,
                    )

client = Client(transport=transport, fetch_schema_from_transport=True)

# Dates
today = datetime.now()
seven_days_ago = today - timedelta(days=7)

# GraphQL query
query = gql("""
        query GetRecentOrders($fromDate: DateTime!) {
          orders(orderDate_Gte: $fromDate) {
              id
                  customer {
                        email
                            }
                              }
                              }
                              """)

# Run the query
params = {"fromDate": seven_days_ago.isoformat()}
response = client.execute(query, variable_values=params)

# Log orders
for order in response.get("orders", []):
        order_id = order["id"]
            email = order["customer"]["email"]
                timestamp = today.strftime("%Y-%m-%d %H:%M:%S")
                    logging.info(f"{timestamp} - Order ID: {order_id}, Email: {email}")

                    print("Order reminders processed!")

