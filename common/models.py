from django.db import models


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


class Session(BaseModel):
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
