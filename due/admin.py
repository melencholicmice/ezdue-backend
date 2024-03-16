from django.contrib import admin
from due.models import Due, DueResponse

# :NOTE: for local developlment only,
# Remove this admin should not acess this
admin.site.register(Due)
admin.site.register(DueResponse)