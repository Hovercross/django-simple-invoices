import os
import uuid

from decimal import Decimal

from django.db import models


def uuidUpload(instance, filename):
    name, ext = os.path.splitext(filename)

    newName = "{}{}".format(uuid.uuid4().hex, ext)

    return "by-uuid/{}".format(newName)


# Create your models here.
class Client(models.Model):
    name = models.CharField(max_length=50)
    address = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Vendor(models.Model):
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    checks_payable_to = models.CharField(max_length=254, blank=True)

    address = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    client = models.ForeignKey(Client, on_delete=models.DO_NOTHING)
    vendor = models.ForeignKey(Vendor, on_delete=models.DO_NOTHING)
    description = models.CharField(max_length=254, blank=True)

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    public = models.BooleanField(default=False)

    date = models.DateField(blank=True, null=True)
    finalized = models.BooleanField(default=False)

    hourly_services_total = models.DecimalField(
        max_digits=20, decimal_places=2, default=0
    )
    fixed_services_total = models.DecimalField(
        max_digits=20, decimal_places=2, default=0
    )
    expense_total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    payment_total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    credit_total = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    total_charges = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_credits = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    total = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    ordering = ["client__name", "date"]

    def update_totals(self):
        # Special case for hourly to make sure we are using the same computation methods throughout
        hourly_services = HourlyService.objects.filter(invoice=self)

        rates = set()
        total_seconds = Decimal(0)
        total_dollars = Decimal()

        # Track both total hours and total dollars, along with the seen rates. We'll decide what to do at the end.
        for hourly_service in hourly_services:
            rates.add(hourly_service.rate)
            total_seconds += Decimal(hourly_service.duration.total_seconds())
            total_dollars += hourly_service.total

        if len(rates) == 0:
            self.hourly_services_total = 0
        elif len(rates) == 1:
            # Aggregated hours
            rate = rates.pop()
            self.hourly_services_total = round(total_seconds / 3600 * rate, 2)
        else:
            self.hourly_services_total = total_dollars

        MAPPING = [
            ("fixed_services_total", FixedService),
            ("expense_total", Expense),
            ("payment_total", Payment),
            ("credit_total", Credit),
        ]

        for attr, C in MAPPING:
            type_total = C.objects.filter(invoice=self).aggregate(models.Sum("total"))[
                "total__sum"
            ]
            if type_total is None:
                type_total = 0

            setattr(self, attr, type_total)

        CHARGE_ATTRS = [
            "hourly_services_total",
            "fixed_services_total",
            "expense_total",
        ]
        CREDIT_ATTRS = ["payment_total", "credit_total"]

        self.total_charges = sum([getattr(self, attr) for attr in CHARGE_ATTRS])
        self.total_credits = sum([getattr(self, attr) for attr in CREDIT_ATTRS]) * -1

        self.total = self.total_charges - self.total_credits

    def __str__(self):
        return "{id} - {client}".format(id=self.id, client=self.client)


class DisplayTotalMixin(object):
    @property
    def display_total(self):
        if self.total:
            return "${:0.2f}".format(self.total)

        return "-"


class ReverseDisplayTotalMixin(object):
    @property
    def display_total(self):
        if self.total:
            return "${:0.2f}".format(self.total * -1)

        return "-"


class LineItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    date = models.DateField(blank=True, null=True)
    description = models.CharField(max_length=255, blank=True)

    position = models.PositiveIntegerField(default=0, db_index=True)

    total = models.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        abstract = True
        ordering = ["position"]

    def __str__(self):
        if self.description:
            return "{class_name:} {id:}: {description}".format(
                class_name=self.__class__.__name__,
                id=self.id,
                description=self.description,
            )

        return "{class_name:} {id:}".format(
            class_name=self.__class__.__name__,
            id=self.id,
        )


class HourlyService(LineItem, DisplayTotalMixin):
    location = models.CharField(max_length=255, blank=True, null=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField(null=True)

    def save(self, *args, **kwargs):
        self.total = Decimal(self.duration.total_seconds()) / 3600 * self.rate
        super().save(*args, **kwargs)


class FixedService(LineItem, DisplayTotalMixin):
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total = self.amount
        super().save(*args, **kwargs)


class Expense(LineItem, DisplayTotalMixin):
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total = self.amount
        super().save(*args, **kwargs)


class Payment(LineItem, ReverseDisplayTotalMixin):
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total = self.amount * -1
        super().save(*args, **kwargs)


class Credit(LineItem, ReverseDisplayTotalMixin):
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total = self.amount * -1
        super().save(*args, **kwargs)


class RelatedPDF(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    description = models.CharField(max_length=254, blank=True)

    position = models.PositiveIntegerField(default=0, db_index=True)

    pdf = models.FileField(upload_to=uuidUpload, verbose_name="PDF")

    class Meta:
        ordering = ["position"]

    # TODO: Validate that the document is a PDF
