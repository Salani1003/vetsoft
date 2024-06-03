import os
from datetime import datetime

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from playwright.sync_api import Browser, expect, sync_playwright

from app.models import Client, Medicine, Provider

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
playwright = sync_playwright().start()
headless = os.environ.get("HEADLESS", 1) == 1
slow_mo = os.environ.get("SLOW_MO", 0)


class PlaywrightTestCase(StaticLiveServerTestCase):
    """Base test case for Playwright tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser: Browser = playwright.firefox.launch(
            headless=headless,
            slow_mo=int(slow_mo),
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.browser.close()

    def setUp(self):
        super().setUp()
        self.page = self.browser.new_page()

    def tearDown(self):
        super().tearDown()
        self.page.close()


class HomeTestCase(PlaywrightTestCase):
    """Test case for home page."""

    def test_should_have_navbar_with_links(self):
        self.page.goto(self.live_server_url)

        navbar_home_link = self.page.get_by_test_id("navbar-Home")

        expect(navbar_home_link).to_be_visible()
        expect(navbar_home_link).to_have_text("Home")
        expect(navbar_home_link).to_have_attribute("href", reverse("home"))

        navbar_clients_link = self.page.get_by_test_id("navbar-Clientes")

        expect(navbar_clients_link).to_be_visible()
        expect(navbar_clients_link).to_have_text("Clientes")
        expect(navbar_clients_link).to_have_attribute("href", reverse("clients_repo"))

    def test_should_have_home_cards_with_links(self):
        self.page.goto(self.live_server_url)

        home_clients_link = self.page.get_by_test_id("home-Clientes")

        expect(home_clients_link).to_be_visible()
        expect(home_clients_link).to_have_text("Clientes")
        expect(home_clients_link).to_have_attribute("href", reverse("clients_repo"))


class ClientsRepoTestCase(PlaywrightTestCase):
    """Test case for clients repository."""

    def test_should_show_message_if_table_is_empty(self):
        self.page.goto(f"{self.live_server_url}{reverse('clients_repo')}")

        expect(self.page.get_by_text("No existen clientes")).to_be_visible()

    def test_should_show_clients_data(self):
        Client.objects.create(
            name="Juan Sebastián Veron",
            address="13 y 44",
            phone=54221555232,
            email="brujita75@vetsoft.com",
        )

        Client.objects.create(
            name="Guido Carrillo",
            address="1 y 57",
            phone=54221232555,
            email="goleador@vetsoft.com",
        )

        self.page.goto(f"{self.live_server_url}{reverse('clients_repo')}")

        expect(self.page.get_by_text("No existen clientes")).not_to_be_visible()

        expect(self.page.get_by_text("Juan Sebastián Veron")).to_be_visible()
        expect(self.page.get_by_text("13 y 44")).to_be_visible()
        expect(self.page.get_by_text("54221555232")).to_be_visible()
        expect(self.page.get_by_text("brujita75@vetsoft.com")).to_be_visible()

        expect(self.page.get_by_text("Guido Carrillo")).to_be_visible()
        expect(self.page.get_by_text("1 y 57")).to_be_visible()
        expect(self.page.get_by_text("54221232555")).to_be_visible()
        expect(self.page.get_by_text("goleador@vetsoft.com")).to_be_visible()

    def test_should_show_add_client_action(self):
        self.page.goto(f"{self.live_server_url}{reverse('clients_repo')}")

        add_client_action = self.page.get_by_role(
            "link",
            name="Nuevo cliente",
            exact=False,
        )
        expect(add_client_action).to_have_attribute("href", reverse("clients_form"))

    def test_should_show_client_edit_action(self):
        client = Client.objects.create(
            name="Juan Sebastián Veron",
            address="13 y 44",
            phone=54221555232,
            email="brujita75@vetsoft.com",
        )

        self.page.goto(f"{self.live_server_url}{reverse('clients_repo')}")

        edit_action = self.page.get_by_role("link", name="Editar")
        expect(edit_action).to_have_attribute(
            "href",
            reverse("clients_edit", kwargs={"id": client.id}),
        )

    def test_should_show_client_delete_action(self):
        client = Client.objects.create(
            name="Juan Sebastián Veron",
            address="13 y 44",
            phone=54221555232,
            email="brujita75@vetsoft.com",
        )

        self.page.goto(f"{self.live_server_url}{reverse('clients_repo')}")

        edit_form = self.page.get_by_role(
            "form",
            name="Formulario de eliminación de cliente",
        )
        client_id_input = edit_form.locator("input[name=client_id]")

        expect(edit_form).to_be_visible()
        expect(edit_form).to_have_attribute("action", reverse("clients_delete"))
        expect(client_id_input).not_to_be_visible()
        expect(client_id_input).to_have_value(str(client.id))
        expect(edit_form.get_by_role("button", name="Eliminar")).to_be_visible()

    def test_should_can_be_able_to_delete_a_client(self):
        Client.objects.create(
            name="Juan Sebastián Veron",
            address="13 y 44",
            phone=54221555232,
            email="brujita75@vetsoft.com",
        )

        self.page.goto(f"{self.live_server_url}{reverse('clients_repo')}")

        expect(self.page.get_by_text("Juan Sebastián Veron")).to_be_visible()

        def is_delete_response(response):
            return response.url.find(reverse("clients_delete"))

        # verificamos que el envio del formulario fue exitoso
        with self.page.expect_response(is_delete_response) as response_info:
            self.page.get_by_role("button", name="Eliminar").click()

        response = response_info.value
        self.assertTrue(response.status < 400)

        expect(self.page.get_by_text("Juan Sebastián Veron")).not_to_be_visible()


class ClientCreateEditTestCase(PlaywrightTestCase):
    """Test case for clients creation and edition."""

    def test_cant_update_to_invalid_phone(self):
        client = Client.objects.create(
            name="Juan Sebastián Veron",
            address="13 y 44",
            phone=54221555232,
            email="brujita75@vetsoft.com",
        )
        self.page.goto(f"{self.live_server_url}{reverse('clients_repo')}")
        self.page.get_by_role("link", name="Editar").click()
        self.page.get_by_label("Teléfono").fill("435345354")
        self.page.get_by_role("button", name="Guardar").click()


    def test_should_be_able_to_create_a_new_client(self):
        self.page.goto(f"{self.live_server_url}{reverse('clients_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_label("Nombre").fill("Martin Palermo")
        self.page.get_by_label("Teléfono").fill("54221555232")
        self.page.get_by_label("Email").fill("brujita75@vetsoft.com")
        self.page.get_by_label("Dirección").fill("13 y 44")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text("Martin Palermo")).to_be_visible()
        expect(self.page.get_by_text("54221555232")).to_be_visible()
        expect(self.page.get_by_text("brujita75@vetsoft.com")).to_be_visible()
        expect(self.page.get_by_text("13 y 44")).to_be_visible()

    def test_should_view_errors_if_form_is_invalid(self):
        self.page.goto(f"{self.live_server_url}{reverse('clients_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text("Por favor ingrese un nombre")).to_be_visible()
        expect(self.page.get_by_text("Por favor ingrese un teléfono")).to_be_visible()
        expect(self.page.get_by_text("Por favor ingrese un email")).to_be_visible()

        self.page.get_by_label("Nombre").fill("Juan Sebastián Veron")
        self.page.get_by_label("Teléfono").fill("54221555232")
        self.page.get_by_label("Email").fill("brujita75")
        self.page.get_by_label("Dirección").fill("13 y 44")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text("Por favor ingrese un nombre")).not_to_be_visible()
        expect(
            self.page.get_by_text("Por favor ingrese un teléfono"),
        ).not_to_be_visible()

        expect(
            self.page.get_by_text("Por favor ingrese un email valido"),
        ).to_be_visible()

    def test_should_be_able_to_edit_a_client(self):
        client = Client.objects.create(
            name="Juan Sebastián Veron",
            address="13 y 44",
            phone=54221555232,
            email="brujita75@vetsoft.com",
        )

        path = reverse("clients_edit", kwargs={"id": client.id})
        self.page.goto(f"{self.live_server_url}{path}")

        self.page.get_by_label("Nombre").fill("Guido Carrillo")
        self.page.get_by_label("Teléfono").fill("54221232555")
        self.page.get_by_label("Email").fill("goleador@vetsoft.com")
        self.page.get_by_label("Dirección").fill("1 y 57")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text("Juan Sebastián Veron")).not_to_be_visible()
        expect(self.page.get_by_text("13 y 44")).not_to_be_visible()
        expect(self.page.get_by_text("54221555232")).not_to_be_visible()
        expect(self.page.get_by_text("brujita75@vetsoft.com")).not_to_be_visible()

        expect(self.page.get_by_text("Guido Carrillo")).to_be_visible()
        expect(self.page.get_by_text("1 y 57")).to_be_visible()
        expect(self.page.get_by_text("54221232555")).to_be_visible()
        expect(self.page.get_by_text("goleador@vetsoft.com")).to_be_visible()

        edit_action = self.page.get_by_role("link", name="Editar")
        expect(edit_action).to_have_attribute(
            "href",
            reverse("clients_edit", kwargs={"id": client.id}),
        )


class ProductCreateEditTestCase(PlaywrightTestCase):
    """Test case for products creation and edition."""

    def test_should_not_be_able_to_create_a_product_with_negative_or_zero_price(self):
        self.page.goto(f"{self.live_server_url}{reverse('products_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_label("Nombre").fill("Pelota")
        self.page.get_by_label("Tipo").fill("Juguete")
        self.page.get_by_label("Precio").fill("0")

        self.page.get_by_role("button", name="Guardar").click()

        expect(
            self.page.get_by_text("Por favor ingrese un precio mayor a 0."),
        ).to_be_visible()

        self.page.get_by_label("Precio").fill("-10")

        self.page.get_by_role("button", name="Guardar").click()

        expect(
            self.page.get_by_text("Por favor ingrese un precio mayor a 0."),
        ).to_be_visible()


class MedicineCreateEditTestCase(PlaywrightTestCase):
    """Test case for medicines creation and edition."""

    def test_should_not_be_able_to_create_a_new_medicine_whit_invalid_data(self):
        self.page.goto(f"{self.live_server_url}{reverse('medicines_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_role("button", name="Guardar").click()

        expect(
            self.page.get_by_text("Por favor ingrese un nombre del medicamento."),
        ).to_be_visible()
        expect(
            self.page.get_by_text("Por favor ingrese la descripción del medicamento."),
        ).to_be_visible()
        expect(
            self.page.get_by_text("Por favor ingrese la dosis del medicamento."),
        ).to_be_visible()

    def test_should_be_able_to_create_a_new_medicine(self):
        self.page.goto(f"{self.live_server_url}{reverse('medicines_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_label("Nombre").fill("Ivermectina")
        self.page.get_by_label("Descripción").fill("Antiparasitario")
        self.page.get_by_label("Dosis").fill("1")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text("Ivermectina")).to_be_visible()
        expect(self.page.get_by_text("Antiparasitario")).to_be_visible()
        expect(self.page.get_by_text("1.0")).to_be_visible()

    def test_should_be_able_to_edit_a_medicine(self):
        medicine = Medicine.objects.create(
            name="Ivermectina",
            description="Antiparasitario",
            dose=1,
        )

        path = reverse("medicines_edit", kwargs={"id": medicine.id})
        self.page.goto(f"{self.live_server_url}{path}")

        self.page.get_by_label("Nombre").fill("Paracetamol")
        self.page.get_by_label("Descripción").fill("Analgésico")
        self.page.get_by_label("Dosis").fill("5")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text("Ivermectina")).not_to_be_visible()
        expect(self.page.get_by_text("Antiparasitario")).not_to_be_visible()
        expect(self.page.get_by_text("1.0")).not_to_be_visible()

        expect(self.page.get_by_text("Paracetamol")).to_be_visible()
        expect(self.page.get_by_text("Analgésico")).to_be_visible()
        expect(self.page.get_by_text("5.0")).to_be_visible()

        edit_action = self.page.get_by_role("link", name="Editar")
        expect(edit_action).to_have_attribute(
            "href",
            reverse("medicines_edit", kwargs={"id": medicine.id}),
        )

    def test_should_not_be_able_to_edit_a_medicine_whit_dose_gratter_than_10(self):
        medicine = Medicine.objects.create(
            name="Ivermectina",
            description="Antiparasitario",
            dose=1,
        )

        path = reverse("medicines_edit", kwargs={"id": medicine.id})
        self.page.goto(f"{self.live_server_url}{path}")

        self.page.get_by_label("Dosis").fill("30")

        self.page.get_by_role("button", name="Guardar").click()

        expect(
            self.page.get_by_text("La dosis debe estar entre 1 y 10."),
        ).to_be_visible()

    def test_should_not_be_able_to_edit_a_medicine_whit_dose_lower_than_1(self):
        medicine = Medicine.objects.create(
            name="Ivermectina",
            description="Antiparasitario",
            dose=1,
        )

        path = reverse("medicines_edit", kwargs={"id": medicine.id})
        self.page.goto(f"{self.live_server_url}{path}")

        self.page.get_by_label("Dosis").fill("0")

        self.page.get_by_role("button", name="Guardar").click()

        expect(
            self.page.get_by_text("La dosis debe estar entre 1 y 10."),
        ).to_be_visible()

    def test_should_response_with_404_status_if_medicine_doesnt_exists(self):
        response = self.client.get(reverse("medicines_edit", kwargs={"id": 100}))
        self.assertEqual(response.status_code, 404)

    def test_should_be_able_to_delete_a_medicine(self):
        Medicine.objects.create(
            name="Ivermectina",
            description="Antiparasitario",
            dose=1,
        )

        self.page.goto(f"{self.live_server_url}{reverse('medicines_repo')}")

        expect(self.page.get_by_text("Ivermectina")).to_be_visible()

        def is_delete_response(response):
            return response.url.find(reverse("medicines_delete"))

        with self.page.expect_response(is_delete_response) as response_info:
            self.page.get_by_role("button", name="Eliminar").click()

        response = response_info.value
        self.assertTrue(response.status < 400)

        expect(self.page.get_by_text("Ivermectina")).not_to_be_visible()

    def test_should_show_medicines_data(self):
        Medicine.objects.create(
            name="Ivermectina",
            description="Antiparasitario",
            dose=1,
        )

        Medicine.objects.create(
            name="Paracetamol",
            description="Analgésico",
            dose=5,
        )

        self.page.goto(f"{self.live_server_url}{reverse('medicines_repo')}")

        expect(self.page.get_by_text("Ivermectina")).to_be_visible()
        expect(self.page.get_by_text("Antiparasitario")).to_be_visible()
        expect(self.page.get_by_text("1.0")).to_be_visible()

        expect(self.page.get_by_text("Paracetamol")).to_be_visible()
        expect(self.page.get_by_text("Analgésico")).to_be_visible()
        expect(self.page.get_by_text("5.0")).to_be_visible()


class PetCreateEditTestCase(PlaywrightTestCase):
    """Test case for pets creation and edition."""

    def test_should_not_be_able_to_create_pet_with_birthday_today(self):
        self.page.goto(f"{self.live_server_url}{reverse('pets_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()
        self.page.get_by_label("Nombre").click()
        self.page.get_by_label("Nombre").fill("pocchi")
        self.page.get_by_label("Raza").click()
        self.page.get_by_label("Raza").fill("shiba")
        self.page.get_by_label("Fecha de nacimiento").fill(str(datetime.today().date()))
        self.page.get_by_role("button", name="Guardar").click()
        expect(self.page.get_by_text("Por favor ingrese una fecha")).to_be_visible()

    def test_should_be_able_to_create_a_new_pet(self):
        Client.save_client(
            {
                "name": "duenio",
                "phone": "54221555232",
                "address": "13 y 44",
                "email": "email@vetsoft.com",
            },
        )
        self.page.goto(f"{self.live_server_url}{reverse('pets_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_label("Nombre").fill("Pocchi")
        self.page.get_by_label("Raza").fill("Shiba")
        self.page.get_by_label("Fecha de nacimiento").fill("2021-01-01")
        self.page.get_by_label("Dueño").select_option(label="duenio")
        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.locator("tbody")).to_contain_text("Pocchi")
        expect(self.page.locator("tbody")).to_contain_text("Shiba")


class ProviderCreateEditTestCase(PlaywrightTestCase):
    """Test case for providers creation and edition."""

    def test_should_not_be_able_to_create_a_provider_with_invalid_data(self):
        self.page.goto(f"{self.live_server_url}{reverse('providers_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_label("Nombre").fill("Servicios Veterinarios")
        self.page.get_by_label("Email").fill("email@gmail.com")
        self.page.get_by_label("Dirección").fill("")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text("Por favor ingrese una dirección")).to_be_visible()

    def test_should_be_able_to_create_a_provider(self):
        self.page.goto(f"{self.live_server_url}{reverse('providers_form')}")

        expect(self.page.get_by_role("form")).to_be_visible()

        self.page.get_by_label("Nombre").fill("Servicios Veterinarios")
        self.page.get_by_label("Email").fill("email@gmail.com")
        self.page.get_by_label("Dirección").fill("13 y 44")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text("Servicios Veterinarios")).to_be_visible()
        expect(self.page.get_by_text("email@gmail.com")).to_be_visible()
        expect(self.page.get_by_text("13 y 44")).to_be_visible()

    def test_should_be_able_to_edit_a_provider(self):
        provider = Provider.objects.create(
            name="Proveedor  1 SA",
            email="proveedor1@gmail.com",
            address="brandsen 159",
        )
        path = reverse("providers_edit", kwargs={"id": provider.id})
        self.page.goto(f"{self.live_server_url}{path}")

        self.page.get_by_label("Nombre").fill("Nuevo proveedor SA")
        self.page.get_by_label("Email").fill("unNuevoEmail@gmail.com")
        self.page.get_by_label("Dirección").fill("primera junta 659")

        self.page.get_by_role("button", name="Guardar").click()

        expect(self.page.get_by_text("Proveedor  1 SA")).not_to_be_visible()
        expect(self.page.get_by_text("proveedor1@gmail.com")).not_to_be_visible()
        expect(self.page.get_by_text("brandsen 159")).not_to_be_visible()

        expect(self.page.get_by_text("Nuevo proveedor SA")).to_be_visible()
        expect(self.page.get_by_text("unNuevoEmail@gmail.com")).to_be_visible()
        expect(self.page.get_by_text("primera junta 659")).to_be_visible()

        edit_action = self.page.get_by_role("link", name="Editar")
        expect(edit_action).to_have_attribute(
            "href",
            reverse("providers_edit", kwargs={"id": provider.id}),
        )

    def test_should_be_able_to_delete_a_provider(self):
        Provider.objects.create(
            name="Servicios Veterinarios",
            email="email@gmail.com",
            address="13 y 44",
        )

        self.page.goto(f"{self.live_server_url}{reverse('providers_repo')}")
        expect(self.page.get_by_text("Servicios Veterinarios")).to_be_visible()

        def is_delete_response(response):
            return response.url.find(reverse("providers_delete"))

        with self.page.expect_response(is_delete_response) as response_info:
            self.page.get_by_role("button", name="Eliminar").click()

        response = response_info.value
        self.assertTrue(response.status < 400)

        expect(self.page.get_by_text("Servicios Veterinarios")).not_to_be_visible()
