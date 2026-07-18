from django.contrib import admin
from .models import MembershipPlan, Membership, MembershipFreeze


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_value', 'duration_unit', 'price', 'is_active')
    list_filter = ('is_active', 'duration_unit')


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('member', 'plan', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'plan')
    search_fields = ('member__username',)


@admin.register(MembershipFreeze)
class MembershipFreezeAdmin(admin.ModelAdmin):
    list_display = ('membership', 'freeze_start', 'freeze_end')