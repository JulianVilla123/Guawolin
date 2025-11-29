import uuid
import qrcode
from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.conf import settings
from io import BytesIO
from django.core.files.base import ContentFile


# Modelo personalizado de usuario
class Usuario(AbstractUser):
    email = models.EmailField(unique=True)

    ROLES = (
        ('organizador', 'Organizador'),
        ('asistente', 'Asistente'),
    )
    rol = models.CharField(max_length=20, choices=ROLES)

    def __str__(self):
        return f"{self.username} ({self.rol})"

# Modelo de evento
class Evento(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha = models.DateTimeField()
    lugar = models.CharField(max_length=200)
    imagen = models.ImageField(upload_to='eventos/', blank=True, null=True)
    cupo_maximo = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    organizador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='eventos'
    )

    def boletos_vendidos(self):
        return self.boletos.count()  # relación inversa

    def boletos_disponibles(self):
        return self.cupo_maximo - self.boletos_vendidos()

    def __str__(self):
        return f"{self.titulo} ({self.fecha})"


# Modelo de ticket
class Ticket(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='tickets')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    confirmado = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} – {self.evento.titulo}"

# Modelo de Boleto
class Boleto(models.Model):
    evento = models.ForeignKey("Evento", on_delete=models.CASCADE)
    comprador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="boletos"   # 👈 aquí
    )
    nombre = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_compra = models.DateTimeField(auto_now_add=True)

    codigo_unico = models.CharField(max_length=50, editable=False, null=True, blank=True)
    qr_image = models.ImageField(upload_to="boletos_qr/", blank=True, null=True)

    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.codigo_unico:
            self.codigo_unico = uuid.uuid4().hex[:10]

         # Calcular total siempre que haya precio en el evento
        if self.evento and hasattr(self.evento, "precio"):
            self.total = self.cantidad * self.evento.precio

        super().save(*args, **kwargs)

        if not self.qr_image:
            qr = qrcode.make(f"Boleto {self.id} - Código: {self.codigo_unico}")
            buffer = BytesIO()
            file_name = f"boleto_{self.codigo_unico}.png"
            self.qr_image.save(file_name, ContentFile(buffer.getvalue()), save=False)
            super().save(update_fields=["qr_image"])

    def __str__(self):
        return f"Boleto {self.codigo_unisco} de {self.nombre} para {self.evento.titulo}"

