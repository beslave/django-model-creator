from django.conf.urls import url
from .views import DynamicModelView


urlpatterns = [
    url(r'^$', DynamicModelView.as_view(), name='dynamic_model'),
    url(
        r'^(?P<model_name>[a-zA-Z0-9_]+)/$',
        DynamicModelView.as_view(),
        name='dynamic_model'
    ),
]
