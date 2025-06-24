from django.db import models
from django.contrib.auth.models import User, Permission


# Create your models here.
#//======================== SubAdmin Model ====================================//
class SubAdmin(models.Model):
    """
    Represents a sub-admin user in the system who has specific, limited permissions
    such as reading, updating, or deleting book records.

    This model extends Django's built-in User model via a one-to-one relationship,
    allowing each sub-admin to be associated with a single user account. Permissions
    are stored in a many-to-many relationship with Django's `Permission` model.

    Custom permissions (`ReadBook`, `UpdateBook`, `DeleteBook`) are defined to enable
    fine-grained access control for sub-admins without granting full administrative rights.

    Usage:
        - Assign permissions via `subadmin.permissions.add(...)`
        - Enforce permissions in views using `user.has_perm('app_label.codename')`

    Example:
        sub_admin = SubAdmin.objects.create(user=some_user)
        read_perm = Permission.objects.get(codename='ReadBook')
        sub_admin.permissions.add(read_perm)
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    permissions = models.ManyToManyField(Permission)

    class Meta:
        #This defines the singular name for the model that appears in the Django admin and elsewhere.
        #displays Sub Admin(s) instead of class name
        verbose_name = 'Sub Admin'
        verbose_name_plural = 'Sub Admins'
        permissions = [
            ('ReadBook','can read book'),
            ('UpdateBook' , 'can update book'),
            ('DeleteBook' , 'can delete book'),
        ]
#//============================================================//