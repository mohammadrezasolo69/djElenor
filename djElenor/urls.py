from django.contrib import admin
from django.urls import include, path

from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

urlpatterns_apps = []

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", csrf_exempt(GraphQLView.as_view(graphiql=True)), name="api"),

    path('', include(urlpatterns_apps)),

]

# ------------------------------------------ Config Static ----------------------------------------------------------
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
