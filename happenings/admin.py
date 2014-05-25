from __future__ import unicode_literals

from django.contrib import admin
from happenings.models import Event, Location, Category, Tag


class EventAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('start_date', 'end_date', 'all_day', 'repeat',
                       'end_repeat', 'title', 'description',
                       'created_by',)
        }),
        ('Location', {
            'classes': ('collapse',),
            'fields': ('location',)
        }),
        ('Category', {
            'classes': ('collapse',),
            'fields': ('categories',)
        }),
        ('Tag', {
            'classes': ('collapse',),
            'fields': ('tags',)
        }),
        ('Color', {
            'classes': ('collapse',),
            'fields': (
                ('background_color', 'background_color_custom'),
                ('font_color', 'font_color_custom'),
            )
        }),
    )

    list_display = ('title', 'start_date', 'end_date', 'repeat', 'end_repeat')
    list_filter = ['start_date']
    search_fields = ['title']
    date_hierarchy = 'start_date'

admin.site.register(Event, EventAdmin)
admin.site.register(Location)
admin.site.register(Category)
admin.site.register(Tag)
