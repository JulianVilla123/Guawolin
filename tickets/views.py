from decimal import Decimal
import re
from django.shortcuts import render,redirect
from guawolin import settings
from . models import EventoFavorito, Ticket, Usuario, Incidencia
from django.contrib import messages
from django.shortcuts import render
from .forms import RegisterAssistantForm, RegisterOrganizerForm, RegisterSoporteForm, RegisterAdminForm, RegisterDevForm, IncidenciaForm
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
import stripe
import uuid
import json
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from tickets.forms import EventoForm
from .models import Evento
from django.http import HttpResponse
from tickets.decoradores import solo_organizadores, solo_asistentes, solo_administradores, solo_desarrolladores, solo_soporte
from django.shortcuts import get_object_or_404 #detalle de evento
from django.contrib import messages #eliminar eventos
from django.db.models import Q
from .models import Evento, Ticket
from django.utils import timezone
from .models import Evento, Boleto
from django.contrib.auth.views import LoginView
from django.urls import reverse, reverse_lazy
from django.db.models import Sum
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST
import smtplib


stripe.api_key = settings.STRIPE_SECRET_KEY

def es_organizador_o_asistente(user):
    return user.is_authenticated and (user.rol == "organizador" or user.rol == "asistente")

def home(request):
    return render(request, 'guawolin/home.html')

class CustomLoginView(LoginView):
    template_name = 'guawolin/login.html'

    def get_success_url(self):
        user = self.request.user

        if user.rol == 'asistente':
            return reverse_lazy('panel_asistente')
        elif user.rol == 'organizador':
            return reverse_lazy('panel_organizador')
        elif user.rol == 'administrador':
            return reverse_lazy('panel_administrador')
        elif user.rol == 'desarrollador':
            return reverse_lazy('panel_desarrollador')
        elif user.rol == 'soporte':
            return reverse_lazy('panel_soporte')
        else:
            return reverse_lazy('home')  # fallback

def logout_view(request):
    logout(request)
    return redirect('home')  # ✅ Asegúrate de que 'home' esté definida en urls.py
  

#Funcion para registrar asistentes
    
def registerAssistant(request):
    if request.method == 'POST':
        form = RegisterAssistantForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']

            if Usuario.objects.filter(username=username).exists():
                messages.error(request, 'El nombre de usuario ya está en uso.')
            elif Usuario.objects.filter(email=email).exists():
                messages.error(request, 'El correo electrónico ya está registrado.')
            else:
                user = form.save(commit=False)
                user.rol = 'asistente'
                user.set_password(form.cleaned_data['password'])
                user.save()

                grupo, _ = Group.objects.get_or_create(name='Asistentes')
                user.groups.add(grupo)

                messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión.')
                return redirect('login')
    else:
        form = RegisterAssistantForm()

    return render(request, 'tickets/ReAssistant.html', {'form': form})


#Funcion para registrar organizadores

def registerOrganizer(request):
    if request.method == 'POST':
        form = RegisterOrganizerForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']

            if Usuario.objects.filter(username=username).exists():
                messages.error(request, 'El nombre de usuario ya está en uso.')
            elif Usuario.objects.filter(email=email).exists():
                messages.error(request, 'El correo electrónico ya está registrado.')
            else:
                user = form.save(commit=False)
                user.rol = 'organizador'
                user.set_password(form.cleaned_data['password'])
                user.save()

                grupo, _ = Group.objects.get_or_create(name='Organizadores')
                user.groups.add(grupo)

                messages.success(request, 'Organizador registrado exitosamente.')
                return redirect('login')
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    else:
        form = RegisterOrganizerForm()

    return render(request, 'tickets/ReOrganizer.html', {'form': form})

#Registro de usuario soporte
def registerSoporte(request):
    if request.method == 'POST':
        form = RegisterSoporteForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']

            if Usuario.objects.filter(username=username).exists():
                messages.error(request, 'El nombre de usuario ya está en uso.')
            elif Usuario.objects.filter(email=email).exists():
                messages.error(request, 'El correo electrónico ya está registrado.')
            else:
                user = form.save(commit=False)
                user.rol = 'soporte'   # 👈 aquí cambias el rol
                user.set_password(form.cleaned_data['password'])
                user.save()

                grupo, _ = Group.objects.get_or_create(name='Soporte')
                user.groups.add(grupo)

                messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión como soporte.')
                return redirect('login')
    else:
        form = RegisterSoporteForm()

    return render(request, 'tickets/ReSoporte.html', {'form': form})

