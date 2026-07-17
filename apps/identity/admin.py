from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, MemberProfile, StaffProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Gym Info', {'fields': ('role', 'phone_number')}),
    )
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active')


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ('member_code', 'user', 'gender', 'created_at')
    search_fields = ('member_code', 'user__username', 'user__email')


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('employee_code', 'user', 'designation', 'hired_date')
    search_fields = ('employee_code', 'user__username')