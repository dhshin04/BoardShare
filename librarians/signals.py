from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_updated
from .models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

# need this so google accounts actually work
@receiver(social_account_updated)
def create_or_update_profile(sender, request, sociallogin, **kwargs):
    user = sociallogin.user
    Profile.objects.get_or_create(user=user)

post_save.connect(create_profile, sender=User)