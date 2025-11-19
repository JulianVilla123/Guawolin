from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.conf import settings


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
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name='boletos'   # 👈 aquí defines la relación inversa
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    fecha_compra = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Boleto de {self.usuario} para {self.evento.titulo}"