def registerAdmin(request):
    if request.method == 'POST':
        form = RegisterAdminForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']

            if Usuario.objects.filter(username=username).exists():
                messages.error(request, 'El nombre de usuario ya está en uso.')
            elif Usuario.objects.filter(email=email).exists():
                messages.error(request, 'El correo electrónico ya está registrado.')
            else:
                user = form.save(commit=False)
                user.rol = 'administrador'   # 👈 rol administrador
                user.set_password(form.cleaned_data['password'])
                user.save()

                grupo, _ = Group.objects.get_or_create(name='Administradores')
                user.groups.add(grupo)

                messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión como administrador.')
                return redirect('login')
    else:
        form = RegisterAdminForm()

    return render(request, 'tickets/ReAdmin.html', {'form': form})


# Registro de usuario desarrollador
def registerDev(request):
    if request.method == 'POST':
        form = RegisterDevForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']

            if Usuario.objects.filter(username=username).exists():
                messages.error(request, 'El nombre de usuario ya está en uso.')
            elif Usuario.objects.filter(email=email).exists():
                messages.error(request, 'El correo electrónico ya está registrado.')
            else:
                user = form.save(commit=False)
                user.rol = 'desarrollador'   # 👈 rol desarrollador
                user.set_password(form.cleaned_data['password'])
                user.save()

                grupo, _ = Group.objects.get_or_create(name='Desarrolladores')
                user.groups.add(grupo)

                messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión como desarrollador.')
                return redirect('login')
    else:
        form = RegisterDevForm()

    return render(request, 'tickets/ReDev.html', {'form': form})





#configuracion del perfil actualizacion de datos.
def profile_settings(request):
    return render(request, 'guawolin/profile_settings.html')



#view para reportes
@login_required
def reports(request):
    if request.user.rol != 'organizador':
        return redirect('home')
    return render(request, 'tickets/reportes.html')






##FUNCIONES DE ASISTENTE
#Vista para el panel asistentes
@solo_asistentes
def panel_asistente(request):
    now = timezone.now()
    inicio_mes = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    tickets_comprados = Ticket.objects.filter(
        usuario=request.user,
        fecha_registro__gte=inicio_mes,
        fecha_registro__lte=now,
        transferido_por__isnull=True
    )
    tickets_transferidos = Ticket.objects.filter(
        usuario=request.user,
        fecha_registro__gte=inicio_mes,
        fecha_registro__lte=now,
        transferido_por__isnull=False
    )

    incidencias = Incidencia.objects.filter(usuario=request.user).order_by('-fecha_creacion')

    context = {
        "total_boletos_comprados": tickets_comprados.count(),
        "total_boletos_transferidos": tickets_transferidos.count(),
        "total_gasto": tickets_comprados.aggregate(gasto=Sum("evento__precio"))["gasto"] or 0,
        "tickets_comprados": tickets_comprados,
        "tickets_transferidos": tickets_transferidos,
        "incidencias": incidencias,
    }
    return render(request, "eventos/panel_asistente.html", context)



#Para asistentes que quieren ver todos los eventos agregarlos a favoritos y comprar boletos
def eventos_disponibles(request):
    eventos = Evento.objects.all().order_by('-fecha')
    return render(request, 'eventos/eventos_disponibles.html', {'eventos': eventos})

