from django.conf import settings
from django.contrib.auth.views import redirect_to_login

ROTAS_PUBLICAS = (
    "/admin/",
    "/login/",
    "/core/sync-produtos/",
    "/static/",
)


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated or request.path_info.startswith(ROTAS_PUBLICAS):
            return self.get_response(request)

        return redirect_to_login(request.get_full_path(), login_url=settings.LOGIN_URL)
