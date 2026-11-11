from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import HerramientaForm
from .models import Categoria, Herramienta, Prestamo


class PrestamosTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.socio = user_model.objects.create_user(username='socio', password='ClaveSegura123!')
        self.otro_socio = user_model.objects.create_user(username='otro', password='ClaveSegura123!')
        self.encargado = user_model.objects.create_user(
            username='encargado', password='ClaveSegura123!', is_staff=True
        )
        self.categoria = Categoria.objects.create(nombre='Jardinería')
        self.herramienta = Herramienta.objects.create(
            codigo='HER-001',
            nombre='Pala',
            categoria=self.categoria,
            fecha_ingreso=date.today(),
        )

    def test_herramienta_code_requires_three_digits(self):
        form = HerramientaForm(data={
            'codigo': 'HER-1',
            'nombre': 'Pala',
            'categoria': self.categoria.pk,
            'estado': Herramienta.Estado.BUENO,
            'disponible': True,
            'fecha_ingreso': date.today(),
        })
        self.assertFalse(form.is_valid())
        self.assertIn('codigo', form.errors)

    def test_member_cannot_view_or_cancel_another_members_loan(self):
        prestamo = Prestamo.objects.create(
            socio=self.otro_socio,
            herramienta=self.herramienta,
            fecha_devolucion_esperada=date.today() + timedelta(days=7),
        )
        self.client.force_login(self.socio)
        self.assertNotContains(self.client.get(reverse('mis_prestamos')), 'HER-001')
        response = self.client.post(reverse('cancelar_prestamo', args=[prestamo.pk]))
        self.assertEqual(response.status_code, 404)
        prestamo.refresh_from_db()
        self.assertEqual(prestamo.estado, Prestamo.Estado.PENDIENTE)

    def test_member_can_confirm_and_cancel_request(self):
        self.client.force_login(self.socio)
        response = self.client.post(
            reverse('agregar_solicitud', args=[self.herramienta.pk]), follow=True
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('confirmar_solicitud'))
        self.assertRedirects(response, reverse('mis_prestamos'))
        prestamo = Prestamo.objects.get(socio=self.socio, herramienta=self.herramienta)
        self.assertFalse(Herramienta.objects.get(pk=self.herramienta.pk).disponible)
        self.client.post(reverse('cancelar_prestamo', args=[prestamo.pk]))
        prestamo.refresh_from_db()
        self.assertEqual(prestamo.estado, Prestamo.Estado.CANCELADO)
        self.assertTrue(Herramienta.objects.get(pk=self.herramienta.pk).disponible)

    def test_non_staff_cannot_access_inventory_crud(self):
        self.client.force_login(self.socio)
        response = self.client.get(reverse('herramienta_list'))
        self.assertRedirects(
            response, f'{reverse("login")}?next={reverse("herramienta_list")}'
        )

    def test_staff_can_activate_and_return_a_loan(self):
        self.herramienta.disponible = False
        self.herramienta.save(update_fields=['disponible'])
        prestamo = Prestamo.objects.create(
            socio=self.socio,
            herramienta=self.herramienta,
            fecha_devolucion_esperada=date.today() + timedelta(days=7),
        )
        self.client.force_login(self.encargado)
        self.client.post(reverse('activar_prestamo', args=[prestamo.pk]))
        prestamo.refresh_from_db()
        self.assertEqual(prestamo.estado, Prestamo.Estado.ACTIVO)
        self.client.post(reverse('registrar_devolucion', args=[prestamo.pk]))
        prestamo.refresh_from_db()
        self.assertEqual(prestamo.estado, Prestamo.Estado.DEVUELTO)
        self.assertIsNotNone(prestamo.fecha_devolucion_real)
        self.assertTrue(Herramienta.objects.get(pk=self.herramienta.pk).disponible)

    def test_catalogue_excludes_unavailable_and_repair_tools(self):
        en_reparacion = Herramienta.objects.create(
            codigo='HER-002',
            nombre='Taladro',
            categoria=self.categoria,
            estado=Herramienta.Estado.REPARACION,
            fecha_ingreso=date.today(),
        )
        self.client.force_login(self.socio)
        response = self.client.get(reverse('catalogo'))
        self.assertContains(response, self.herramienta.nombre)
        self.assertNotContains(response, en_reparacion.nombre)

    def test_request_is_limited_to_three_unique_tools(self):
        tools = [self.herramienta]
        for number in range(2, 5):
            tools.append(Herramienta.objects.create(
                codigo=f'HER-00{number}',
                nombre=f'Herramienta {number}',
                categoria=self.categoria,
                fecha_ingreso=date.today(),
            ))
        self.client.force_login(self.socio)
        for tool in tools:
            self.client.post(reverse('agregar_solicitud', args=[tool.pk]))
        self.client.post(reverse('agregar_solicitud', args=[tools[0].pk]))
        self.assertEqual(len(self.client.session['solicitud']), 3)

    def test_category_with_tools_cannot_be_deleted(self):
        self.client.force_login(self.encargado)
        response = self.client.post(reverse('categoria_delete', args=[self.categoria.pk]))
        self.assertRedirects(response, reverse('categoria_list'))
        self.assertTrue(Categoria.objects.filter(pk=self.categoria.pk).exists())