@solo_asistentes
def detalle_evento_asistente(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    return render(request, 'eventos/detalle_eventoA.html', {
        'evento': evento,
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
        })

@solo_asistentes
def evento_favorito(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)

    # Solo asistentes pueden marcar favoritos
    if request.user.rol != "asistente":
        return HttpResponseForbidden("Solo los asistentes pueden guardar favoritos.")

    favorito, created = EventoFavorito.objects.get_or_create(
        usuario=request.user,
        evento=evento
    )
    return redirect("eventos_disponibles")

@solo_asistentes
def eliminar_favorito(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)

    favorito = EventoFavorito.objects.filter(usuario=request.user, evento=evento).first()
    if favorito:
        favorito.delete()

    return redirect("mis_favoritos")


@solo_asistentes
def mis_favoritos(request):
    favoritos = EventoFavorito.objects.filter(usuario=request.user)
    return render(request, "eventos/mis_favoritos.html", {"favoritos": favoritos})


@solo_asistentes
def mis_tickets(request):
    # Incluimos:
    # - Tickets que pertenecen al usuario actual
    # - Tickets que le fueron transferidos
    # - Tickets que él mismo transfirió (para que los vea como transferidos)
    tickets = Ticket.objects.filter(
        Q(usuario=request.user) | Q(transferido_a=request.user) | Q(transferido_por=request.user)
    ).select_related("evento")

    success = request.GET.get("success") == "1"

    eventos_dict = {}
    for ticket in tickets:
        evento = ticket.evento
        if evento.id not in eventos_dict:
            eventos_dict[evento.id] = {
                "evento": evento,
                "tickets": [],
                "conteo": {
                    "activo": 0,
                    "usado": 0,
                    "expirado": 0,
                    "transferido": 0,
                },
            }

        # 👇 Lógica de conteo ajustada
        if ticket.transferido_a == request.user:
            # El receptor lo ve como activo
            eventos_dict[evento.id]["conteo"]["activo"] += 1
        elif ticket.transferido_por == request.user and ticket.estado == "transferido":
            # El comprador original lo ve como transferido
            eventos_dict[evento.id]["conteo"]["transferido"] += 1
        else:
            # Para otros estados (activo, usado, expirado)
            eventos_dict[evento.id]["conteo"][ticket.estado] += 1

        # Agregar el ticket a la lista del evento
        eventos_dict[evento.id]["tickets"].append(ticket)

    return render(
        request,
        "tickets/mis_tickets.html",
        {
            "eventos_dict": eventos_dict,
            "success": success,
        },
    )
    


@solo_asistentes
def transferir_ticket_usuario(request, ticket_id):
    ticket = get_object_or_404(Ticket, Q(id=ticket_id) & (Q(usuario=request.user) | Q(transferido_a=request.user)))

    if request.method == "POST":
        username = request.POST.get("username")
        nuevo_usuario = Usuario.objects.filter(username=username, rol="asistente").first()

        if not nuevo_usuario:
            return JsonResponse({"status": "error", "message": f"No existe un usuario Fiestapp con username '{username}'"})

        try:
            ticket.transferir_a_usuario(nuevo_usuario)
            return JsonResponse({"status": "success", "message": f"Ticket transferido a {nuevo_usuario.username}"})
        except ValueError as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Método no permitido"})



@solo_asistentes
def transferir_ticket_correo(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, usuario=request.user)

    if request.method == "POST":
        email = request.POST.get("email")

        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({"status": "error", "message": f"El correo '{email}' no es válido."})

        try:
            ticket.transferir_por_correo(email)
            return JsonResponse({"status": "success", "message": f"Ticket enviado correctamente al correo {email}."})
        except ValueError as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Método no permitido"})




@solo_organizadores
def panel_organizador(request):
    """Panel principal para organizadores: muestra eventos creados por el usuario y métricas financieras."""
    eventos = Evento.objects.filter(organizador=request.user).order_by("-fecha")

    # Total de boletos emitidos (tickets individuales)
    total_boletos = Ticket.objects.filter(evento__organizador=request.user).count()

    # Asistentes confirmados (activos + transferidos + usados)
    boletos_confirmados = Ticket.objects.filter(
        evento__organizador=request.user,
        estado__in=["activo", "transferido", "usado"]
    ).count()

    # Ganancia actual: precio del evento × tickets confirmados
    tickets_confirmados = Ticket.objects.filter(
        evento__organizador=request.user,
        estado__in=["activo", "transferido", "usado"]
    )
    ganancia_actual = float(sum(t.evento.precio for t in tickets_confirmados))
    ganancia_potencial = float(sum((e.cupo_maximo or 0) * (e.precio or 0) for e in eventos))


    context = {
        "eventos": eventos,
        "total_boletos": total_boletos,
        "boletos_confirmados": boletos_confirmados,
        "ganancia_actual": ganancia_actual,
        "ganancia_potencial": ganancia_potencial,
    }
    return render(request, "eventos/panel_organizador.html", context)



@solo_organizadores
def ver_asistentes(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    tickets = evento.tickets.select_related("usuario")  # todos los tickets del evento

    context = {
        "evento": evento,
        "tickets": tickets
    }
    return render(request, "eventos/ver_asistentes.html", context)

#Vista de Mis Eventos como Organizador
@solo_organizadores
def mis_eventos(request):
    eventos = Evento.objects.filter(organizador=request.user).order_by('-fecha')
    return render(request, 'eventos/mis_eventosO.html', {'eventos': eventos})

#Vista de detalle de evento 
@solo_organizadores
def detalle_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)

    # Tickets individuales (aforo real)
    tickets = Ticket.objects.filter(evento=evento).select_related("usuario", "boleto")

    tickets_vendidos = tickets.count()
    boletos_disponibles = max(evento.cupo_maximo - tickets_vendidos, 0)
    ingresos_totales = tickets_vendidos * evento.precio

    porcentaje_vendido = 0
    if evento.cupo_maximo > 0:
        porcentaje_vendido = int((tickets_vendidos / evento.cupo_maximo) * 100)

    return render(request, 'eventos/detalle_eventoO.html', {
        "evento": evento,
        "tickets": tickets,  # para listar compradores en el template
        "boletos_vendidos": tickets_vendidos,
        "boletos_disponibles": boletos_disponibles,
        "porcentaje_vendido": porcentaje_vendido,
        "ingresos_totales": ingresos_totales,
    })
    
    
#Eliminar los eventos creados
@solo_organizadores
def eliminar_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id, organizador=request.user)
    if request.method == 'POST':
        evento.delete()
        messages.success(request, 'Evento eliminado correctamente.')
        return redirect('mis_eventos')
    return render(request, 'eventos/eliminacion_evento.html', {'evento': evento})

