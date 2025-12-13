from django.urls import path
from . import views


urlpatterns = [
    # --- Rutas generales ---
    path("buscar/", views.buscar_evento, name="buscar_evento"),
    path("reportes/", views.reports, name="reports"),
    path("no-autorizado/", views.no_autorizado, name="no_autorizado"),

    # --- Asistente ---
    path("registro-asistente/", views.registerAssistant, name="register_assistant"),
    path("asistente/", views.panel_asistente, name="panel_asistente"),
    path("asistente/eventos/", views.eventos_disponibles, name="eventos_disponibles"),
    path("asistente/evento/<int:evento_id>/", views.detalle_evento_asistente, name="detalle_evento_asistente"),
    path("asistente/tickets/", views.mis_tickets, name="mis_tickets"),
    path("asistente/favoritos/", views.mis_favoritos, name="mis_favoritos"),
    path("asistente/evento/<int:evento_id>/favorito/", views.evento_favorito, name="evento_favorito"),
    path("asistente/favoritos/eliminar/<int:evento_id>/", views.eliminar_favorito, name="eliminar_favorito"),
    path("<int:ticket_id>/transferir_usuario/", views.transferir_ticket_usuario, name="transferir_ticket_usuario"),
    path("<int:ticket_id>/transferir_correo/", views.transferir_ticket_correo, name="transferir_ticket_correo"),

    # --- Organizador ---
    path("registro-organizador/", views.registerOrganizer, name="register_organizer"),
    path("organizador/", views.panel_organizador, name="panel_organizador"),
    path("organizador/eventos/", views.mis_eventos, name="mis_eventos"),
    path("organizador/evento/crear/", views.create_event_view, name="crear_evento"),
    path("organizador/evento/<int:evento_id>/", views.detalle_evento, name="detalle_evento"),
    path("organizador/evento/<int:evento_id>/asistentes/", views.ver_asistentes, name="ver_asistentes"),
    path("organizador/evento/<int:evento_id>/eliminar/", views.eliminar_evento, name="eliminar_evento"),
    path("organizador/evento/<int:evento_id>/editar/", views.editar_evento, name="editar_evento"),

    # --- Stripe / Pagos ---
    path("stripe/webhook/", views.stripe_webhook, name="stripe_webhook"),
    path("asistente/comprar-ticket/<int:evento_id>/create-payment-intent/", views.create_payment_intent, name="create_payment_intent"),

    # --- Administrador ---
    path("admin/", views.panel_administrador, name="panel_administrador"),
    path("registro-administrador/", views.registerAdmin, name="register_administrator"),
    path("admin/usuarios/", views.gestionar_usuarios, name="gestionar_usuarios"),
    path("admin/usuarios/<int:usuario_id>/eliminar/", views.eliminar_usuario, name="eliminar_usuario"),
    path("admin/eventos/", views.gestionar_eventos, name="gestionar_eventos"),
    path("admin/eventos/<int:evento_id>/eliminar/", views.eliminar_evento_admin, name="eliminar_evento_admin"),

    # --- Desarrollador ---
    path("dev/", views.panel_desarrollador, name="panel_desarrollador"),
    path("registro-dev/", views.registerDev, name="register_developer"),
    path("logs/", views.logs_view, name="logs"),
    path("api-docs/", views.api_docs, name="api_docs"),

    # --- Soporte ---
    path("soporte/", views.panel_soporte, name="panel_soporte"),
    path("registro-soporte/", views.registerSoporte, name="register_soporte"),
    path("soporte/incidencia/crear/", views.crear_incidencia, name="crear_incidencia"),
    path("soporte/incidencia/<int:incidencia_id>/resolver/", views.resolver_incidencia, name="resolver_incidencia"),
    path("faq/", views.faq, name="faq"),

]
