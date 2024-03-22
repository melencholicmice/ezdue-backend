from django.contrib import admin
from due.models import Due, DueResponse

# :NOTE: for local developlment only,
# Remove this admin should not acess this

class DueResponseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'due',
        'response_mode',
        'status'
    )

class DueAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'amount',
        'reason',
        'status'
    )

admin.site.register(Due,DueAdmin)
admin.site.register(DueResponse,DueResponseAdmin)