from .education_model import EducationModel
from .toxicity_model import ToxicityModel

from django.db import models

class TextScore(models.Model):
    entered_text = models.TextField()
    education_score = models.FloatField()
    toxicity_score_normal = models.FloatField()
    toxicity_score_toxic = models.FloatField()

    def __str__(self):
        return self.entered_text
    
class TextCount(models.Model):
    serial_number = models.AutoField(primary_key=True)
    text = models.TextField(unique=True)
    count = models.IntegerField(default=2)

    def __str__(self):
        return f"{self.text} - {self.count}"