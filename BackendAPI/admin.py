from django.contrib import admin
from . models import Role, User, UserActivityLog
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.mail import send_mail
# Register your models here.
admin.site.site_header = "AURA Admin"
admin.site.site_title = "AURA Admin Portal"
admin.site.index_title = "Welcome to Admin Portal"
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["id", "roles", "get_user_names"]
    ordering = ["id"] 

    def get_user_names(self, obj):
        users = User.objects.filter(role__in=[role[0] for role in User.ROLE_CHOICES if role[1] == obj.roles])
        return ", ".join(user.name for user in users)

    get_user_names.short_description = "Users"
        #display = ['id','username','role']

class UserAdmin(BaseUserAdmin):
   
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ["id","email", "name", "is_admin","role"]
    list_filter = ["is_admin"]
    fieldsets = [
        ("User Credentials", {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["name"]}),
        ("Permissions", {"fields": ["is_admin","role"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "name", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["id","email"]
    filter_horizontal = []
    def save_model(self, request, obj, form, change):
        is_new_user = obj.pk is None
        password = form.cleaned_data.get('password1') if is_new_user else None
        super().save_model(request, obj, form, change)
        
        if is_new_user and password:
            self.send_registration_email(obj, password)

    def send_registration_email(self, user, password):
        subject = 'Registration Details'
        message = f'Hello {user.name} \nUser ID : {user.id}\nYour registration is successful.\n\nEmail: {user.email}\nPassword: {password}'
        send_mail(subject, message, 'aura.riskdashboard@gmail.com', [user.email])
    


# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)

@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'timestamp', 'details']
    list_filter = ['activity_type', 'timestamp']
    search_fields = ['user__email', 'activity_type']
    ordering = ['-timestamp']