#view para crear eventos
@solo_organizadores
def create_event_view(request):
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)
        print("Método:", request.method)
        print("Datos POST:", request.POST)
        print("Archivos:", request.FILES)
        print("Formulario válido:", form.is_valid())
        print("Errores:", form.errors)
        if form.is_valid():
            nuevo_evento = form.save(commit=False)
            nuevo_evento.organizador = request.user

            print("Evento creado:", nuevo_evento.titulo)
            print("Organizador asignado:", nuevo_evento.organizador)
            print("Rol del usuario:", getattr(request.user, 'rol', 'sin rol'))

            nuevo_evento.save()
            return redirect('mis_eventos')
    else:
        form = EventoForm()
    return render(request, 'eventos/create_event.html', {'form': form})

@solo_organizadores
#edita eventos directo sin forms.py
@solo_organizadores
def editar_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)

    if request.method == "POST":
        evento.titulo = request.POST.get("titulo")
        evento.descripcion = request.POST.get("descripcion")
        evento.fecha = request.POST.get("fecha")
        evento.lugar = request.POST.get("lugar")
        evento.cupo_maximo = request.POST.get("cupo_maximo")

        precio = request.POST.get("precio")
        if precio:
            evento.precio = Decimal(precio)

        if "imagen" in request.FILES:
            evento.imagen = request.FILES["imagen"]

        evento.save()
        messages.success(request, "✅ Evento actualizado correctamente.")
        # Redirige a detalle_evento (o ajusta según tu flujo)
        return redirect("detalle_evento", evento_id=evento.id)

    return render(request, "eventos/editar_evento.html", {"evento": evento}
    )

