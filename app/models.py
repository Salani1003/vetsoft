from datetime import datetime

from django.db import models


def validate_client(data):
    """Validates the clients data."""
    errors = {}

    name = data.get("name", "")
    phone = data.get("phone", "")
    email = data.get("email", "")

    if name == "":
        errors["name"] = "Por favor ingrese un nombre"

    if phone == "":
        errors["phone"] = "Por favor ingrese un teléfono"

    if email == "":
        errors["email"] = "Por favor ingrese un email"
    elif email.count("@") == 0:
        errors["email"] = "Por favor ingrese un email valido"

    return errors


def validate_pet(data):
    """
    Validates the pets data
    """
    errors = {}

    name = data.get("name", "")
    breed = data.get("breed", "")
    birthday = data.get("birthday", "")
    client = data.get("client", "")

    if not name:
        errors["name"] = "Por favor ingrese un nombre para la mascota."

    if not breed:
        errors["breed"] = "Por favor ingrese una raza para la mascota."

    if not birthday:
        errors["birthday"] = (
            "Por favor ingrese una fecha de nacimiento para la mascota."
        )

    if not client:
        errors["client"] = "Por favor seleccione un cliente para la mascota."

    today = datetime.now().date()
    if isinstance(birthday, str) and birthday != "":
        birthday = datetime.fromisoformat(birthday).date()
    if birthday >= today:
        errors["invalid_birthday"] = "Por favor ingrese una fecha de nacimiento valida."

    return errors


def validate_vet(data):
    """
    Validates the vets data
    """
    errors = {}

    name = data.get("name", "")
    phone = data.get("phone", "")
    email = data.get("email", "")

    if name == "":
        errors["name"] = "Por favor ingrese un nombre"

    if phone == "":
        errors["phone"] = "Por favor ingrese un teléfono"

    if email == "":
        errors["email"] = "Por favor ingrese un email"
    elif email.count("@") == 0:
        errors["email"] = "Por favor ingrese un email valido"

    return errors


def validate_provider(data):
    """
    Validates the providers data
    """
    errors = {}

    name = data.get("name", "")
    email = data.get("email", "")
    address = data.get("address", "")

    if name == "":
        errors["name"] = "Por favor ingrese un nombre"

    if email == "":
        errors["email"] = "Por favor ingrese un email"
    elif email.count("@") == 0:
        errors["email"] = "Por favor ingrese un email valido"
    if address == "":
        errors["address"] = "Por favor ingrese una dirección"

    return errors


def validate_product(data):
    """
    Validates the products data
    """
    errors = {}

    name = data.get("name", "")
    type = data.get("type", "")
    price = data.get("price", "")

    if not name:
        errors["name"] = "Por favor ingrese un nombre del producto."

    if not type:
        errors["type"] = "Por favor ingrese el tipo de producto."

    if not price:
        errors["price"] = "Por favor ingrese el precio del producto."
    elif not float(price) > 0:
        errors["price"] = "Por favor ingrese un precio mayor a 0."

    return errors


def validate_appointment(data):
    """
    Validates the appointments data
    """
    errors = {}

    pet = data.get("pet", "")
    vet = data.get("vet", "")
    date = data.get("date", "")
    time = data.get("time", "")

    if not pet:
        errors["pet"] = "Por favor seleccione una mascota."

    if not vet:
        errors["vet"] = "Por favor seleccione un veterinario."

    if not date:
        errors["date"] = "Por favor seleccione una fecha."

    if not time:
        errors["time"] = "Por favor seleccione una hora."

    return errors


def validate_medicine(data):
    """
    Validates the medicine data
    """
    errors = {}

    name = data.get("name", "")
    description = data.get("description", "")
    dose = data.get("dose", "")

    if not name:
        errors["name"] = "Por favor ingrese un nombre del medicamento."

    if not description:
        errors["description"] = "Por favor ingrese la descripción del medicamento."

    if not dose:
        errors["dose"] = "Por favor ingrese la dosis del medicamento."
    else:
        dose_value = float(dose)
        if dose_value < 1.0 or dose_value > 10.0:
            errors["dose"] = "La dosis debe estar entre 1 y 10."

    return errors


class Client(models.Model):
    """Client model"""

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

    @classmethod
    def save_client(cls, client_data):
        """Save a new client to the database""" 
        errors = validate_client(client_data)

        if len(errors.keys()) > 0:
            return False, errors

        Client.objects.create(
            name=client_data.get("name"),
            phone=client_data.get("phone"),
            email=client_data.get("email"),
            address=client_data.get("address"),
        )

        return True, None

    def update_client(self, client_data):
        """Update an existing client in the database"""
        self.name = client_data.get("name", "") or self.name
        self.email = client_data.get("email", "") or self.email
        self.phone = client_data.get("phone", "") or self.phone
        self.address = client_data.get("address", "") or self.address

        self.save()


