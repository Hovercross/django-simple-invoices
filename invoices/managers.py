from django.db import models

class InvoiceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(total=models.Sum('lineitem__total'))