# --- DUNCIONES DE ADMINISTRADOR ---
# --- Panel Administrador ---
@solo_administradores
def panel_administrador(request):
    """
    Panel principal del administrador.
    Muestra métricas globales de usuarios, eventos, boletos e incidencias.
    """

    # Usuarios por rol
    total_usuarios = Usuario.objects.count()
    total_organizadores = Usuario.objects.filter(rol="organizador").count()
    total_asistentes = Usuario.objects.filter(rol="asistente").count()
    total_soporte = Usuario.objects.filter(rol="soporte").count()
    total_admins = Usuario.objects.filter(rol="administrador").count()

    # Eventos
    total_eventos = Evento.objects.count()
    eventos_activos = Evento.objects.filter(fecha__gte=timezone.now()).count()
    eventos_pasados = Evento.objects.filter(fecha__lt=timezone.now()).count()

    # Boletos vendidos (sumar cantidad de cada boleto)
    boletos_vendidos = Boleto.objects.aggregate(total=Sum("cantidad"))["total"] or 0

    # Incidencias
    incidencias_resueltas = Incidencia.objects.filter(estado="resuelto").count()
    incidencias_pendientes = Incidencia.objects.filter(estado="pendiente").count()
    incidencias_proceso = Incidencia.objects.filter(estado="proceso").count()

    context = {
        # Usuarios
        "total_usuarios": total_usuarios,
        "total_organizadores": total_organizadores,
        "total_asistentes": total_asistentes,
        "total_soporte": total_soporte,
        "total_admins": total_admins,

        # Eventos
        "total_eventos": total_eventos,
        "eventos_activos": eventos_activos,
        "eventos_pasados": eventos_pasados,

        # Boletos
        "boletos_vendidos": boletos_vendidos,

        # Incidencias
        "incidencias_resueltas": incidencias_resueltas,
        "incidencias_pendientes": incidencias_pendientes,
        "incidencias_proceso": incidencias_proceso,
    }
    return render(request, "eventos/panel_administrador.html", context)


# --- Panel Administrador 
@solo_administradores
def gestionar_usuarios(request):
    """
    Vista para que el administrador gestione usuarios.
    Muestra todos los usuarios registrados con sus roles,
    además de contar tickets y eventos para mostrar advertencias en el modal.
    """
    usuarios = Usuario.objects.all().order_by("-date_joined")

    usuarios_info = []
    for u in usuarios:
        info = {
            "usuario": u,
            # si el usuario es asistente, contar sus boletos/tickets
            "tickets_count": u.boletos.count() if hasattr(u, "boletos") else 0,
            # si el usuario es organizador, contar sus eventos
            "eventos_count": u.eventos.count(),
        }
        usuarios_info.append(info)

    context = {
        "usuarios_info": usuarios_info,
    }
    return render(request, "eventos/gestionar_usuarios.html", context)



@solo_administradores
def gestionar_eventos(request):
    """
    Vista para que el administrador gestione eventos.
    Muestra todos los eventos creados en el sistema.
    """
    eventos = Evento.objects.all().order_by("-fecha")
    now = timezone.now()  # 👈 se pasa al contexto

    context = {
        "eventos": eventos,
        "now": now,
    }
    return render(request, "eventos/gestionar_eventos.html", context)


