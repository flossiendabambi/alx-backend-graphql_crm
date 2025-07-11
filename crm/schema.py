import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.core.validators import RegexValidator
from django.db import transaction
from graphql import GraphQLError
from decimal import Decimal
from datetime import datetime
from graphene_django.filter import DjangoFilterConnectionField
from .filters import CustomerFilter, ProductFilter, OrderFilter
from graphene import relay

# GraphQL types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order


# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise GraphQLError("Email already exists")
        
        if phone:
            validator = RegexValidator(r'^\+?\d[\d\-]{7,}$', "Invalid phone format")
            validator(phone)

        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(graphene.JSONString)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        customers = []
        errors = []

        with transaction.atomic():
            for data in input:
                try:
                    name = data["name"]
                    email = data["email"]
                    phone = data.get("phone", None)

                    if Customer.objects.filter(email=email).exists():
                        raise ValueError(f"Duplicate email: {email}")

                    if phone:
                        validator = RegexValidator(r'^\+?\d[\d\-]{7,}$', "Invalid phone format")
                        validator(phone)

                    customer = Customer(name=name, email=email, phone=phone)
                    customer.save()
                    customers.append(customer)

                except Exception as e:
                    errors.append(str(e))
        return BulkCreateCustomers(customers=customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        stock = graphene.Int(default_value=0)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock):
        if Decimal(price) <= 0:
            raise GraphQLError("Price must be positive")
        if stock < 0:
            raise GraphQLError("Stock cannot be negative")

        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime()

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise GraphQLError("Invalid customer ID")

        if not product_ids:
            raise GraphQLError("At least one product must be selected")

        products = []
        total = Decimal("0.00")
        for pid in product_ids:
            try:
                product = Product.objects.get(id=pid)
                products.append(product)
                total += product.price
            except Product.DoesNotExist:
                raise GraphQLError(f"Invalid product ID: {pid}")

        order = Order(customer=customer, order_date=order_date or datetime.now(), total_amount=total)
        order.save()
        order.products.set(products)
        return CreateOrder(order=order)


# Add to mutation root
class Mutation(StockMutation, graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()


class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(self, info):
        return Customer.objects.all()

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_orders(self, info):
        return Order.objects.all()

class CustomerNode(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (relay.Node, )
        filterset_class = CustomerFilter

class ProductNode(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (relay.Node, )
        filterset_class = ProductFilter

class OrderNode(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (relay.Node, )
        filterset_class = OrderFilter

class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerNode)
    all_products = DjangoFilterConnectionField(ProductNode)
    all_orders = DjangoFilterConnectionField(OrderNode)
    
import graphene
from graphene_django import DjangoObjectType
from crm.models import Product  # adjust if your model path differs

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "stock")

class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass  # no input arguments

    updated_products = graphene.List(ProductType)
    message = graphene.String()

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated = []
        for product in low_stock_products:
            product.stock += 10
            product.save()
            updated.append(product)

        return UpdateLowStockProducts(
            updated_products=updated,
            message=f"{len(updated)} product(s) restocked."
        )

class StockMutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()
