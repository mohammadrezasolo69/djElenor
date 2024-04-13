from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, re_path, path

from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

urlpatterns = [
                  path('', include('djElenor.account.urls')),
                  path('admin/', admin.site.urls),
                  re_path(
                      r"^graphql/$",
                      csrf_exempt(GraphQLView.as_view(graphiql=True)),
                      name="api",
                  ),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
