from django.db import models
import uuid
from django.utils import timezone
from django.contrib.auth.models import User
from PIL import Image

from django.core.files.storage import default_storage
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager
from taggit.models import GenericUUIDTaggedItemBase, TaggedItemBase, Tag

# https://stackoverflow.com/questions/31683216/django-taggit-on-models-with-uuid-as-pk-throwing-out-of-range-on-save
class UUIDTaggedItem(GenericUUIDTaggedItemBase):
    # If you only inherit GenericUUIDTaggedItemBase, you need to define
    # a tag field. e.g.
    tag = models.ForeignKey(Tag, related_name="uuid_tagged_items", on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

class LibrarianItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='owner_items')
    title = models.CharField(max_length=255)
    status = models.CharField(
        max_length=50,
        choices=[
            ('available', 'Available'),
            ('unavailable', 'Unavailable'),
            ('in_repair', 'In Repair'),
        ],
        blank=False,
    )
    location = models.CharField(max_length=255)
    description = models.TextField(blank=False)
    uploaded_at = models.DateTimeField(default=timezone.now)
    # image = models.ImageField(upload_to='boardgame_pics', default='default_boardgame.jpg', storage=default_storage, blank=True, null=True)
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='borrower_items')
    borrowed_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    # https://medium.com/@yashnarsamiyev2/welcome-to-django-taggit-a38c1ff4bb9a
    tags = TaggableManager(through=UUIDTaggedItem)
        
    def __str__(self):
        return self.title
    
    def avg_rating(self):
        reviews = Review.objects.filter(item=self)
        if reviews:
            sum = 0
            num = 0
            for r in reviews:
                sum += r.rating
                num += 1
            avg_rating = sum/num
        else:
            avg_rating = -1
        return avg_rating
      
class LibrarianItemImage(models.Model):
    item = models.ForeignKey(LibrarianItem, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='boardgame_pics', default='boardgame_pics/default_boardgame.jpg', storage=default_storage, blank=True, null=True)

class Review(models.Model):
    item = models.ForeignKey(LibrarianItem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    
class ItemAccessRequest(models.Model):
    patron = models.ForeignKey(User, on_delete=models.CASCADE, related_name='item_requests')
    item = models.ForeignKey(LibrarianItem, on_delete=models.CASCADE, related_name='access_requests')
    status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('denied', 'Denied')],
        default='pending'
    )
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.patron.username} -> {self.item.title} ({self.status})"
    
class ItemReturnRequest(models.Model):
    patron = models.ForeignKey(User, on_delete=models.CASCADE, related_name='item_return_requests')
    item = models.ForeignKey(LibrarianItem, on_delete=models.CASCADE, related_name='return_requests')
    status = models.CharField(
        max_length=15,
        choices=[('pending', 'Pending'), ('received', 'Received'), ('not_received', 'Not Received')],
        default='pending'
    )
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.patron.username} -> {self.item.title} ({self.status})"
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.message[:50]}"

class Collection(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    is_private = models.BooleanField(default=False)
    visible_to = models.ManyToManyField(User, blank=True, related_name='visible_collections')

    items = models.ManyToManyField(LibrarianItem, blank=True)

    def __str__(self):
        return self.name
    
class CollectionAccessRequest(models.Model):
    patron = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_requests')
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='access_requests')
    status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('denied', 'Denied')],
        default='pending'
    )
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.patron.username} -> {self.collection.name} ({self.status})"
    
class AccountUpgradeRequestRead(models.Model):
    request = models.ForeignKey('AccountUpgradeRequest', on_delete=models.CASCADE, related_name='read_receipts')
    librarian = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('request', 'librarian')
    
class AccountUpgradeRequest(models.Model):
    patron = models.ForeignKey(User, on_delete=models.CASCADE, related_name='upgrade_requests')
    status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('denied', 'Denied')],
        default='pending'
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.patron.username} -> ({self.status})"
    
    def mark_as_read(self, user):
        AccountUpgradeRequestRead.objects.get_or_create(request=self, librarian=user)

# This model is used to create a one-to-one relationship between users (A model provided by Django) and this model which just contains an image
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics', default='default.jpg', storage=default_storage, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'
    
    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     img = Image.open(self.image.name)

    #     MAX_SIZE = 300

    #     if img.height > MAX_SIZE or img.width > MAX_SIZE:
    #         output_size = (MAX_SIZE, MAX_SIZE)
    #         img.thumbnail(output_size)
    #         img.save(self.image.name)