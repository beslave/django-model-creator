# coding: utf-8
from django import forms
from django.contrib import admin

from .models import (
    get_app_choices,
    ModelTemplate,
    ModelTemplateField
)


class ModelTemplateForm(forms.ModelForm):
    app = forms.ChoiceField(
        choices=[]
    )

    class Meta:
        model = ModelTemplate

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['app'].choices = sorted(
            get_app_choices(),
            key=lambda x: x[1]
        )


class ModelTemplateFieldInline(admin.TabularInline):
    model = ModelTemplateField
    fk_name = 'model_template'

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        return 1


class ModelTemplateAdmin(admin.ModelAdmin):
    form = ModelTemplateForm
    inlines = [
        ModelTemplateFieldInline,
    ]
    list_display = ('name', 'verbose_name', 'app')
    list_filter = ('app',)


admin.site.register(ModelTemplate, ModelTemplateAdmin)
