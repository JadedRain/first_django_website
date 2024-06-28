import datetime

from django.contrib import admin
from django.db import models
from django.utils import timezone

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    
    @admin.display(boolean=True, ordering="pub_date", description="Published recently")
    def was_published_recent(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    
    @admin.display(boolean=False, ordering="choices_count", description="Number of Choices")
    def choices_count(self):
        return self.choice_set.all().count()
        
    def __str__(self) -> str:
        return self.question_text
    
    
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    
    def __str__(self) -> str:
        return self.choice_text
