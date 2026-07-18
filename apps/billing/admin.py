from django.contrib import admin
from .models import Invoice, InvoiceItem, Payment, Expense


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'member', 'status', 'issued_date', 'total_amount', 'amount_paid', 'balance_due')
    list_filter = ('status',)
    search_fields = ('invoice_number', 'member__username')
    inlines = [InvoiceItemInline, PaymentInline]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('category', 'amount', 'expense_date', 'recorded_by')
    list_filter = ('category',)