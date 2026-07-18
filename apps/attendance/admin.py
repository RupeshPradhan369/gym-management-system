from django.contrib import admin
from .models import Attendance, StaffAttendance, QRToken


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('member', 'check_in_time', 'check_out_time', 'method', 'marked_by')
    list_filter = ('method',)
    search_fields = ('member__username',)


@admin.register(StaffAttendance)
class StaffAttendanceAdmin(admin.ModelAdmin):
    list_display = ('staff', 'check_in_time', 'check_out_time')
    search_fields = ('staff__username',)


@admin.register(QRToken)
class QRTokenAdmin(admin.ModelAdmin):
    list_display = ('member', 'token', 'expires_at', 'is_used')
    list_filter = ('is_used',)