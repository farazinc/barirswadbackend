from django.db import models

class UserProfile(models.Model):
    ROLE_CHOICES = [('user', 'User'), ('seller', 'Seller')]

    uid = models.OneToOneField(
        "auth.User", on_delete=models.CASCADE, related_name="profile"
    )
    name = models.CharField(max_length=120)
    profilePic = models.URLField(null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
