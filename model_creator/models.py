# coding: utf-8
from django.db import models


class DynamicModel(models.Model):
    """
    Base class of all dynamic-created models
    """

    class Meta:
        abstract = True
