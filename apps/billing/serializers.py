from rest_framework import serializers
from .models import Invoice, InvoiceItem, Payment, Expense


class InvoiceItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = InvoiceItem
        fields = ['id', 'item_type', 'description', 'membership', 'quantity', 'unit_price', 'line_total']
        read_only_fields = ['id']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'invoice', 'amount', 'method', 'status', 'esewa_ref_id', 'paid_at', 'created_at']
        read_only_fields = ['id', 'status', 'paid_at', 'created_at', 'esewa_ref_id']


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)
    payments = PaymentSerializer(many=True, read_only=True)
    member_username = serializers.CharField(source='member.username', read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    balance_due = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'member', 'member_username', 'status',
            'issued_date', 'due_date', 'items', 'payments',
            'total_amount', 'amount_paid', 'balance_due', 'created_at',
        ]
        read_only_fields = ['id', 'invoice_number', 'status', 'created_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        request = self.context['request']

        # Generate invoice number, e.g. INV-2026-00001
        from django.utils import timezone
        year = timezone.now().year
        count = Invoice.objects.filter(invoice_number__startswith=f"INV-{year}").count() + 1
        invoice_number = f"INV-{year}-{count:05d}"

        invoice = Invoice.objects.create(
            invoice_number=invoice_number,
            created_by=request.user,
            **validated_data,
        )
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)

        return invoice
    
class ExpenseSerializer(serializers.ModelSerializer):
    recorded_by_username = serializers.CharField(source='recorded_by.username', read_only=True, default=None)

    class Meta:
        model = Expense
        fields = ['id', 'category', 'description', 'amount', 'expense_date', 'recorded_by', 'recorded_by_username', 'created_at']
        read_only_fields = ['id', 'recorded_by', 'created_at']