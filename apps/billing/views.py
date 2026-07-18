from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Invoice, Payment, Expense
from .serializers import InvoiceSerializer, PaymentSerializer, ExpenseSerializer
from apps.identity.permissions import IsAdminOrReceptionist, IsAdmin
from apps.notifications.services import notify
from apps.notifications.models import Notification


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related('member').prefetch_related('items', 'payments').all()
    serializer_class = InvoiceSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdminOrReceptionist()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.role == 'member':
            return self.queryset.filter(member=self.request.user)
        return self.queryset

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrReceptionist])
    def record_payment(self, request, pk=None):
        """
        POST /invoices/{id}/record_payment/  body: {"amount": ..., "method": "cash"}
        For cash/card payments taken at the counter — marks success immediately.
        eSewa uses a separate initiate/callback flow (to be built later).
        """
        invoice = self.get_object()
        payment = Payment.objects.create(
            invoice=invoice,
            amount=request.data.get('amount'),
            method=request.data.get('method', Payment.Method.CASH),
            status=Payment.Status.SUCCESS,
            paid_at=timezone.now(),
        )
        invoice.refresh_from_db()
        if invoice.balance_due <= 0:
            invoice.status = Invoice.Status.PAID
        else:
            invoice.status = Invoice.Status.PARTIALLY_PAID
        invoice.save()

        notify(
            user=invoice.member,
            title="Payment received",
            body=f"We received your payment of Rs. {payment.amount} for invoice {invoice.invoice_number}.",
            notification_type=Notification.NotificationType.PAYMENT_SUCCESS,
        )

        return Response(InvoiceSerializer(invoice, context={'request': request}).data)


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAdmin]

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)