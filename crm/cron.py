from datetime import datetime
import requests

def log_crm_heartbeat():
    now = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    log_message = f"{now} CRM is alive\n"
    
    # Write to log
    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(log_message)

    # Optional: Verify GraphQL endpoint
    try:
        response = requests.post(
            'http://localhost:8000/graphql',
            json={'query': '{ hello }'}
        )
        if response.status_code == 200:
            print("GraphQL heartbeat OK")
        else:
            print("GraphQL heartbeat failed")
    except Exception as e:
        print(f"GraphQL heartbeat exception: {e}")
