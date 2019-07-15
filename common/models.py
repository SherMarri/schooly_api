from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)


    class Meta:
        abstract = True


class Config(BaseModel):
    name = models.CharField(max_length=20)
    description = models.TextField(max_length=500, null=True, blank=True)
    value = models.IntegerField()

    def __str__(self):
        return self.name