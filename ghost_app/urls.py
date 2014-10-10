from django.conf.urls import url
from .views import DynamicModelView, DeleteDynamicModelObjectView


urlpatterns = [
    url(r'^$', DynamicModelView.as_view(), name='dynamic_model'),
    url(
        r'^(?P<model_name>[a-zA-Z0-9_]+)/$',
        DynamicModelView.as_view(),
        name='dynamic_model'
    ),
    url(
        r'^(?P<model>[a-zA-Z0-9_]+)/(?P<object_id>\d+)/delete$',
        DeleteDynamicModelObjectView.as_view(),
        name='delete_dynamic_model_object'
    ),
]
