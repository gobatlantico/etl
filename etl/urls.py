from django.conf.urls import include, url
from . import views

urlpatterns = [
        #url(r'^$', views.index),
        #View used to login to the website
        url(r'^$',views.login,name='login'),
        #View that allow the user to select and option
        url(r'^options/$',views.options, name='options'),
        #View used to logout
        url(r'^logout/$',views.logout,name='logout'),
        #View that upload the excel file to the server
        url(r'^loadexcel/$',views.LoadExcel, name='loadexcel'),
        #View that get metadata and data.
        url(r'^metadataexcel/$',views.metadataexcel, name='metadataexcel'),
        #View that allow the user to select columns
        url(r'^pickcolumns/$',views.pickcolumns, name='pickcolumns'),
        #View that Preview all the data that will be uploaded to datos.gov.co
        url(r'^preview/$',views.preview, name='preview'),
        #View that allows to select a datase that will be updated  
        url(r'^selectmodify/$',views.selectmodify, name='selectmodify'),
        #View that allows to select a datase that will be updated  
        url(r'^modify/$',views.modify, name='modify'),
        #View that load an Excel to modify a dataset
        url(r'^modifysheet/$',views.modifysheet, name='modifysheet'),
        #View that preview all the data that will be updated to datos.gov.co
        url(r'^modifypreview/$',views.modifypreview, name='modifypreview'),
        #View that allows to select a datase that will be deleted Using DataTables
        url(r'^selectdelete/$',views.selectdelete, name='selectdelete'), 
        #View that allows to select a datase that will be deleted
        #url(r'^delete/$',views.delete, name='delete'), 
        #View that deleted a dataset
        url(r'^deletepreview/$',views.deletepreview, name='deletepreview'),
        #View used to change password
        url(r'^changepass/$',views.changepass,name='changepass'),
        #View used to create new users ADMIN USE ONLY
        url(r'^createusers/$',views.createusers,name='createusers'),
        #View used to select  users ADMIN USE ONLY
        url(r'^selectusers/$',views.selectusers,name='selectusers'),
        #View used to modify  users ADMIN USE ONLY
        url(r'^modifyusers/$',views.modifyusers,name='modifyusers'),
        #View used to manage datasets  users ADMIN USE ONLY
        url(r'^selectdata/$',views.selectdata,name='selectdata'),
        #Preview data that will be Public/private
        url(r'^permissonpreview/$',views.permissonpreview,name='permissonpreview'),
        #View used to manage datasets  users ADMIN USE ONLY
        url(r'^datamanager/$',views.datamanager,name='datamanager'),
        #Form where the user submit the email address
        url(r'^password_reset/$',views.password_reset,name='password_reset'),
        #Success on password_reset
        url(r'^password_reset_done/$',views.password_reset_done,name='password_reset_done'),
        #This view will validate the token and display a password form
        url(r'^password_reset_confirm/([a-zA-Z0-9]{8})/$',views.password_reset_confirm,name='password_reset_confirm'),
        #Page displayed to the user after the password was successfully changed.
        url(r'^password_reset_complete/$',views.password_reset_complete,name='password_reset_complete'),
        # Show database option: data management or data upload
        url(r'^databaseoptions/$',views.databaseoptions,name='databaseoptions'),
        #Show views on the DB.
        url(r'^selectdatabase/$',views.selectdatabase,name='selectdatabase'),
        #form with metadata
        url(r'^metadataetl/$',views.metadataetl,name='metadataetl'),
        #Show views on the DB.
        url(r'^etlpreview/$',views.etlpreview,name='etlpreview'),
        #Show views on the DB.
        url(r'^selectETL/$',views.selectETL,name='selectETL'),
        #Edit ETL VW update period.
        url(r'^modifyETL/$',views.modifyETL,name='modifyETL'),
        #Edit ETL VW update period.
        url(r'^updatenow/$',views.updatenow,name='updatenow'),


    ]