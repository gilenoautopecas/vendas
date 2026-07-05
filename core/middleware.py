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
        if request.user.is_authenticated or request.path_info.startswith(ROTAS_PUBLICAS):
            # Redireciona para o wizard se o usuário não tem empresa vinculada
            if (
                request.user.is_authenticated
                and not request.user.is_superuser
                and not request.path_info.startswith(ROTAS_PUBLICAS)
                and request.path_info != "/configurar/"
            ):
                try:
                    request.user.perfil
                except Exception:
                    from django.shortcuts import redirect
                    return redirect("setup_empresa")

            return self.get_response(request)

        return redirect_to_login(request.get_full_path(), login_url=settings.LOGIN_URL)
