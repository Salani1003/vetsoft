from datetime import datetime, timedelta

from django.shortcuts import reverse
from django.test import Client as DjangoClient
from django.test import TestCase

from app.models import Client, Pet, Medicine,Provider


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

class MedicineTest(TestCase):
    def test_repo_use_repo_template(self):
        response = self.client.get(reverse("medicines_repo"))
        self.assertTemplateUsed(response, "medicines/repository.html")

    def test_repo_display_all_medicines(self):
        response = self.client.get(reverse("medicines_repo"))
        self.assertTemplateUsed(response, "medicines/repository.html")

    def test_form_use_form_template(self):
        response = self.client.get(reverse("medicines_form"))
        self.assertTemplateUsed(response, "medicines/form.html")

    def test_can_create_medicine(self):
        response = self.client.post(
            reverse("medicines_form"),
            data={
                "name": "Ibuprofeno",
                "description": "Ibuprofeno 400mg",
                "dose": 1,
            },
        )
        medicines = Medicine.objects.all()
        self.assertEqual(len(medicines), 1)

        self.assertEqual(medicines[0].name, "Ibuprofeno")
        self.assertEqual(medicines[0].description, "Ibuprofeno 400mg")
        self.assertEqual(medicines[0].dose, 1)

        self.assertRedirects(response, reverse("medicines_repo"))

    def test_validation_errors_create_medicine(self):
        response = self.client.post(
            reverse("medicines_form"),
            data={},
        )

        self.assertContains(response, "Por favor ingrese un nombre del medicamento.")
        self.assertContains(response, "Por favor ingrese la descripción del medicamento.")
        self.assertContains(response, "Por favor ingrese la dosis del medicamento.")

    def test_edit_medicine_with_valid_data(self):
        medicine = Medicine.objects.create(
            name="Ibuprofeno",
            description="Ibuprofeno 400mg",
            dose=4,
        )

        response = self.client.post(
            reverse("medicines_form"),
            data={
                "id": medicine.id,
                "name": "Paracetamol",
            },
        )

        # redirect after post
        self.assertEqual(response.status_code, 302)

        editedMedicine = Medicine.objects.get(pk=medicine.id)
        self.assertEqual(editedMedicine.name, "Paracetamol")
        self.assertEqual(editedMedicine.description, medicine.description)
        self.assertEqual(editedMedicine.dose, medicine.dose)

    def test_should_response_with_404_status_if_medicine_doesnt_exists(self):
        response = self.client.get(reverse("medicines_edit", kwargs={"id": 100}))
        self.assertEqual(response.status_code, 404)

    def test_validation_invalid_dose(self):
        response = self.client.post(
            reverse("medicines_form"),
            data={
                "name": "Ibuprofeno",
                "description": "Ibuprofeno 400mg",
                "dose": 11,
            },
        )

        self.assertContains(response, "La dosis debe estar entre 1 y 10.")



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

class ProviderIntegrationTest(TestCase):
    def test_repo_use_repo_template(self):
        response = self.client.get(reverse("providers_repo"))
        self.assertTemplateUsed(response, "providers/repository.html")

    def test_repo_display_all_medicines(self):
        response = self.client.get(reverse("providers_repo"))
        self.assertTemplateUsed(response, "providers/repository.html")

    def test_form_use_form_template(self):
        response = self.client.get(reverse("providers_form"))
        self.assertTemplateUsed(response, "providers/form.html")

    def test_can_create_provider(self):
        response = self.client.post(
            reverse("providers_form"),
            data={
                "name": "Laboratorio Roemmers",
                "address": "13 y 44",
                "email": "laboratorioRoemmers@gmail.com"
                }
        )
        providers = Provider.objects.all()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(providers), 1)
        self.assertEqual(providers[0].name, "Laboratorio Roemmers")
        self.assertEqual(providers[0].address, "13 y 44")
        self.assertEqual(providers[0].email, "laboratorioRoemmers@gmail.com")
        self.assertRedirects(response,reverse("providers_repo"))

    def test_validation_errors_create_provider(self):
        response = self.client.post(
            reverse("providers_form"),
            data={},
        )

        self.assertContains(response, "Por favor ingrese un nombre")
        self.assertContains(response, "Por favor ingrese una dirección")
        self.assertContains(response, "Por favor ingrese un email")

    def test_edit_provider_with_valid_data(self):
        provider=Provider.objects.create(
                name= "Servicios Veterinarios SA",
                email= "Serviciosveterinarios@gmail.com",
                address= "Calle 13 n°1587",
        )

        response = self.client.post(
            reverse("providers_form"),
            data={
                "id": provider.id,
                "name": "Laboratorio Roemmers",
            },
        )

        self.assertEqual(response.status_code, 302)
        editedProvider = Provider.objects.get(pk=provider.id)
        self.assertEqual(editedProvider.name, "Laboratorio Roemmers")
        self.assertEqual(editedProvider.email, provider.email)
        self.assertEqual(editedProvider.address, provider.address)

    def test_should_response_with_404_status_if_provider_doesnt_exists(self):
        response = self.client.get(reverse("providers_edit", kwargs={"id": 100}))
        self.assertEqual(response.status_code, 404)
    
    def test_validation_invalid_email(self):
        response = self.client.post(
            reverse("providers_form"),
            data={
                "name": "Laboratorio Roemmers",
                "email": "laboratorioRoemmersgmail.com",
                "address": "13 y 44",
            },
        )

        self.assertContains(response, "Por favor ingrese un email valido")

    def test_validation_invalid_address(self):
        response = self.client.post(
            reverse("providers_form"),
            data={
                "name": "Laboratorio Roemmers",
                "email": "laboratorioRoemmersgmail.com",
                "address": "",
            },
        )

        self.assertContains(response, "Por favor ingrese una dirección")

    def test_edit_provider_without_name(self):
        # If we want to edit a provider without a name, it should keep the previous name.
        provider=Provider.objects.create(
                name= "Servicios Veterinarios SA",
                email= "Serviciosveterinarios@gmail.com",
                address= "Calle 13 n°1587",
        )

        response = self.client.post(
            reverse("providers_form"),
            data={
                "id": provider.id,
                "name": "",
                "email": "nuevoEmail@gmail.com",
                "address": "Calle 13 n°1587",
            },
        )
        self.assertEqual(response.status_code, 302)
        editedProvider = Provider.objects.get(pk=provider.id)
        self.assertEqual(editedProvider.name, "Servicios Veterinarios SA")

    
