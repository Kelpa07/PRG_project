from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	bio = models.TextField(blank=True, help_text="Tell us about yourself")
	avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
	location = models.CharField(max_length=100, blank=True, help_text="Your location")
	website = models.URLField(blank=True, help_text="Your website or social media")
	phone = models.CharField(max_length=20, blank=True, help_text="Phone number")

	def __str__(self):
		return f"Profile({self.user.username})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)


class Order(models.Model):
	STATUS_CHOICES = [
		('on_the_way', 'On the way'),
		('received', 'Received'),
		('cancelled', 'Cancelled'),
	]
	user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
	items = models.TextField(help_text='JSON list of items')
	total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='on_the_way')
	payment_method = models.CharField(max_length=20, choices=[('qr_payment', 'QR Payment'), ('cash', 'Cash')], default='cash')
	payment_status = models.CharField(max_length=20, choices=[('paid', 'Paid'), ('pending_verification', 'Pending Verification'), ('unpaid', 'Unpaid')], default='unpaid')
	transaction_ref = models.CharField(max_length=100, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Order {self.id} - {self.status} - {self.total}"


class MenuItem(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	price = models.DecimalField(max_digits=6, decimal_places=2)
	image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
	available = models.BooleanField(default=True)

	def __str__(self):
		return self.name

# Create your models here.
