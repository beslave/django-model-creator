from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View

from .model_templates_importer import Importer
from .models import get_app_choices


class ImportModelTemplateView(View):
    """
    Create new models templates or update exiting ones
    from file with allowed formats
    """

    template_name = 'admin/model_creator/modeltemplate/import_form.html'

    @method_decorator(staff_member_required)
    def dispatch(self, request):
        if request.method == 'POST':
            app = request.POST['app']
            file_type = request.POST['file_type']
            data = request.FILES['file'].read().decode('utf-8')

            SelectedTypeImporter = Importer.get_importer_by_type(file_type)
            SelectedTypeImporter(data, app).save()

            return redirect('admin:model_creator_modeltemplate_changelist')

        allowed_file_types = Importer.get_importers().keys()

        return render(request, self.template_name, {
            'apps': get_app_choices,
            'allowed_file_types': allowed_file_types,
            'title': _('Import model templates'),
        })
