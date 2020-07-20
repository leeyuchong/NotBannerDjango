from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Courses(models.Model):
    courseID=models.CharField(max_length=12, primary_key=True)
    title=models.CharField(max_length=31)
    units=models.DecimalField(max_digits=2, decimal_places=1)
    sp=models.BooleanField()
    requests=models.PositiveSmallIntegerField(null=True)
    limits=models.CharField(max_length=20, null=True)
    Max=models.PositiveSmallIntegerField()
    enr=models.PositiveSmallIntegerField()
    avl=models.SmallIntegerField()
    wl=models.PositiveSmallIntegerField()
    gm=models.CharField(max_length=2)
    yl=models.BooleanField()
    pr=models.BooleanField()
    fr=models.BooleanField()
    la=models.BooleanField()
    qa=models.BooleanField()
    Format=models.CharField(max_length=3)
    xlist=models.CharField(max_length=20)
    d1=models.CharField(max_length=5)
    time1=models.CharField(max_length=15)
    starttime1=models.PositiveSmallIntegerField(null=True)
    duration1=models.PositiveSmallIntegerField(null=True)
    delt91=models.DecimalField(max_digits=5, decimal_places=2, null=True)
    d2=models.CharField(max_length=5, null=True)
    time2=models.CharField(max_length=15, null=True)
    starttime2=models.PositiveSmallIntegerField(null=True)
    duration2=models.PositiveSmallIntegerField(null=True)
    delt92=models.DecimalField(max_digits=5, null=True, decimal_places=2)
    loc=models.CharField(max_length=10, blank=True)
    instructor=models.CharField(max_length=30, blank=True)
    description=models.TextField(blank=True)
    status=models.CharField(max_length=9)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # cal1name=models.CharField(max_length=30, blank=True)
    cal1course1=models.CharField(max_length=12, default='blank')
    cal1course2=models.CharField(max_length=12, default='blank')
    cal1course3=models.CharField(max_length=12, default='blank')
    cal1course4=models.CharField(max_length=12, default='blank')
    cal1course5=models.CharField(max_length=12, default='blank')
    cal1course6=models.CharField(max_length=12, default='blank')
    cal1course7=models.CharField(max_length=12, default='blank')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
