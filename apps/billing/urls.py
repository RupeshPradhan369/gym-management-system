from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet, ExpenseViewSet

router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'expenses', ExpenseViewSet, basename='expense')

urlpatterns = router.urls