class Pet(models.Model):
    """Pet model"""

    name = models.CharField(max_length=20)
    breed = models.CharField(max_length=20)
    birthday = models.DateField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @classmethod
    def save_pet(cls, pet_data):
        """Save a new pet to the database"""
        errors = validate_pet(pet_data)

        if len(errors.keys()) > 0:
            return False, errors

        Pet.objects.create(
            name=pet_data.get("name"),
            breed=pet_data.get("breed"),
            birthday=pet_data.get("birthday"),
            client_id=pet_data.get("client"),
        )

        return True, None

    def update_pet(self, pet_data):
        """Update an existing pet in the database"""
        self.name = pet_data.get("name", "") or self.name
        self.breed = pet_data.get("breed", "") or self.breed
        self.birthday = pet_data.get("birthday", "") or self.birthday
        self.client_id = pet_data.get("client", "") or self.client

        self.save()


class Vet(models.Model):
    """Vet model"""

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return self.name

    @classmethod
    def save_vet(cls, vet_data):
        """Save a new vet to the database"""
        errors = validate_vet(vet_data)

        if len(errors.keys()) > 0:
            return False, errors

        Vet.objects.create(
            name=vet_data.get("name"),
            phone=vet_data.get("phone"),
            email=vet_data.get("email"),
        )

        return True, None

    def update_vet(self, vet_data):
        """Update an existing vet in the database"""
        self.name = vet_data.get("name", "") or self.name
        self.email = vet_data.get("email", "") or self.email
        self.phone = vet_data.get("phone", "") or self.phone

        self.save()


class Provider(models.Model):
    """Provider model"""

    name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    @classmethod
    def save_provider(cls, provider_data):
        """Save a new provider to the database"""
        errors = validate_provider(provider_data)

        if len(errors.keys()) > 0:
            return False, errors

        Provider.objects.create(
            name=provider_data.get("name"),
            email=provider_data.get("email"),
            address=provider_data.get("address"),
        )

        return True, None

    def update_provider(self, provider_data):
        """Update an existing provider in the database"""
        self.name = provider_data.get("name", "") or self.name
        self.email = provider_data.get("email", "") or self.email
        self.address = provider_data.get("address", "") or self.address

        self.save()


class Product(models.Model):
    """Product model"""

    name = models.CharField(max_length=20)
    type = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

    @classmethod
    def save_product(cls, product_data):
        """Save a new product to the database"""
        errors = validate_product(product_data)
        if len(errors.keys()) > 0:
            return False, errors

        Product.objects.create(
            name=product_data.get("name"),
            type=product_data.get("type"),
            price=product_data.get("price"),
        )

        return True, None

    def update_product(self, product_data):
        """Update an existing product in the database"""
        self.name = product_data.get("name", "") or self.name
        self.type = product_data.get("type", "") or self.type
        self.price = product_data.get("price", "") or self.price

        self.save()


class Appointment(models.Model):
    """Appointment model"""

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    vet = models.ForeignKey(Vet, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()

    def __str__(self):
        return self.pet.name

    @classmethod
    def save_appointment(cls, appointment_data):
        """Save a new appointment to the database"""
        errors = validate_appointment(appointment_data)

        if len(errors.keys()) > 0:
            return False, errors

        Appointment.objects.create(
            pet_id=appointment_data.get("pet"),
            vet_id=appointment_data.get("vet"),
            date=appointment_data.get("date"),
            time=appointment_data.get("time"),
        )

        return True, None

    def update_appointment(self, appointment_data):
        """Update an existing appointment in the database"""
        self.pet_id = appointment_data.get("pet", "") or self.pet
        self.vet_id = appointment_data.get("vet", "") or self.vet
        self.date = appointment_data.get("date", "") or self.date
        self.time = appointment_data.get("time", "") or self.time

        self.save()


class Medicine(models.Model):
    """Medicine model"""

    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100)
    dose = models.FloatField()

    def __str__(self):
        return self.name

    @classmethod
    def save_medicine(cls, medicine_data):
        """Save a new medicine to the database"""
        errors = validate_medicine(medicine_data)

        if len(errors) > 0:
            return False, errors

        cls.objects.create(
            name=medicine_data.get("name"),
            description=medicine_data.get("description"),
            dose=float(medicine_data.get("dose")),
        )

        return True, None

    def update_medicine(self, medicine_data):
        """Update an existing medicine in the database"""
        self.name = medicine_data.get("name", self.name)
        self.description = medicine_data.get("description", self.description)
        self.dose = medicine_data.get("dose", self.dose)

        errors = validate_medicine(
            {
                "name": self.name,
                "description": self.description,
                "dose": self.dose,
            },
        )

        if len(errors.keys()) > 0:
            return False, errors

        self.save()
        return True, None
