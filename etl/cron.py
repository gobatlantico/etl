from django.core.mail import send_mail
from .models import ETLS
from .datos import getView,UpdateDataset
from datetime import datetime, timedelta
import re

def EveryDay():
	#Get all ETLs that will be actualized dayly
	daily_etl=ETLS.objects.filter(update_period='D')
	for ETL in daily_etl:
		view_data=getView(ETL.view)
		info=UpdateDataset(view_data,ETL.dataset_id)
		if info=="OK":
			data=ETLS.objects.get(dataset_id=ETL.dataset_id)
			ip=get_client_ip(request)
			data.ip_address=ip
			data.save() 

def Updater():
	etl_list=ETLS.objects.all().exclude(update_period=None)
	for ETL in etl_list:
		print('faltan %s' %(ETL.next_update-datetime.now()))
		#Checking is
		if ETL.next_update-datetime.now() <= timedelta(minutes=3):
			#getting update period
			period=ETL.update_period
			#spliting numbers from letters
			integer=int(re.findall('\d+',period)[0])
			time_interval=re.findall('[A-Z]',period)[0]
			print(integer)
			print(time_interval)
			#Creating a time delta
			if time_interval[0]=='D':
				delta=timedelta(days=integer)
			elif time_interval=='M':
				delta=timedelta(days=integer*30)
			elif time_interval=='H':
				delta=timedelta(hours=integer)
			else:
				delta=timedelta()
			# getting next update
			next_update=datetime.now()+delta
			#msg='Se ha actualizado la ETL con nombre %s, \n siguiente actualización: %s' %(ETL.title, next_update)
			#send_mail('Prueba de Contrab',
			#	msg,
			#	'german0917@gmail.com',
			#	['gamonsalve@uninorte.edu.co'],
			#	fail_silently=False)
			data=ETLS.objects.get(dataset_id=ETL.dataset_id)
			data.next_update=next_update
			#data.save()
			view_data=getView(ETL.view)
			info=UpdateDataset(view_data,ETL.dataset_id)
			if info=="OK":
				#data=ETLS.objects.get(dataset_id=ETL.dataset_id)
				data.save()
				print('updated')