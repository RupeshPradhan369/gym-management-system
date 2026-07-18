from django.db import models
from django.utils import timezone
from apps.identity.models import User
from apps.membership.models import Membership


class Invoice(models.Model):
    """
    One invoice can bundle multiple charges — a membership renewal,
    a locker fee, a protein shake — as separate InvoiceItem rows.
    """

    class Status(models.TextChoices):
        UNPAID = 'unpaid', 'Unpaid'
        PARTIALLY_PAID = 'partially_paid', 'Partially Paid'
        PAID = 'paid', 'Paid'
        CANCELLED = 'cancelled', 'Cancelled'

    invoice_number = models.CharField(max_length=30, unique=True, editable=False)
    member = models.ForeignKey(User, on_delete=models.PROTECT, related_name='invoices', limit_choices_to={'role': 'member'})
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UNPAID)
    issued_date = models.DateField(default=timezone.localdate)
    due_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='invoices_created')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_amount(self):
        return sum((item.line_total for item in self.items.all()), start=0)

    @property
    def amount_paid(self):
        return sum((p.amount for p in self.payments.filter(status=Payment.Status.SUCCESS)), start=0)

    @property
    def balance_due(self):
        return self.total_amount - self.amount_paid

    def __str__(self):
        return f"{self.invoice_number} — {self.member.username}"


class InvoiceItem(models.Model):
    """A single charge line on an invoice — membership, locker, product, etc."""

    class ItemType(models.TextChoices):
        MEMBERSHIP = 'membership', 'Membership'
        LOCKER = 'locker', 'Locker'
        PRODUCT = 'product', 'Product'
        PERSONAL_TRAINING = 'personal_training', 'Personal Training'
        REGISTRATION_FEE = 'registration_fee', 'Registration Fee'
        OTHER = 'other', 'Other'

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=30, choices=ItemType.choices)
    description = models.CharField(max_length=255)
    membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoice_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def line_total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.description} x{self.quantity}"


class Payment(models.Model):
    """A payment attempt/record against an invoice — cash, card, or eSewa."""

    class Method(models.TextChoices):
        CASH = 'cash', 'Cash'
        CARD = 'card', 'Card'
        ESEWA = 'esewa', 'eSewa'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=Method.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    esewa_ref_id = models.CharField(max_length=100, blank=True)  # eSewa's transaction reference
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.amount} for {self.invoice.invoice_number} ({self.status})"


class Expense(models.Model):
    """Gym operating expenses — rent, equipment, salaries — for the reports module."""

    class Category(models.TextChoices):
        RENT = 'rent', 'Rent'
        SALARY = 'salary', 'Salary'
        EQUIPMENT = 'equipment', 'Equipment'
        UTILITIES = 'utilities', 'Utilities'
        MAINTENANCE = 'maintenance', 'Maintenance'
        OTHER = 'other', 'Other'

    category = models.CharField(max_length=20, choices=Category.choices)
    description = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField(default=timezone.localdate)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='expenses_recorded')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} — {self.amount} ({self.expense_date})"