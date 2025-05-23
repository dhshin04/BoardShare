from django.db import models
#from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

def ends_with_validator(value):
    if not value.endswith("@gmail.com"):
        raise ValidationError(f"Input must end with '@gmail.com'")
    else:
        return value

class UserType(models.Model):
    email = models.EmailField(max_length=255, unique=True, validators=[ends_with_validator])
    is_librarian = models.BooleanField(default=False)

    def __str__(self):
        return self.email