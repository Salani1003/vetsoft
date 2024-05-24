from django.test import TestCase
from app.models import Client
from app.models import Product


class ClientModelTest(TestCase):
    def test_can_create_and_get_client(self):
        Client.save_client(
            {
                "name": "Juan Sebastian Veron",
                "phone": "221555232",
                "address": "13 y 44",
                "email": "brujita75@hotmail.com",
            }
        )
        clients = Client.objects.all()
        self.assertEqual(len(clients), 1)

        self.assertEqual(clients[0].name, "Juan Sebastian Veron")
        self.assertEqual(clients[0].phone, "221555232")
        self.assertEqual(clients[0].address, "13 y 44")
        self.assertEqual(clients[0].email, "brujita75@hotmail.com")

    def test_can_update_client(self):
        Client.save_client(
            {
                "name": "Juan Sebastian Veron",
                "phone": "221555232",
                "address": "13 y 44",
                "email": "brujita75@hotmail.com",
            }
        )
        client = Client.objects.get(pk=1)

        self.assertEqual(client.phone, "221555232")

        client.update_client({"phone": "221555233"})

        client_updated = Client.objects.get(pk=1)

        self.assertEqual(client_updated.phone, "221555233")

    def test_update_client_with_error(self):
        Client.save_client(
            {
                "name": "Juan Sebastian Veron",
                "phone": "221555232",
                "address": "13 y 44",
                "email": "brujita75@hotmail.com",
            }
        )
        client = Client.objects.get(pk=1)

        self.assertEqual(client.phone, "221555232")

        client.update_client({"phone": ""})

        client_updated = Client.objects.get(pk=1)

        self.assertEqual(client_updated.phone, "221555232")


class ProductModelTest(TestCase):
    def test_can_create_product(self):
        result = Product.save_product(
            {
                "name": "Pelota",
                "type": "Juguete",
                "price": str(33),
            }
        )

        self.assertEqual(result, (True, None))

    def test_cannot_create_product_with_price_0(self):
        result = Product.save_product(
            {
                "name": "Pelota",
                "type": "Juguete",
                "price": str(0),
            }
        )

        self.assertEqual(result, (False, {"price": "Por favor ingrese un precio mayor a 0."}))
    
    def test_cannot_create_product_with_price_negative(self):
        result = Product.save_product(
            {
                "name": "Pelota",
                "type": "Juguete",
                "price": str(-33),
            }
        )

        self.assertEqual(result, (False, {"price": "Por favor ingrese un precio mayor a 0."}))
    
    def test_can_create_product_without_price(self):
        result = Product.save_product(
            {
                "name": "Pelota",
                "type": "Juguete",
                "price": "",
            }
        )

        self.assertEqual(result, (False, {"price": "Por favor ingrese el precio del producto."}))