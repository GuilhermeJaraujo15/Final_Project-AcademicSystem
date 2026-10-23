from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from apps.academics.views import dashboard

if settings.DEMO_MODE:
    urlpatterns = [path("", include("apps.preview.urls"))]
else:
    urlpatterns = [
        path("admin/", admin.site.urls),
        path("", dashboard, name="dashboard"),
        path("accounts/login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
        path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
        path("api/v1/", include("apps.academics.api_urls")),
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    ]
