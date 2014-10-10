from django.forms import ModelForm
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View
from model_creator.models import DynamicModel


APP_LABEL = 'ghost_app'


class DynamicModelView(View):

    template_name = 'ghost_app/dynamic_model.html'

    def dispatch(self, request, model_name=None, *args, **kwargs):
        self.model_name = model_name
        self.model_list = DynamicModel.all_models().get(APP_LABEL, [])

        if self.model_name is None and self.model_list:
            self.model_name = self.model_list[0].__name__.lower()

        self.model = DynamicModel.get_model(
            APP_LABEL,
            self.model_name
        )

        self.form = None

        if self.model:
            form_class = self.model.get_model_form()

            if request.method == 'POST':
                data = {
                    field.name: request.POST.get(field.name)
                    for field in self.model.get_template_fields()
                }
                self.form = form_class(data=data)
                if self.form.is_valid():
                    self.form.save()
                    return redirect(
                        'dynamic_model',
                        model_name=self.model_name
                    )
            else:
                self.form = form_class()

        return render(
            request, self.template_name,
            self.get_context_data(*args, **kwargs)
        )

    def get_context_data(self, *args, **kwargs):
        model_objects = self.model and self.model.objects.all().order_by('-pk')

        context = {
            'model': self.model,
            'models_list': self.model_list,
            'model_name': self.model_name,
            'model_objects': model_objects,
            'add_form': self.form
        }
        return context


class DeleteDynamicModelObjectView(View):

    def get(self, request, model, object_id):
        model_class = DynamicModel.get_model(APP_LABEL, model)
        if not model_class:
            raise Http404

        get_object_or_404(model_class, pk=object_id).delete()

        return redirect('dynamic_model', model_name=model)

