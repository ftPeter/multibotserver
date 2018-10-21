from polymorphic.models import PolymorphicModel
from django.db import models

# Create your models here.
class Robot(models.Model):
    name = models.CharField(max_length=200)
    ip = models.CharField(max_length=200)
    time = models.CharField(max_length=200)
    type = models.ForeignKey('RobotType', on_delete=models.CASCADE,)

class RobotType(PolymorphicModel):
    pass

class RobotTypeA(RobotType):
    typeName = models.CharField(max_length=200, default='TypeA', editable=False)
    actions = models.CharField(max_length=200, default='Change Color, Move Left', editable=False)

    def get_actions(self):
        return self.actions.split(", ")

class RobotTypeB(RobotType):
    typeName = models.CharField(max_length=200, default='TypeB', editable=False)
    actions = models.CharField(max_length=200, default='Change Color, Move Right', editable=False)

    def get_actions(self):
        return self.actions.split(", ")
