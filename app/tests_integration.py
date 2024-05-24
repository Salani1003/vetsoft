from datetime import datetime, timedelta

from django.shortcuts import reverse
from django.test import Client as DjangoClient
from django.test import TestCase

from app.models import Client, Pet


class HomePageTest(TestCase):
    def test_use_home_template(self):
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(response, "home.html")


class ClientsTest(TestCase):
    def test_repo_use_repo_template(self):
        response = self.client.get(reverse("clients_repo"))
        self.assertTemplateUsed(response, "clients/repository.html")

    def test_repo_display_all_clients(self):
        response = self.client.get(reverse("clients_repo"))
        self.assertTemplateUsed(response, "clients/repository.html")

    def test_form_use_form_template(self):
        response = self.client.get(reverse("clients_form"))
        self.assertTemplateUsed(response, "clients/form.html")

    def test_can_create_client(self):
        response = self.client.post(
            reverse("clients_form"),
            data={
                "name": "Juan Sebastian Veron",
                "phone": "221555232",
                "address": "13 y 44",
                "email": "brujita75@hotmail.com",
            },
        )
        clients = Client.objects.all()
        self.assertEqual(len(clients), 1)

        self.assertEqual(clients[0].name, "Juan Sebastian Veron")
        self.assertEqual(clients[0].phone, "221555232")
        self.assertEqual(clients[0].address, "13 y 44")
        self.assertEqual(clients[0].email, "brujita75@hotmail.com")

        self.assertRedirects(response, reverse("clients_repo"))

    def test_validation_errors_create_client(self):
        response = self.client.post(
            reverse("clients_form"),
            data={},
        )

        self.assertContains(response, "Por favor ingrese un nombre")
        self.assertContains(response, "Por favor ingrese un teléfono")
        self.assertContains(response, "Por favor ingrese un email")

    def test_should_response_with_404_status_if_client_doesnt_exists(self):
        response = self.client.get(reverse("clients_edit", kwargs={"id": 100}))
        self.assertEqual(response.status_code, 404)

    def test_validation_invalid_email(self):
        response = self.client.post(
            reverse("clients_form"),
            data={
                "name": "Juan Sebastian Veron",
                "phone": "221555232",
                "address": "13 y 44",
                "email": "brujita75",
            },
        )

        self.assertContains(response, "Por favor ingrese un email valido")

    def test_edit_user_with_valid_data(self):
        client = Client.objects.create(
            name="Juan Sebastián Veron",
            address="13 y 44",
            phone="221555232",
            email="brujita75@hotmail.com",
        )

        response = self.client.post(
            reverse("clients_form"),
            data={
                "id": client.id,
                "name": "Guido Carrillo",
            },
        )

        # redirect after post
        self.assertEqual(response.status_code, 302)

        editedClient = Client.objects.get(pk=client.id)
        self.assertEqual(editedClient.name, "Guido Carrillo")
        self.assertEqual(editedClient.phone, client.phone)
        self.assertEqual(editedClient.address, client.address)
        self.assertEqual(editedClient.email, client.email)


class ProductTest(TestCase):
    def test_zero_price_validation(self):
        response = self.client.post(
            reverse("products_form"),
            data={
                "name": "Pelota",
                "type": "Juguete",
                "price": str(0),
            },
        )
        self.assertContains(response, "Por favor ingrese un precio mayor a 0.")

    def test_negative_price_validation(self):
        response = self.client.post(
            reverse("products_form"),
            data={
                "name": "Pelota",
                "type": "Juguete",
                "price": str(-1),
            },
        )
        self.assertContains(response, "Por favor ingrese un precio mayor a 0.")


class PetIntegrationTest(TestCase):
    def setUp(self):
        self.example_client = Client.objects.create(
            name="Juan Sebastián Veron",
            address="13 y 44",
            phone="221555232",
            email="brujita75@hotmail.com",
        )

    def test_create_pet_birthday_today(self):
        response = self.client.post(
            reverse("pets_form"),
            data={
                "name": "Fiat",
                "breed": "Labrador",
                "birthday": datetime.now().date(),
                "client": self.example_client.id,
            },
        )

        self.assertEqual(response.status_code, 200)  # returns same page but with error
        self.assertFalse(Pet.objects.filter(name="Fiat").exists())

    def test_create_pet_birthday_past_date(self):
        past_date = datetime.now().date() - timedelta(days=1)
        response = self.client.post(
            reverse("pets_form"),
            data={
                "name": "Buddy",
                "breed": "Beagle",
                "birthday": past_date,
                "client": self.example_client.id,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Pet.objects.count(), 1)
        self.assertEqual(Pet.objects.first().name, "Buddy")
