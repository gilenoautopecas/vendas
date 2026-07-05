from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import render

from .licenca_check import verificar_licenca

ROTAS_PUBLICAS = (
    "/admin/",
    "/login/",
    "/core/sync-produtos/",
    "/static/",
    "/licenca-expirada/",
    "/configurar/",
)


class LicencaMiddleware:
    """Bloqueia o acesso se a licença estiver ausente ou expirada."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path_info.startswith(ROTAS_PUBLICAS):
            return self.get_response(request)

        resultado = verificar_licenca()
        if not resultado.valida:
            return render(request, "core/licenca_expirada.html", {
                "motivo": resultado.motivo,
            }, status=403)

        return self.get_response(request)


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.shortcuts import redirect

        # Rotas públicas passam direto
        if request.path_info.startswith(ROTAS_PUBLICAS):
            return self.get_response(request)

        # Não autenticado → vai pro login
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), login_url=settings.LOGIN_URL)

        # Superuser não precisa de empresa vinculada
        if request.user.is_superuser:
            return self.get_response(request)

        # Usuário sem empresa → wizard de configuração
        from .models import PerfilUsuario
        if not PerfilUsuario.objects.filter(user=request.user).exists():
            return redirect("setup_empresa")

        return self.get_response(request)
