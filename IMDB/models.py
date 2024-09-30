from django.db import models
from django.contrib.auth.models import User
import pandas as pd
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
# Create your models here.

# FilmReview table. 
class FilmReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)
    rating = models.IntegerField()
    sentiment = models.CharField(max_length=1000, null=True)
    film = models.ForeignKey('Film', on_delete = models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f"{self.user.username} - {self.text} - Rating: {self.rating}"
    
# ExtendedUser table. In spate, orm-ul pt django creeaza o tabela intermediara
# pentru field-ul ManyToMany favoriteFilms
class ExtendedUser(models.Model):
    user = models.OneToOneField(User, primary_key = True, on_delete=models.CASCADE)
    favoriteMovies =  models.ManyToManyField('Film', blank=True)
    avatar = models.ImageField(upload_to='images/', null=True, blank=True)
    newsletter_subscribed = models.BooleanField(default=False)

    def __str__(self):
       return self.user.username
    
@receiver(post_save, sender=User)
def update_extended_user(sender, instance, created, **kwargs):
    if created:
        ExtendedUser.objects.create(user=instance)
    else:
        instance.extendeduser.save()

@receiver(post_delete, sender=User)
def delete_extended_user(sender, instance, **kwargs):
    try:
        instance.extendeduser.delete()
    except ExtendedUser.DoesNotExist:
        pass

class Actor(models.Model):
    name = models.CharField(primary_key = True, max_length=30)
    birth_date = models.DateField()
    biography = models.TextField(null=True)
    films = models.ManyToManyField('Film', blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    
    def __str__(self):
        return self.name
 
class Producers(models.Model):
    name = models.CharField(primary_key = True, max_length=30)
    birth_date = models.DateField()

    def __str__(self):
        return self.name

# Film table. In spate, orm-ul pt django creeaza o tabela intermediara
# pentru field-ul ManyToMany actors
class Film(models.Model):
    title = models.CharField(primary_key = True, max_length=50)
    release_date = models.DateField()
    producer = models.ForeignKey('Producers', on_delete=models.CASCADE)
    genre = models.CharField(max_length= 40, blank=True)
    actors = models.ManyToManyField('Actor', blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    description = models.CharField(max_length = 1000, null=True)
    streaming_platform = models.CharField(max_length= 25, null=True)
    score = models.IntegerField(null=True)

    def __str__(self):
        return self.title

class Dataset(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='datasets/')

    def __str__(self):
        return self.name

    @classmethod
    def process_csv_data(cls, dataset_id):
        dataset = cls.objects.get(pk=dataset_id)
        if dataset.file:
            df = pd.read_csv(dataset.file.path, low_memory=False)
            for index,row in df.iterrows():
                DatasetEntry.objects.create(dataset=dataset, review=row['review'], sentiment=row['sentiment'])

class DatasetEntry(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    review = models.TextField()
    sentiment = models.CharField(max_length=10)

    def __str__(self):
        return self.review[:50]