from urllib import request
from django.shortcuts import render,redirect
from . models import Ticket, Usuario
from django.contrib import messages
from django.shortcuts import render
from .forms import RegisterAssistantForm, RegisterOrganizerForm
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from tickets import views
from tickets.forms import EventoForm
from .models import Evento
from django.http import HttpResponse
from tickets.decoradores import solo_organizadores
from tickets.decoradores import solo_asistentes
from django.shortcuts import get_object_or_404 #detalle de evento
from django.contrib import messages #eliminar eventos
from django.db.models import Q
from .models import Evento, Ticket
from django.utils import timezone
from .models import Evento, Boleto
import re


def es_organizador_o_asistente(user):
    return user.is_authenticated and (user.rol == "organizador" or user.rol == "asistente")

def home(request):
    return render(request, 'guawolin/home.html')

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



#view para la configuracion del perfil
def profile_settings(request):
    return render(request, 'tickets/profile_settings.html')

#view para mis_eventos
@login_required
def my_events(request):
    if request.user.rol != 'organizador':
        return redirect('home')
    return render(request, 'tickets/mis_eventos.html')

#view para reportes
@login_required
def reports(request):
    if request.user.rol != 'organizador':
        return redirect('home')
    return render(request, 'tickets/reportes.html')

@login_required
def mis_tickets(request):
    boletos = request.user.boletos.all()  # 👈 ahora sí funciona
    return render(request, "tickets/mis_tickets.html", {"boletos": boletos})

def events(request):
    return render(request, 'tickets/eventos.html')

def logout_view(request):
    logout(request)
    return redirect('home')  # ✅ Asegúrate de que 'home' esté definida en urls.py
  

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
            return redirect('my_events')
    else:
        form = EventoForm()
    return render(request, 'eventos/create_event.html', {'form': form})


#Vista para el panel asistentes
@solo_asistentes
def panel_asistente(request):
    eventos = Evento.objects.filter(fecha__gte=timezone.now()).order_by('fecha')
    return render(request, "eventos/panel_asistente.html", {"eventos": eventos})

#Vista para el panel organizador
@solo_organizadores
def panel_organizador(request):
    eventos = Evento.objects.filter(organizador=request.user).order_by('-fecha')
    return render(request, 'panel_organizador.html', {'eventos': eventos})


#Vista para usuario no autorizado
def no_autorizado(request):
    return HttpResponse(" No tienes permiso para acceder a esta vista.", status=403)

@solo_asistentes
def mis_boletos(request):
    boletos = Ticket.objects.filter(usuario=request.user).select_related('evento').order_by('-fecha_registro')
    return render(request, 'mis_boletos.html', {'boletos': boletos})

#Vista de Mis Eventos 
@solo_organizadores
def mis_eventos(request):
    eventos = Evento.objects.filter(organizador=request.user).order_by('-fecha')
    return render(request, 'eventos/mis_eventos.html', {'eventos': eventos})

#Vista de detalle de evento 
@login_required
def detalle_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    boletos = Boleto.objects.filter(evento=evento)


 # Métricas de boletos
    boletos_vendidos = sum(b.cantidad for b in boletos)  # suma la cantidad de cada compra
    boletos_disponibles = max(evento.cupo_maximo - boletos_vendidos, 0)
    ingresos_totales = boletos_vendidos * evento.precio

 
    porcentaje_vendido = 0
    if evento.cupo_maximo > 0:
        porcentaje_vendido = int((boletos_vendidos / evento.cupo_maximo) * 100)

    return render(request, 'eventos/detalle_evento.html', {
        "evento": evento,
        "boletos": boletos,  #  para listar compradores en el template
        "boletos_vendidos": boletos_vendidos,
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
        return redirect('my_events')
    return render(request, 'eventos/eliminacion_evento.html', {'evento': evento})

#Acceso a los eventos disponibles
@solo_asistentes  
def eventos_disponibles(request):
    eventos = Evento.objects.all().order_by('-fecha')
    return render(request, 'eventos/eventos_disponibles.html', {'eventos': eventos})


#comprar boleto
@login_required
def comprar_boleto(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)

    # 🔢 calcular boletos vendidos y disponibles
    boletos_vendidos = sum(b.cantidad for b in Boleto.objects.filter(evento=evento))
    boletos_disponibles = max(evento.cupo_maximo - boletos_vendidos, 0)

    if request.method == "POST":
        cantidad = int(request.POST.get("cantidad", 1))
        nombre = request.POST.get("nombre")
        email = request.POST.get("email")

        if boletos_vendidos + cantidad > evento.cupo_maximo:
            messages.error(request, "Ya no hay suficientes boletos disponibles para este evento.")
            return redirect("comprar_boleto", evento_id=evento.id)

        boleto = Boleto.objects.create(
            evento=evento,
            comprador=request.user,
            cantidad=cantidad,
            nombre=nombre,
            email=email,
        )

        messages.success(request, "Tu compra se realizó correctamente.")
        return redirect("boleto_detalle", boleto_id=boleto.id)

    return render(request, "tickets/comprar_boleto.html", {
        "evento": evento,
        "boletos_disponibles": boletos_disponibles,
    })


def boleto_detalle(request, boleto_id):
    boleto = get_object_or_404(Boleto, id=boleto_id)
    total = boleto.cantidad * boleto.evento.precio   # cálculo en Python

    qr_url = request.build_absolute_uri(boleto.qr_image.url) if boleto.qr_image else None

    return render(request, "tickets/boleto_detalle.html", {
        "boleto": boleto,
        "total": total,
        "qr_url": qr_url,
    })

@login_required
@user_passes_test(es_organizador_o_asistente)
def buscar_evento(request):
    query = request.GET.get("q")
    resultados = Evento.objects.filter(
        Q(titulo__icontains=query) |
        Q(lugar__icontains=query) |
        Q(descripcion__icontains=query)
    ) if query else []
    return render(request, "eventos/buscar_evento.html", {"resultados": resultados})


@login_required
def reportes_eventos(request):
    return HttpResponse("Hola Julian, la vista funciona ✅")


def convertir_a_embed(url):
    """
    Convierte cualquier URL de YouTube en formato embed.
    Si no se puede, devuelve None.
    """
    patrones = [
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",
        r"youtube\.com/embed/([a-zA-Z0-9_-]{11})"
    ]
    for patron in patrones:
        match = re.search(patron, url)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/embed/{video_id}"
    return None

def como_usar_fiestapp(request):
    # Lista original de videos (raw_videos)
    raw_videos = [
        {
            "titulo": "Cómo registrarse como asistente",
            "url": "https://youtu.be/IWUxc5VZ4lY?si=FnwENm1VL0qth9oO",
            "fallback": "https://www.youtube.com/embed/IWUxc5VZ4lY?si=E_GxpE7r0biyELir",
        },
        {
            "titulo": "Cómo registrarse como organizador",
            "url": "https://youtu.be/s48CH1VQDTo?si=QCOBYJgjdxC-2QBn",
            "fallback": "https://www.youtube.com/embed/s48CH1VQDTo?si=wNQzT0GEjmF80zra",
        },
    ]

    # Convertimos a embed y añadimos fallback
    tutoriales = []
    for video in raw_videos:
        embed_url = convertir_a_embed(video["url"])
        tutoriales.append({
            "titulo": video["titulo"],
            "url": embed_url,
            "fallback": video["url"]
        })

    return render(request, "guawolin/como_usar.html", {"tutoriales": tutoriales})