from django.views.generic import TemplateView
from model_creator.models import DynamicModel


class DynamicModelView(TemplateView):

    APP_LABEL = 'ghost_app'
    template_name = 'ghost_app/dynamic_model.html'

    def get_context_data(self, model_name=None, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        model_list = DynamicModel.all_models()[self.APP_LABEL]
        if model_name is None:
            model_name = model_list[0].__name__.lower() if model_list else None
        model = DynamicModel.get_model(self.APP_LABEL, model_name)

        model_objects = model.objects.all() if model else []

        context.update({
            'models_list': model_list,
            'model': model,
            'model_objects': model_objects
        })
        return context
