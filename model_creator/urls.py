from django.conf.urls import url

from .views import ImportModelTemplateView


urlpatterns = [
    url(
        r'^admin/modeltemplate/import$',
        ImportModelTemplateView.as_view(),
        name='import_model_template'
    ),
]
