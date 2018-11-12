from polymorphic.models import PolymorphicModel
from django.db import models
from datetime import datetime

# Create your models here.
class Robot(models.Model):
    name = models.CharField(max_length=200)
    ip = models.CharField(max_length=200)
    time = models.CharField(max_length=200)
    type = models.OneToOneField('RobotType', on_delete=models.CASCADE,)
    active = models.BooleanField(default=False)

class RobotType(PolymorphicModel):
    pass

class RobotTypeA(RobotType):
    typeName = models.CharField(max_length=200, default='TypeA', editable=False)
    actions = models.CharField(max_length=200, default='Change Color, Check Battery, Take Picture', editable=False)

    def get_actions(self):
        return self.actions.split(", ")

class Image(models.Model):
    image = models.ImageField(upload_to='media')
    timestamp = models.DateTimeField(default=datetime.now)
    robot = models.ForeignKey(RobotTypeA, on_delete=models.CASCADE, related_name='gallery')