@solo_administradores
def eliminar_usuario(request, usuario_id):
    """
    Vista para que el administrador elimine un usuario del sistema.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)

    # Opcional: evitar que un admin se elimine a sí mismo
    if usuario == request.user:
        messages.error(request, "No puedes eliminar tu propia cuenta.")
        return redirect("gestionar_usuarios")

    if request.method == "POST":
        usuario.delete()
        messages.success(request, f"Usuario {usuario.username} eliminado correctamente.")
        return redirect("gestionar_usuarios")

    return render(request, "eventos/eliminacion_usuario.html", {"usuario": usuario})

@solo_administradores
def eliminar_evento_admin(request, evento_id):
    """
    Vista para que el administrador elimine cualquier evento del sistema.
    """
    evento = get_object_or_404(Evento, id=evento_id)

    if request.method == "POST":
        evento.delete()
        messages.success(request, f"Evento '{evento.titulo}' eliminado correctamente.")
        return redirect("gestionar_eventos")

    # Si quieres evitar un template de confirmación, puedes redirigir directo
    return redirect("gestionar_eventos")



#TODAS LAS FUNCIONES DE DESARROLLADOR.
# --- Panel Desarrollador ---
@solo_desarrolladores
def panel_desarrollador(request):
    # Estado real de servicios externos
    estado_pagos = check_stripe()
    estado_correo = check_smtp()

    # Logs reales: lee las últimas 20 líneas del archivo configurado en settings.py
    try:
        log_path = settings.BASE_DIR / "logs/django.log"
        with open(log_path, "r", encoding="utf-8") as f:
            logs = "".join(f.readlines()[-20:])
    except Exception:
        logs = "No se pudieron leer los logs."

    # Incidencias técnicas (si tienes un modelo Incidencia)
    incidencias = Incidencia.objects.filter(estado="abierta")

    context = {
        "estado_pagos": estado_pagos,
        "estado_correo": estado_correo,
        "logs": logs,
        "incidencias": incidencias,
    }
    return render(request, "eventos/panel_desarrollador.html", context)


def check_stripe():
    try:
        # Intentamos obtener el balance de Stripe con la clave configurada en settings.py
        stripe.Balance.retrieve()
        return "Operativo ✅"
    except Exception as e:
        return f"Error ❌ ({str(e)})"

def check_smtp():
    try:
        # Usamos la configuración de correo definida en settings.py
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
        if settings.EMAIL_USE_TLS:
            server.starttls()
        if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.quit()
        return "Conectado ✅"
    except Exception as e:
        return f"Error ❌ ({str(e)})"


@solo_desarrolladores
def logs_view(request):
    log_entries = []
    log_path = settings.BASE_DIR / "logs/django.log"

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()[-50:]  # últimas 50 líneas
            for line in lines:
                # Ejemplo de línea: "2025-12-12 18:30:00,123 INFO django.request: GET /home/ 200"
                match = re.match(r"^(?P<fecha>\S+\s+\S+)\s+(?P<nivel>\w+)\s+(?P<mensaje>.+)$", line.strip())
                if match:
                    log_entries.append({
                        "fecha": match.group("fecha"),
                        "nivel": match.group("nivel"),
                        "mensaje": match.group("mensaje"),
                    })
                else:
                    # Si no coincide con el patrón, lo guardamos como mensaje plano
                    log_entries.append({
                        "fecha": "",
                        "nivel": "INFO",
                        "mensaje": line.strip(),
                    })
    except Exception:
        log_entries = [{"fecha": "", "nivel": "ERROR", "mensaje": "No se pudieron leer los logs."}]

    return render(request, "eventos/logs.html", {"logs": log_entries})



@solo_desarrolladores
def api_docs(request):
    """
    Documentación real de la API basada en las views existentes.
    """

    endpoints = [

        # --- ORGANIZADORES ---
        {
            "path": "/mis-eventos/",
            "method": "GET",
            "desc": "Lista los eventos creados por el organizador autenticado.",
            "example": "curl -X GET http://localhost:8000/mis-eventos/"
        },
        {
            "path": "/eventos/crear/",
            "method": "POST",
            "desc": "Crea un nuevo evento (solo organizadores).",
            "example": """curl -X POST http://localhost:8000/eventos/crear/ \
  -F "titulo=Concierto" \
  -F "descripcion=Rock en vivo" \
  -F "fecha=2025-12-20" \
  -F "lugar=Auditorio" \
  -F "cupo_maximo=200" \
  -F "precio=500" \
  -F "imagen=@imagen.jpg"
