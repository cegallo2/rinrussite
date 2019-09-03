from django.db import models
from django.contrib.auth.models import User
from datetime import datetime  

class Simulation(models.Model):
	unProcessedPDBURL = models.CharField(max_length=100)
	zipPath=models.CharField(max_length=100, default="")
	idNumber=models.AutoField(primary_key=True)
	isProcessed=models.BooleanField(default=False)
	valid=models.BooleanField(default=False) 
	dateRan=models.DateTimeField(default=datetime.now, blank=True)
	residue=models.CharField(max_length=100)
	chain=models.CharField(max_length=100)
	simName=models.CharField(max_length=100)
	userName=models.CharField(max_length=100, default="Not Specified")
	modelVersion=models.DecimalField(max_digits=4, decimal_places=2, default=0.9)



	
	
