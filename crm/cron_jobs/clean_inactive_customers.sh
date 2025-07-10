#!/bin/bash

# Log file
LOG_FILE="/tmp/customer_cleanup_log.txt"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Run Django management command to delete inactive customers
DELETED_COUNT=$(python3 manage.py shell <<EOF
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer

one_year_ago = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(orders__isnull=True, created_at__lt=one_year_ago)
count = inactive_customers.count()
inactive_customers.delete()
print(count)
EOF
)

# Write to log
echo "$TIMESTAMP - Deleted $DELETED_COUNT inactive customers" >> "$LOG_FILE"
