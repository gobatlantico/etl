from django.db import models
from django.utils import timezone
from django.forms import ModelForm
from django import forms
import datetime
# Create your models here.

class Categories(models.Model):
    category=models.CharField(max_length=100)

class Secretaries(models.Model):
	secretary=models.CharField(max_length=100)

class Users(models.Model):
	user=models.CharField(max_length=150, unique=True)
	name=models.CharField(max_length=150, default='Sin Nombre')
	password=models.CharField(max_length=150)
	secretaria=models.ForeignKey(Secretaries,to_field='id')
	#User state, type, Dates (Done)
	state=models.CharField(max_length=2, default='A')
	admin=models.BooleanField(default=False)
	created=models.DateField(auto_now_add=True)
	modified=models.DateField(auto_now=True)
	#---------------------------------
	#secretaria con id the secretaries (TO DO)
	#---------------------------------

class Datasets(models.Model):
	user=models.ForeignKey(Users,to_field='id')
	ip_address=models.CharField(max_length=20)
	title=models.CharField(max_length=150)
	dataset_id=models.CharField(max_length=255)
	
	#add creation date and modification date (DONE)
	created=models.DateField(auto_now_add=True)
	modified=models.DateField(auto_now=True)
	public=models.BooleanField(default=False)
	#----------------------------------------------
	#id User for field user in Datasets (TO DO)
	#----------------------------------------------
	

class Token(models.Model):
	user=models.ForeignKey(Users,to_field='id')
	token=models.CharField(max_length=150, unique=True)

class ETLS(models.Model):
	user=models.ForeignKey(Users,to_field='id')
	ip_address=models.CharField(max_length=20)
	title=models.CharField(max_length=150)
	dataset_id=models.CharField(max_length=255)
	view=models.CharField(max_length=255,null=True)
	#add creation date and modification date (DONE)
	created=models.DateField(auto_now_add=True)
	modified=models.DateTimeField(auto_now=True)
	public=models.BooleanField(default=False)
	next_update=models.DateTimeField(null=True)
	update_period=models.CharField(max_length=4,null=True)