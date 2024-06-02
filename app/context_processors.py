from django.urls import reverse

links = [
    {"label": "Home", "href": reverse("home"), "icon": "bi bi-house-door"},
    {"label": "Clientes", "href": reverse("clients_repo"), "icon": "bi bi-people"},
    {"label": "Produtos", "href": reverse("products_repo"), "icon": "bi bi-box"},
    {"label": "Mascotas", "href": reverse("pets_repo"), "icon": "bi bi-paw"},
    {"label": "Veterinarios", "href": reverse("vets_repo"), "icon": "bi bi-person"},
    {"label": "Citas", "href": reverse("appointments_repo"), "icon": "bi bi-calendar"},
    {"label": "Medicamentos", "href": reverse("medicines_repo"), "icon": "bi bi-capsule"},
    {"label": "Proveedores", "href": reverse("providers_repo"), "icon": "bi bi-truck"},
]


def navbar(request):
    """
    Generates a navigation bar with active link indicators.
    This function processes a list of navigation links and marks the current link as active based on the request path.

    """
    def add_active(link):
        copy = link.copy()

        if copy["href"] == "/":
            copy["active"] = request.path == "/"
        else:
            copy["active"] = request.path.startswith(copy.get("href", ""))

        return copy

    return {"links": map(add_active, links)}
