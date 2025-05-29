from django.core.validators import RegexValidator
from django.db import models
from .helpers import *
from djongo.models import ArrayField, EmbeddedField, JSONField
from usermanagement.models import Users, Business
from django.core.exceptions import ValidationError
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from datetime import date
from django.db.models import Q


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def validate_account_number(value):
    if value < 0 or value > 9999999999999999:
        raise ValidationError("Account number must be a positive integer with up to 16 digits")


class Address(models.Model):
    address_line1 = models.CharField(max_length=200, null=True, blank=True)
    state = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    postal_code = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True


class DetailedItem(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    quantity = models.CharField(max_length=200, null=True, blank=True)
    unit_price = models.CharField(max_length=200, null=True, blank=True)
    hsn_sac = models.CharField(max_length=200, null=True, blank=True)
    discount = models.CharField(max_length=200, null=True, blank=True)
    amount = models.CharField(max_length=200, null=True, blank=True)
    cgst = models.CharField(max_length=200, null=True, blank=True)
    sgst = models.CharField(max_length=200, null=True, blank=True)
    igst = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        abstract = True


class PaymentDetail(models.Model):
    date = models.CharField(max_length=50, null=True, blank=True)
    paid_amount = models.FloatField(null=True, blank=True)

    class Meta:
        abstract = True


class InvoicingProfile(BaseModel):
    business = models.OneToOneField(Business, on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=50)
    account_number = models.BigIntegerField(validators=[validate_account_number])
    ifsc_code = models.CharField(max_length=50)
    swift_code = models.CharField(max_length=50, null=True, blank=True)
    signature = models.ImageField(upload_to=signatures_upload_path, null=True, blank=True)
    gst_registered = models.BooleanField()
    gstin = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return f"Invoicing Profile: {self.business}"


class InvoiceFormat(models.Model):
    invoicing_profile = models.ForeignKey(
        'InvoicingProfile',
        related_name='invoice_formats',
        on_delete=models.CASCADE,
        null=True
    )
    # is_common_format = models.BooleanField(
    #     default=False,
    #     help_text="Indicates if this format applies to all GSTINs under the invoicing profile"
    # )
    is_common_format = models.CharField(max_length=10, choices=[('yes', 'Yes'), ('no', 'No')], default='yes')
    gstin = models.CharField(max_length=20, null=True, blank=False)
    prefix = models.CharField(max_length=20, blank=True, null=True)
    series_code = models.CharField(max_length=10, blank=True, null=True)
    running_number_start = models.IntegerField(default=1)
    include_branch_code = models.BooleanField(default=False)
    include_financial_year = models.BooleanField(default=True)
    include_series_code = models.BooleanField(default=False)
    include_running_number = models.BooleanField(default=True)
    reset_every_fy = models.BooleanField(default=True)
    maintain_sequence_per_branch = models.BooleanField(default=False)
    maintain_sequence_per_gstin = models.BooleanField(default=False)
    format_version = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Invoice Format for {self.invoicing_profile.gst_registered} [{self.gstin}]"

    def clean(self):
        # Check if the combination of invoicing_profile and gstin already exists
        if self.gstin:
            if InvoiceFormat.objects.filter(
                invoicing_profile=self.invoicing_profile,
                gstin=self.gstin
            ).exclude(id=self.id).exists():
                raise ValidationError(
                    {"gstin": "GSTIN already exists for this Invoicing Profile."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()  # Ensure model validations are executed before saving
        super().save(*args, **kwargs)


class CustomerProfile(models.Model):
    invoicing_profile = models.ForeignKey(InvoicingProfile,  related_name='customer_profiles',
                                          on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    pan_number = models.CharField(max_length=10, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    address_line1 = models.CharField(max_length=200, null=True, blank=True)
    address_line2 = models.CharField(max_length=200, null=True, blank=True)
    state = models.CharField(max_length=30, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    city = models.CharField(max_length=30, null=True, blank=True)
    gst_registered = models.CharField(max_length=100, null=True, blank=True)
    gstin = models.CharField(max_length=100, null=True, blank=True)
    gst_type = models.CharField(max_length=60, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    opening_balance = models.IntegerField(null=True)
    entity_type = models.CharField(max_length=100, null=True, blank=True, default=None)

    def __str__(self):
        return f"Customer: {self.name}"


class GoodsAndServices(models.Model):
    invoicing_profile = models.ForeignKey(InvoicingProfile, on_delete=models.CASCADE, null=True, related_name='goods_and_services')
    type = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    sku_value = models.FloatField(null=True)
    units = models.CharField(max_length=100, null=True, blank=True)
    hsn_sac = models.CharField(max_length=500, null=True, blank=True)
    gst_rate = models.CharField(max_length=10, null=True, blank=True)
    tax_preference = models.CharField(max_length=60, null=True, blank=True)
    selling_price = models.IntegerField(null=True)
    description = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - GST Rate: {self.gst_rate}%"


class CustomerInvoiceReceipt(models.Model):
    TAX_DEDUCTED_CHOICES = [
        ('no_tax', 'No Tax deducted'),
        ('tds_income_tax', 'Yes, TDS (Income Tax)'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('written off', 'written off')
    ]
    invoice = models.ForeignKey('Invoice', related_name='customer_invoice_receipts', on_delete=models.CASCADE)
    date = models.DateField(null=False, blank=False)
    amount = models.FloatField()
    method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='cash')
    reference_number = models.CharField(max_length=50, null=True, blank=True)
    payment_number = models.IntegerField()
    tax_deducted = models.CharField(
        max_length=60,
        choices=TAX_DEDUCTED_CHOICES,
        default='no_tax'
    )
    amount_withheld = models.FloatField(null=True)
    comments = models.TextField(blank=True)

    class Meta:
        unique_together = ('invoice', 'payment_number')

    def clean(self):
        if self.tax_deducted == 'tds_income_tax' and self.amount_withheld is None:
            raise ValidationError("Amount withheld must be specified if tax is deducted.")
        if self.tax_deducted == 'no_tax' and self.amount_withheld is not None:
            raise ValidationError("Amount withheld should be null if no tax is deducted.")

    def __str__(self):
        return f"Payment for Invoice #{self.invoice.invoice_number} - {self.method}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save the current payment receipt

        # After saving, update the invoice's payment status
        self.invoice.update_payment_status()


class Invoice(models.Model):
    invoicing_profile = models.ForeignKey('InvoicingProfile', on_delete=models.CASCADE, null=True,
                                          related_name='invoices')
    customer = models.CharField(max_length=200, null=False, blank=False)
    terms = models.CharField(max_length=500, null=False, blank=False)
    financial_year = models.CharField(max_length=50, null=False, blank=False)
    invoice_number = models.CharField(max_length=50, null=False, blank=False)
    format_version = models.IntegerField(null=False)
    invoice_date = models.DateField(null=False, blank=False)
    due_date = models.DateField(null=False, blank=False)
    month = models.IntegerField(null=False, blank=False)
    sales_person = models.CharField(max_length=60, null=True, blank=True)
    order_number = models.CharField(max_length=60, null=True, blank=True)
    place_of_supply = models.CharField(max_length=500, null=False, blank=False)
    billing_address = models.JSONField(default=dict, null=True, blank=True)
    shipping_address = models.JSONField(default=dict, null=True, blank=True)
    item_details = JSONField(
        default=list,
        blank=True
    )
    gstin = models.CharField(max_length=100, null=True, blank=True)
    branch_code = models.CharField(max_length=100, null=True, blank=True, default="NA")
    total_amount = models.FloatField(null=True, blank=False)
    subtotal_amount = models.FloatField(null=True, blank=False)
    shipping_amount = models.FloatField(null=True, blank=False)
    total_cgst_amount = models.FloatField(null=True, blank=False)
    total_sgst_amount = models.FloatField(null=True, blank=False)
    total_igst_amount = models.FloatField(null=True, blank=False)
    pending_amount = models.FloatField(null=True, blank=False)
    amount_invoiced = models.FloatField(null=True, blank=False)
    payment_status = models.CharField(max_length=50, default="Pending", null=True, blank=True)
    notes = models.CharField(max_length=500, null=True, blank=True)
    terms_and_conditions = models.CharField(max_length=500, null=True, blank=True)
    applied_tax = models.BooleanField(default=False)
    shipping_tax = models.FloatField(null=True)
    shipping_amount_with_tax = models.FloatField(null=True)
    selected_gst_rate = models.FloatField(null=True)
    invoice_status = models.CharField(max_length=60, null=False, blank=False)
    customer_gstin = models.CharField(max_length=100, null=True, blank=True)
    customer_pan = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Invoice: {self.invoice_number}"

    def update_payment_status(self):
        # Handle the different cases for invoice_status
        if self.invoice_status in ["Draft", "Pending Approval", "Resubmission"]:
            # If the invoice is in any of these statuses, set payment_status to "NA"
            self.payment_status = "NA"
            self.save()
            return

        # If the invoice is Approved, set the payment_status to Pending
        if self.invoice_status == "Approved":
            self.payment_status = "Pending"

        # Check if the total amount has changed
        previous_total_amount = self.__class__.objects.get(id=self.id).total_amount
        total_paid = sum(receipt.amount for receipt in self.customer_invoice_receipts.all())

        # If the total amount has increased, adjust the pending amount and payment status
        if self.total_amount > previous_total_amount:
            # If the total amount has increased, update the pending amount
            self.pending_amount = self.total_amount - total_paid

            # If the pending amount is 0, mark it as Paid
            if self.pending_amount == 0:
                self.payment_status = "Paid"
            # If there's still a balance to be paid, mark it as Partially Paid
            elif self.pending_amount > 0:
                self.payment_status = "Partially Paid"

            # If the due date has passed and the invoice is not fully paid, mark as Overdue
            if self.due_date < date.today() and self.payment_status != "Paid":
                self.payment_status = "Overdue"

        # If the invoice amount remains the same or decreased, calculate the pending amount
        else:
            self.pending_amount = self.total_amount - total_paid

            # Ensure pending amount is not negative (in case of overpayments)
            self.pending_amount = max(self.pending_amount, 0)

            # Check if the invoice is fully paid
            if total_paid >= self.total_amount:
                self.payment_status = "Paid"
            elif total_paid > 0:
                self.payment_status = "Partially Paid"
            else:
                self.payment_status = "Pending"

        # Check if the invoice is overdue (only if due_date has passed and payment is not fully made)
        if self.due_date < date.today() and self.payment_status != "Paid":
            self.payment_status = "Overdue"

        # Save the updates to the database
        self.save()


# Signals to automatically update the payment status after saving a payment receipt
@receiver(post_save, sender=CustomerInvoiceReceipt)
def update_invoice_payment_status(sender, instance, **kwargs):
    instance.invoice.update_payment_status()


@receiver(post_delete, sender=CustomerInvoiceReceipt)
def update_invoice_payment_status_on_delete(sender, instance, **kwargs):
    """
    Triggered when a CustomerInvoiceReceipt is deleted.
    """
    instance.invoice.update_payment_status()