"""
        },
        {
            "path": "/eventos/<id>/editar/",
            "method": "POST",
            "desc": "Edita un evento existente del organizador.",
            "example": """curl -X POST http://localhost:8000/eventos/5/editar/ \
  -F "titulo=Nuevo título" """
        },
        {
            "path": "/eventos/<id>/eliminar/",
            "method": "POST",
            "desc": "Elimina un evento creado por el organizador.",
            "example": "curl -X POST http://localhost:8000/eventos/5/eliminar/"
        },

        # --- ADMINISTRADOR ---
        {
            "path": "/admin/panel/",
            "method": "GET",
            "desc": "Panel principal del administrador con métricas globales.",
            "example": "curl -X GET http://localhost:8000/admin/panel/"
        },
        {
            "path": "/admin/usuarios/",
            "method": "GET",
            "desc": "Lista todos los usuarios registrados.",
            "example": "curl -X GET http://localhost:8000/admin/usuarios/"
        },
        {
            "path": "/admin/usuarios/<id>/eliminar/",
            "method": "POST",
            "desc": "Elimina un usuario del sistema.",
            "example": "curl -X POST http://localhost:8000/admin/usuarios/10/eliminar/"
        },
        {
            "path": "/admin/eventos/",
            "method": "GET",
            "desc": "Lista todos los eventos del sistema.",
            "example": "curl -X GET http://localhost:8000/admin/eventos/"
        },
        {
            "path": "/admin/eventos/<id>/eliminar/",
            "method": "POST",
            "desc": "Elimina cualquier evento del sistema.",
            "example": "curl -X POST http://localhost:8000/admin/eventos/5/eliminar/"
        },

        # --- DESARROLLADOR ---
        {
            "path": "/dev/panel/",
            "method": "GET",
            "desc": "Panel del desarrollador: estado de servicios, logs, incidencias.",
            "example": "curl -X GET http://localhost:8000/dev/panel/"
        },
        {
            "path": "/dev/api-docs/",
            "method": "GET",
            "desc": "Documentación técnica de la API.",
            "example": "curl -X GET http://localhost:8000/dev/api-docs/"
        },

        # --- INCIDENCIAS (si existen en tu modelo) ---
        {
            "path": "/incidencias/",
            "method": "GET",
            "desc": "Lista incidencias del usuario o del sistema.",
            "example": "curl -X GET http://localhost:8000/incidencias/"
        },

        # --- BOLETOS (si tu modelo Boleto existe) ---
        {
            "path": "/boletos/comprar/",
            "method": "POST",
            "desc": "Compra boletos para un evento.",
            "example": """curl -X POST http://localhost:8000/boletos/comprar/ \
  -H "Content-Type: application/json" \
  -d '{"evento_id":1, "cantidad":2}'"""
        },
    ]

    return render(request, "eventos/api_docs.html", {"endpoints": endpoints})


#TODAS LAS FUNCIONES DE SOPORTE
# --- Panel Soporte ---
@solo_soporte
def panel_soporte(request):
    """
    Panel principal del soporte.
    Aquí puede ver las incidencias pendientes levantadas por usuarios.
    """
    incidencias_soporte = Incidencia.objects.filter(estado="pendiente").order_by("-fecha_creacion")
    context = {
        "incidencias_soporte": incidencias_soporte,
    }
    return render(request, "eventos/panel_soporte.html", context)


#crear 
@login_required
def crear_incidencia(request):
    if request.method == 'POST':
        form = IncidenciaForm(request.POST)
        if form.is_valid():
            incidencia = form.save(commit=False)
            incidencia.usuario = request.user
            incidencia.save()
            messages.success(request, 'Incidencia creada exitosamente.')

            # Redirigir solo si el usuario es asistente, organizador o administrador
            if request.user.rol == 'asistente':
                return redirect('panel_asistente')
            elif request.user.rol == 'organizador':
                return redirect('panel_organizador')
            elif request.user.rol == 'administrador':
                return redirect('panel_administrador')
            else:
                messages.error(request, 'Tu rol no tiene permiso para levantar incidencias.')
                return redirect('no_autorizado')
    else:
        form = IncidenciaForm()

    return render(request, 'tickets/crear_incidencia.html', {'form': form})

@solo_soporte
def resolver_incidencia(request, incidencia_id):
    incidencia = get_object_or_404(Incidencia, id=incidencia_id)

    if request.method == "POST":
        nueva_respuesta = request.POST.get("respuesta")
        nuevo_estado = request.POST.get("estado", "resuelto")

        incidencia.respuesta = nueva_respuesta
        incidencia.estado = nuevo_estado
        incidencia.asignado_a = request.user  # el agente que la atendió
        incidencia.save()

        # Aquí podrías enviar un correo al usuario que la levantó
        # send_mail("Tu incidencia fue atendida", nueva_respuesta, "soporte@tuapp.com", [incidencia.usuario.email])

        messages.success(request, "La incidencia fue actualizada correctamente.")
        return redirect("panel_soporte")

    return render(request, "eventos/resolver_incidencia.html", {"incidencia": incidencia})


#Frecuent Questions
def faq(request):
    return render(request, "eventos/faq.html")



#Vista para usuario no autorizado
def no_autorizado(request):
    return HttpResponse(" No tienes permiso para acceder a esta vista.", status=403)





@csrf_exempt
@require_POST
@login_required
def create_payment_intent(request, evento_id):
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
        cantidad = int(payload.get("cantidad", 1))

        if cantidad < 1:
            return JsonResponse({"error": "Cantidad inválida."}, status=400)

        evento = get_object_or_404(Evento, id=evento_id)

        if cantidad > evento.boletos_disponibles():
            return JsonResponse({"error": "No hay boletos suficientes."}, status=400)

        total_amount_cents = int(float(evento.precio) * cantidad * 100)

        intent = stripe.PaymentIntent.create(
            amount=total_amount_cents,
            currency="mxn",
            payment_method_types=["card", "oxxo"],
            description=f"{evento.titulo} x{cantidad}",
            metadata={
                "evento_id": str(evento.id),
                "comprador_id": str(request.user.id),
                "cantidad": str(cantidad),
            },
        )

        return JsonResponse({
            "clientSecret": intent.client_secret,
            "amount": total_amount_cents,
            "currency": "mxn",
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    
    

@csrf_exempt
def stripe_webhook(request):
    payload = request.body.decode("utf-8")
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        print("❌ Payload inválido")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        print("❌ Firma inválida en webhook de Stripe")
        return HttpResponse(status=400)

    print(f"📩 Evento recibido: {event['type']}")

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]

        try:
            evento_id = int(intent["metadata"].get("evento_id"))
            comprador_id = int(intent["metadata"].get("comprador_id"))
            cantidad = int(intent["metadata"].get("cantidad", 1))

            evento = Evento.objects.get(id=evento_id)
            comprador = Usuario.objects.get(id=comprador_id)

            # Crear el boleto con la cantidad comprada
            boleto = Boleto.objects.create(
                evento=evento,
                comprador=comprador,
                cantidad=cantidad,
            )

            print(f"✅ Boleto creado: {boleto} con {cantidad} tickets")

            # El modelo Boleto.save() ya genera los tickets (N tickets con QR)

        except Evento.DoesNotExist:
            print(f"❌ Evento con id {evento_id} no existe")
        except Usuario.DoesNotExist:
            print(f"❌ Usuario con id {comprador_id} no existe")
        except Exception as e:
            print(f"❌ Error creando boleto: {e}")

    elif event["type"] == "payment_intent.processing":
        intent = event["data"]["object"]
        print(f"⏳ Pago OXXO en proceso para PaymentIntent {intent['id']}")

    elif event["type"] == "payment_intent.payment_failed":
        intent = event["data"]["object"]
        print(f"⚠️ Pago fallido para PaymentIntent {intent['id']}")

    elif event["type"] == "payment_intent.canceled":
        intent = event["data"]["object"]
        print(f"⚠️ PaymentIntent cancelado {intent['id']}")

    return HttpResponse(status=200)









@login_required
def buscar_evento(request):
    query = request.GET.get("q")
    resultados = Evento.objects.filter(
        Q(titulo__icontains=query) |
        Q(lugar__icontains=query) |
        Q(descripcion__icontains=query)
    ) if query else []

    # Detectar rol del usuario
    if request.user.groups.filter(name__in=["Administrador", "Soporte", "Desarrollador"]).exists():
        # Solo ver información, sin compra
        template = "eventos/buscar_evento_info.html"
    else:
        # Organizador/Asistente con compra habilitada
        template = "eventos/buscar_evento.html"

    return render(request, template, {"resultados": resultados})






def como_usar_fiestapp(request):
    # Lista de videos locales en static/videos/
    tutoriales = [
        {
            "titulo": "¿Qué puede hacer un asistente?",
            "archivo": "videos/VIDEO ASISTENTE.mp4",
            "descripcion": "Aquí te enseño a registrarte como asistente y cómo participar en un evento."
        },
        {
            "titulo": "¿Qué puede hacer un organizador?",
            "archivo": "videos/VIDEO ORGANIZADOR.mp4",
            "descripcion": "Aquí aprendes a registrarte como organizador, poner tu casa, la fecha y el costo del boleto para empezar la pachanga."
        },
    ]
    return render(request, "guawolin/como_usar.html", {"tutoriales": tutoriales})