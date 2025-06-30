import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx-backend-graphql_crm.settings")
django.setup()

from crm.models import Customer, Product
from faker import Faker
import random

fake = Faker()

def seed():
    Customer.objects.all().delete()
    Product.objects.all().delete()

    for _ in range(10):
        Customer.objects.create(
            name=fake.name(),
            email=fake.unique.email(),
            phone=fake.phone_number()
        )

    for _ in range(5):
        Product.objects.create(
            name=fake.word(),
            price=round(random.uniform(10, 1000), 2),
            stock=random.randint(0, 50)
        )

    print("Database seeded.")

if __name__ == "__main__":
    seed()
