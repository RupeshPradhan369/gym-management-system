from django.contrib import admin
from .models import Equipment, Maintenance, Locker, LockerAssignment


class MaintenanceInline(admin.TabularInline):
    model = Maintenance
    extra = 0


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'status', 'purchase_date')
    list_filter = ('category', 'status')
    inlines = [MaintenanceInline]


@admin.register(Locker)
class LockerAdmin(admin.ModelAdmin):
    list_display = ('locker_number', 'status', 'monthly_fee')
    list_filter = ('status',)


@admin.register(LockerAssignment)
class LockerAssignmentAdmin(admin.ModelAdmin):
    list_display = ('locker', 'member', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)