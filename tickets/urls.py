from django.urls import path
from . import views
from django.http import HttpResponse

urlpatterns = [
    path('registro-asistente/', views.registerAssistant, name='register_assistant'),
    path('registro-organizador/', views.registerOrganizer, name='register_organizer'),
    path("mis-tickets/", views.mis_tickets, name="mis_tickets"),         # Asistente
    path('mis_eventos/', views.my_events, name='my_events'),
    path('eventos/', views.events, name='events'),           # Organizador
    path('reportes/', views.reports, name='reports'), 
    path('panel/organizador/crear/', views.create_event_view, name='crear_evento'), #Vista de crear evento 
    path('no-autorizado/', views.no_autorizado, name='no_autorizado'), # Vista no autorizado
    path('panel/organizador/', views.panel_organizador, name='panel_organizador'), #Panel Organizador
    path('panel/asistente/', views.panel_asistente, name='panel_asistente'), #Panel Asistente
    path('panel/asistente/mis-boletos/', views.mis_boletos, name='mis_boletos'), #Boletos del usuario
    path('panel/organizador/mis-eventos/', views.mis_eventos, name='my_events'), #Mis Eventos
    path('panel/organizador/evento/<int:evento_id>/', views.detalle_evento, name='detalle_evento'), #Detalle de evento
    path('panel/organizador/evento/<int:evento_id>/eliminar/', views.eliminar_evento, name='eliminar_evento'), #eliminación de eventos
    path('panel/asistente/eventos/', views.eventos_disponibles, name='eventos_disponibles'), #Vista Eventos asistente
    path('eventos/<int:evento_id>/comprar/', views.comprar_boleto, name='comprar_boleto'), #compra de boletos
    path("buscar/", views.buscar_evento, name="buscar_evento"), #Buscar Evento
    path("sboleto/<int:boleto_id>/", views.boleto_detalle, name="boleto_detalle"),
]
