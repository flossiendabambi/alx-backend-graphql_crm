#!/bin/bash

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the project root (assumes script is in crm/cron_jobs)
cd "$SCRIPT_DIR/../.."

# Store the current working directory
cwd=$(pwd)

# Confirm we're in the expected location
if [[ "$cwd" == *"/alx-backend-graphql_crm" ]]; then
	    echo "Running cleanup script in $cwd"
    else
	        echo "Unexpected cwd: $cwd"
fi

# Run the Django shell command to clean inactive customers
DELETED_COUNT=$(python3 manage.py shell <<EOF
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer

cutoff = timezone.now() - timedelta(days=365)
qs = Customer.objects.filter(orders__isnull=True, created_at__lt=cutoff)
count = qs.count()
qs.delete()
print(count)
EOF
)

# Log result to /tmp file
if [[ "$DELETED_COUNT" -gt 0 ]]; then
	    echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted $DELETED_COUNT inactive customers" >> /tmp/customer_cleanup_log.txt
    else
	        echo "$(date '+%Y-%m-%d %H:%M:%S') - No inactive customers to delete" >> /tmp/customer_cleanup_log.txt
fi

