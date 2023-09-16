from django.db import models

class Teacher(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    google_scholar = models.URLField()
    research_gate = models.URLField()
    dblp = models.URLField()
    rg_interests = models.TextField()
    gs_interests = models.TextField()
    pubs_proba = models.TextField()
    
class Publication(models.Model):
    title = models.CharField(max_length=300)
    authors = models.TextField() 
    date = models.CharField(max_length=12)  
    journal_book = models.TextField()
    doi = models.URLField()
    auth_id = models.URLField()
    lang = models.CharField(max_length=4)
    abstract = models.TextField()

class FinalPublication(models.Model):
    source = models.CharField(max_length=255)
    auth_id = models.CharField(max_length=255)
    title = models.CharField(max_length=2000)
    abstract = models.TextField()
    authors = models.CharField(max_length=1000)
    date = models.TextField()
    journal = models.CharField(max_length=600)
    doi = models.CharField(max_length=500)
    norm_title = models.CharField(max_length=1000)
    norm_abstract = models.TextField()
    order = models.CharField(max_length=255)
    coeff = models.TextField()
    proba = models.TextField()
    