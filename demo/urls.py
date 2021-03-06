from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

import ghost_app.urls
import model_creator.urls


urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(
        r'^model_creator/',
        include(model_creator.urls, namespace='model_creator')
    ),
    url(r'^', include(ghost_app.urls))
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
