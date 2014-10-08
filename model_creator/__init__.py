from django.conf import settings as app_settings


__all__ = ('settings',)

default_app_config = 'model_creator.apps.ModelCreatorConfig'

default_settings = {
    # Applications where dynamic models will be created
    'DYNAMIC_APPS': [],
}


class Settings(object):

    def __init__(self):
        for k, v in default_settings.items():
            setattr(
                self, k,
                getattr(app_settings, 'MODEL_CREATOR_{}'.format(k), v)
            )


settings = Settings()
