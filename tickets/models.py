import uuid
import qrcode
from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.conf import settings
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
from django.core.files import File
from django.utils import timezone   

class Usuario(AbstractUser):
    email = models.EmailField(unique=True)

    ROLES = (
        ('desarrollador', 'Desarrollador'),   # Backend
        ('administrador', 'Administrador'),   # Frontend admin
        ('soporte', 'Soporte'),               # Frontend soporte
        ('organizador', 'Organizador'),       # Usuario final tipo organizador
        ('asistente', 'Asistente'),           # Usuario final tipo asistente
    )
    rol = models.CharField(max_length=20, choices=ROLES)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    def __str__(self):
        return f"{self.username} ({self.rol})"
    
    

class EventoFavorito(models.Model):
    usuario = models.ForeignKey("Usuario", on_delete=models.CASCADE)
    evento = models.ForeignKey("Evento", on_delete=models.CASCADE)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("usuario", "evento")
        
        

# Modelo de evento
class Evento(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha = models.DateTimeField()
    lugar = models.CharField(max_length=200)
    imagen = models.ImageField(upload_to='eventos/', blank=True, null=True)
    cupo_maximo = models.PositiveIntegerField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    organizador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='eventos'
    )

    def boletos_vendidos(self):
        return self.boletos.count()  # compras realizadas

    def tickets_vendidos(self):
        return self.tickets.count()  # tickets individuales generados

    def boletos_disponibles(self):
        # Control de aforo real: restar tickets
        return self.cupo_maximo - self.tickets.count()

    def __str__(self):
        return f"{self.titulo} ({self.fecha})"



class Ticket(models.Model):
    ESTADOS = [
        ("activo", "Activo"),
        ("usado", "Usado"),
        ("expirado", "Expirado"),
        ("transferido", "Transferido"),
    ]

    boleto = models.ForeignKey("Boleto", on_delete=models.CASCADE, related_name="tickets")
    evento = models.ForeignKey("Evento", on_delete=models.CASCADE, related_name="tickets")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    codigo_unico = models.CharField(max_length=50, editable=False, null=True, blank=True)
    qr_image = models.ImageField(upload_to="tickets_qr/", blank=True, null=True)

    estado = models.CharField(max_length=20, choices=ESTADOS, default="activo")

    # Campos nuevos para transferencias
    transferido_a = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets_recibidos"
    )
    transferido_por = models.ForeignKey(   # 👈 NUEVO CAMPO
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets_transferidos"
    )
    transferido_email = models.EmailField(null=True, blank=True)
    fecha_transferencia = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.codigo_unico:
            self.codigo_unico = uuid.uuid4().hex[:12].upper()

        if not self.qr_image:
            qr = qrcode.make(self.codigo_unico)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            file_name = f"{self.codigo_unico}.png"
            self.qr_image.save(file_name, ContentFile(buffer.getvalue()), save=False)

        super().save(*args, **kwargs)
        
        
    def transferir_a_usuario(self, nuevo_usuario):
        """Transfiere el ticket a otro usuario de Fiestapp,
        conservando siempre quién lo transfirió."""
        if self.estado != "activo":
            raise ValueError("Solo se pueden transferir tickets activos.")
        if nuevo_usuario == self.usuario:
            raise ValueError("No puedes transferirte el ticket a ti mismo.")

        # Guardar quién lo transfirió
        self.transferido_por = self.usuario
        # Guardar a quién se transfirió
        self.transferido_a = nuevo_usuario
        # Actualizar dueño actual
        self.usuario = nuevo_usuario
        self.fecha_transferencia = timezone.now()
        # 👇 marcar como transferido
        self.estado = "transferido"

        self.save(update_fields=[
            "usuario", "transferido_a", "transferido_por",
            "fecha_transferencia", "estado"
        ])

    def transferir_por_correo(self, email):
        if self.estado != "activo":
            raise ValueError("Solo se pueden transferir tickets activos.")
        if email == self.usuario.email:
            raise ValueError("No puedes enviarte el ticket a tu propio correo.")

        self.transferido_email = email
        self.transferido_por = self.usuario   # 👈 también guardamos quién lo envió
        self.estado = "transferido"
        self.fecha_transferencia = timezone.now()
        self.save(update_fields=["estado", "fecha_transferencia", "transferido_email", "transferido_por"])

        from django.core.mail import EmailMessage
        email_msg = EmailMessage(
            subject=f"Has recibido un ticket para {self.evento.titulo}",
            body=f"Tu código único es {self.codigo_unico}.",
            from_email="noreply@fiestapp.com",
            to=[email],
        )
        if self.qr_image:
            email_msg.attach_file(self.qr_image.path)
        email_msg.send()

    def __str__(self):
        return f"Ticket {self.codigo_unico} - {self.evento.titulo}"








class Boleto(models.Model):
    evento = models.ForeignKey("Evento", on_delete=models.CASCADE, related_name="boletos")
    comprador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="boletos")
    cantidad = models.PositiveIntegerField(default=1)
    fecha_compra = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # saber si es un boleto nuevo

        if self.evento and hasattr(self.evento, "precio"):
            self.total = self.cantidad * self.evento.precio

        # Validación de aforo real
        if self.evento.tickets.count() + self.cantidad > self.evento.cupo_maximo:
            raise ValueError("No hay suficientes lugares disponibles para este evento.")

        super().save(*args, **kwargs)

        # Generar tickets solo si el boleto es nuevo
        if is_new:
            for i in range(self.cantidad):
                ticket = Ticket(
                    boleto=self,
                    evento=self.evento,
                    usuario=self.comprador,
                    estado="activo"  # estado inicial
                )
                ticket.save()  # 👈 dispara el save() de Ticket para generar código y QR


class Incidencia(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('proceso', 'En proceso'),
        ('resuelto', 'Resuelto'),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    respuesta = models.TextField(blank=True, null=True)


    # Relación con el usuario que reporta (organizador o asistente)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='incidencias'
    )

    # Relación con el agente de soporte que atiende
    asignado_a = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidencias_asignadas'
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titulo} - {self.estado}"
