#!/bin/bash

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to project root (one level above crm/)
cd "$SCRIPT_DIR/.."

# Check if we are in the correct directory
CWD=$(pwd)
if [[ "$CWD" == *"/crm" ]]; then
	    cd ..
    else
	        echo "Unexpected working directory: $CWD"
fi

# Run cleanup using manage.py shell
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

# Log result
if [[ "$DELETED_COUNT" -gt 0 ]]; then
	    echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted $DELETED_COUNT inactive customers" >> /tmp/customer_cleanup_log.txt
    else
	        echo "$(date '+%Y-%m-%d %H:%M:%S') - No inactive customers found" >> /tmp/customer_cleanup_log.txt
fi

