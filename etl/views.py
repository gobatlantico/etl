from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import send_mail
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password, check_password
# from .forms import ExcelUpload ,SheetSelection, ColumnsSelection
# from .forms import DatasetSelection, Sheet, DatasetDelete
# from .forms import LoginForm, NewUser, EditUser, ResetEmail
# from .forms import ChangePassword, Secretaries, ResetPassword
# from .models import Categories, Datasets, Users, Token
# from .datos import Sheets, CreateCategories, Columns, FinalExcel, UploadDataset
# from .datos import get_client_ip, DatasetColumns, ModifyDataset, getDataset
# from .datos import DeleteDataset, CreateSecretaries, Public, Private
from .datos import *
from .models import *
from .forms import *
import os
import json
import random
import string
from datetime import datetime, timedelta
import pandas as pd
import cx_Oracle


#________________________________________ 
#----------------------------------------   
#ACCESS VALIDATION
#________________________________________
#----------------------------------------

def LoginValidation(view):
    def wrap(request, *args, **kwargs):
        #Login check
        try:
            if request.session['Logged']==True:
                #if exists and it's True, continue
                return view(request, *args, **kwargs)
            elif request.session['logged']==False:
                #redirecting to login if it's False
                return redirect('/')
        except:
            #if the user did not logged, create de sessión as False
            print('user not logged')
            request.session['Logged']=False
            return redirect('/')
            #End Login check
    return wrap

#Original LoginValidations
# #Login check
    # try:
    #     if request.session['Logged']==True:
    #         #if exists and it's True do nothing
    #         pass
    #     elif request.session['logged']==False:
    #         #redirecting to login if it's False
    #         return redirect('/')
    # except:
    #     #if the user did not logged, create de sessión as False
    #     request.session['Logged']=False
    #     return redirect('/')
    # #End Login Check

#________________________________________ 
#----------------------------------------   
#View used to login in the website
#________________________________________
#----------------------------------------


# Create your views here.

def login(request):
    #print(request.user)
    try:
        if request.session['Logged']:
            return redirect('/options')
    except:
        pass
    info=''
    if request.method=='POST':
        form= LoginForm(request.POST)
        #If there are Errors with the email...
        if form.errors.as_data():
            for e in form.errors['email'].as_data():
                e=str(e)
                e=e[2:len(e)-2]
                messages.add_message(request, messages.ERROR,e)

        if form.is_valid():
            Email=form.cleaned_data['email']
            Password=form.cleaned_data['password']
            try:
                LogData=Users.objects.filter(user=Email)
                if LogData[0].state=='I':
                    messages.add_message(request, messages.ERROR,"El Usuario no está Activo")
                    return render(request,'etl/login.html',{'form':form})
                elif LogData[0].state!='A':
                    messages.add_message(request, messages.INFO,"Hay un Error con su Usuario o Contraseña")
                    return render(request,'etl/login.html',{'form':form})

                #Checking password
                if check_password(Password,LogData[0].password):
                    
                    request.session['user']=Email
                    request.session['name']=LogData[0].name
                    request.session['user_id']=LogData[0].id
                    request.session['Logged']=True
                    return redirect('/options')
                else:
                    #info='Hay un error con su usuario o contraseña'
                    #Error Notification with Notify.js
                    messages.add_message(request, messages.INFO,"Hay un Error con su Usuario o Contraseña")
                    return render(request,'etl/login.html',{'form':form})
            except:
                #info='Hay un error con su usuario o contraseña'
                #Error Notification with Notify.js 
                messages.add_message(request, messages.INFO,"Hay un Error con su Usuario o Contraseña")
                return render(request,'etl/login.html',{'form':form})

    else:
        form=LoginForm()
    return render(request,'etl/login.html',{'form':form})


#View that allows the user to weather upload an excel or upload from a database
@LoginValidation
def options(request):
    
    #admin options
    UserData=Users.objects.filter(user=request.session['user'])     
    if UserData[0].admin:
        admin=True
        request.session['admin']=admin
        return render(request,'etl/options.html',{'admin':admin})
    else:
        admin=False
        request.session['admin']=admin
        return render(request,'etl/options.html',{'admin':admin})

@LoginValidation
def logout(request):
    logout(request)
    return redirect('/')

    

#________________________________________ 
#----------------------------------------   
#Views used in CREATE DATASET
#________________________________________
#----------------------------------------

#Loading Excel File /loadexcel
@LoginValidation
def LoadExcel(request):    

    if request.method == 'POST':
        form = ExcelUpload(request.POST, request.FILES)
        if form.is_valid():
            #Get File from the form
            ExcelFile=request.FILES['ExcelFile']
            #Validating File
            if ExcelFile.name.find(".xls")==-1:
                print("NO EXCEL FILE")
                messages.add_message(request, messages.ERROR,"Seleccioné una archivo válido (.xls o .xlsx)")
                return redirect("/loadexcel")
            #Saving the excel file
            rootpath=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Excel')
            fs=FileSystemStorage(location=rootpath)
            #delete de file if exist
            fs.delete(ExcelFile.name)
            filename=fs.save(ExcelFile.name,ExcelFile)
            sheetnames=Sheets(ExcelFile.name)
            #Saving Sessions
            request.session['sheetnames']=sheetnames
            request.session['ExcelName']=ExcelFile.name
            request.session['Uploaded']=True
            #request.session['user']='UsuarioPruebas'
            
            return redirect("/metadataexcel")
    else:
        form = ExcelUpload()
    #Deleting a file that will not be used
    try:
        if request.session['Uploaded']:
            rootpath=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Excel')
            fs=FileSystemStorage(location=rootpath)
            fs.delete(request.session['ExcelName'])
    except:
        print('Not File')
    request.session['Uploaded']=False
    return render(request,'etl/loadexcel.html',{'form':form})

#Simplified metadata form
@LoginValidation
def metadataexcel(request):

    if request.method=='POST':
        form=SheetSelection(request.POST, sheetlist=request.session['sheetnames'])
        if form.is_valid():
            #getting data from the form and Saving sessions to use it later
            sheet=form.cleaned_data['sheet']
            request.session['sheet']=sheet
            title=form.cleaned_data['title']
            request.session['title']=title
            category=form.cleaned_data['category']
            request.session['category']=category
            description=form.cleaned_data['description']
            request.session['description']=description
            tags=form.cleaned_data['tags']
            request.session['tags']=tags
            return redirect("/pickcolumns")
    else:
        form=SheetSelection(sheetlist=request.session['sheetnames'])
    return render(request, 'etl/metadataexcel.html',{'form':form})

#Select columns
@LoginValidation 
def pickcolumns(request):


    columnslist,ExcelFile=Columns(request.session['ExcelName'],request.session['sheet'])
    form=ColumnsSelection(columnslist=columnslist)
    #Replacing NaN for ""
    ExcelFile=ExcelFile.replace(pd.np.nan,'', regex=True)
    #Showing all rows Excel file
    ExcelFile=ExcelFile.to_html(classes='table-striped " id = "my_table',index=False)
    if request.method=='POST':
        form=ColumnsSelection(request.POST  ,columnslist=columnslist)
        #get selection
        if form.is_valid():
            columns=form.cleaned_data['columns']
            request.session['columns']=columns
            print(columns)
            return redirect('/preview')
        else:
            #Looking for error messages 
            if form.errors.as_data():
                for e in form.errors['columns'].as_data():
                    e=str(e)
                    e=e[2:len(e)-2]
                    messages.add_message(request, messages.ERROR,e)
    return render(request,'etl/pickcolumns.html',{'form':form,'ExcelFile':ExcelFile})

#Preview data before upload
@LoginValidation
def preview(request):

    if request.method=='POST':
        ExcelFile=FinalExcel(request.session['ExcelName'],
                                request.session['sheet'],
                                request.session['columns'])
        
        
        info,dataset_id=UploadDataset(ExcelFile,request.session['title'],
                                request.session['description'],
                                request.session['category'],
                                request.session['tags'])
        if info=='OK':
            #Saving info in the data base
            ip=get_client_ip(request)
            UserData=Users.objects.only('id').get(user=request.session['user'])
            data=Datasets(user=UserData,
                            ip_address=ip,
                            title=request.session['title'],
                            dataset_id=dataset_id)
            data.save()
            #delete de file to avoid server overload
            rootpath=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Excel')
            fs=FileSystemStorage(location=rootpath)
            fs.delete(request.session['ExcelName'])
            user=request.session['user']
            user_id=request.session['user_id']
            name=request.session['name']
            admin=request.session['admin']
            #delete all sessions 
            request.session.flush()
            #Saving needed sessions
            #request.session['Saved']=True
            request.session['user']=user
            request.session['user_id']=user_id
            request.session['name']=name
            request.session['admin']=admin
            request.session['Logged']=True
            messages.add_message(request, messages.SUCCESS,
                                "Sus datos fueron cargados a datos.gov.co") 
            return redirect('/loadexcel')
        else:
            #Handling errors in uploading data 
            #request.session['Saved']=False
            messages.add_message(request, messages.ERROR,
                                "Ocurrio un Error subiendo sus datos a datos.gov.co")
            return redirect('/loadexcel')

    ExcelFile=FinalExcel(request.session['ExcelName'],
                            request.session['sheet'],
                            request.session['columns'])
    #Replacing NaN for ""
    ExcelFile=ExcelFile.replace(pd.np.nan,'', regex=True)
    # Showing the entire ExcelFile
    ExcelFile=ExcelFile.to_html(classes='table-striped " id = "my_table',index=False)
    return render(request,'etl/preview.html',{'ExcelFile':ExcelFile,
                                            'title':request.session['title'],
                                            'description':request.session['description'],
                                            'tags':request.session['tags'],
                                            'category':request.session['category']})









#________________________________________ 
#----------------------------------------   
#Views used in MODIFY DATASET
#________________________________________
#----------------------------------------
@LoginValidation
def  selectmodify(request):
    print("seleccionado")
    #-----------------------
    #POST GET BY JQUERY
    if request.method=='GET':
        id_number= request.GET.get("celda", None)
        print("get excuted")
        print(id_number)
        if id_number:            
            request.session['dataset_id']=id_number
            print('Se creo la sesion')
    

    #------------------------------------
    print("tablas")
    #getting data from DB and Checking user restriction
    UserData=Users.objects.filter(user=request.session['user'])
    if UserData[0].admin:
        DatasetsTable=Datasets.objects.all().values('user_id__user', 'user__name','dataset_id',
                                                'title','created','modified', 'public')
    else:

        DatasetsTable=Datasets.objects.filter(user=request.session['user_id']).values(
                                                'user_id__user','user__name','dataset_id',
                                                'title','created','modified', 'public')
    table=pd.DataFrame(list(DatasetsTable))
  
    if list(table)==[]:
        table=''
    else:
        # Changing True for Si and False for NO
        table['public']=table['public'].map({False:"No",True:"Si"})
        #Renaming columns
        table=table.rename(columns={'user_id__user':'Usuario','user__name':'Nombre','dataset_id':'id','title':'Título',
                                'public':'Público','created':'Creado','modified':'Modificado'})
        #Generate HTML Table
        table=table.to_html(classes='display table-responsive" id = "my_table" style="width:100%',
                            index=False) 
    print("rendering")    
    return render(request,'etl/selectmodify.html',{'table':table})


#View that loads an Excel to modify a dataset   
@LoginValidation
def modify(request):

    if request.method=='POST':
        form=DatasetSelection(request.POST,request.FILES)#,user=request.session['user'])
        if form.is_valid():
            #Get File from the form
            ExcelFile=request.FILES['ExcelFile']
            #Validating File
            if ExcelFile.name.find(".xls")==-1:
                print("NO EXCEL FILE")
                messages.add_message(request, messages.ERROR,"Seleccioné una archivo válido (.xls o .xlsx)")
                return redirect("/modify")
            #Saving the excel file
            rootpath=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Excel')
            fs=FileSystemStorage(location=rootpath)
            #delete de file if exist
            fs.delete(ExcelFile.name)
            filename=fs.save(ExcelFile.name,ExcelFile)
            sheetnames=Sheets(ExcelFile.name)
            request.session['sheetnames']=sheetnames
            request.session['ExcelName']=ExcelFile.name
            #request.session['dataset_id']=list(Datasets.objects.values_list('dataset_id',flat=True).filter(title=dataset))
            request.session['Uploaded']=True
            return redirect('/modifysheet')
    else:
        form=DatasetSelection()#user=request.session['user'])
    #Deleting a file that will not be used
    try:
        if request.session['Uploaded']:
            rootpath=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Excel')
            fs=FileSystemStorage(location=rootpath)
            fs.delete(request.session['ExcelName'])
    except:
        print('Not File')

    
    
    return render(request,'etl/modify.html',{'form':form}) 



#View that loads an Excel to modify a dataset
@LoginValidation
def modifysheet(request):

    if request.method=='POST':
        form=Sheet(request.POST,sheetlist=request.session['sheetnames'])
        if form.is_valid():
            sheet=form.cleaned_data['sheet']
            request.session['sheet']=sheet
            columnslist,ExcelFile=Columns(request.session['ExcelName'],request.session['sheet'])
            dataset_columns, columns=DatasetColumns(request.session['dataset_id'])              
            try:
                # Alert Excel problems, doble column, empty cells
                #Analizing if the columns exist in the uploaded file
                inter=set(dataset_columns) & set(columnslist)
                if len(inter)==len(dataset_columns):
                    #if exist save columns
                    request.session['columns']=columns
                    return redirect('/modifypreview')
                else:
                    
                    #Add File Error
                    #Creating Error Message
                    messages.add_message(request,messages.ERROR,
                            "Las columnas de los datos seleccionados no coinciden con las columnas del conjunto de datos a modificar")   
                    return redirect('/selectmodify')
            except BaseException as e:
                #if there is a problem with the file redirect to modify
                print('ERROR')
                print(str(e))
                
                messages.add_message(request,messages.ERROR,"Hay un error con el archivo cargado")   
                return redirect('/selectmodify')

    form=Sheet(sheetlist=request.session['sheetnames'])
    return render(request,'etl/modifysheet.html',{'form':form})



#View that previews all the data that will be updated to datos.gov.co
@LoginValidation
def modifypreview(request):

    if request.method=='POST':
        ExcelFile=FinalExcel(request.session['ExcelName'],
                                request.session['sheet'],
                                request.session['columns'])
     
        
        info=ModifyDataset(ExcelFile, request.session['dataset_id'])
        if info=='OK':
            #After a modification, the dataset will be private
            private=Private(request.session['dataset_id'])
            #delete de file to avoid server overload
            rootpath=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Excel')
            fs=FileSystemStorage(location=rootpath)
            fs.delete(request.session['ExcelName'])
            #Saving changes info in the data base
            # Gettin DATASETS object
            data=Datasets.objects.get(dataset_id=request.session['dataset_id'])
            ip=get_client_ip(request)
            user=request.session['user']
            user_id=request.session['user_id']
            name=request.session['name']
            admin=request.session['admin']
            data.ip_address=ip
            if private =='OK':
                data.public=False
                messages.add_message(request,messages.SUCCESS, "Sus datos ahora son privados")
            data.save() 
            #delete all sessions 
            request.session.flush()
            #Saving needed sessions
            
            request.session['user']=user
            request.session['user_id']=user_id
            request.session['name']=name
            request.session['admin']=admin
            request.session['Logged']=True
            messages.add_message(request,messages.SUCCESS, "Sus datos fueron actualizados en datos.gov.co")
            return redirect('/selectmodify')
        else:
            #if there is an error send messages to selectmodify
            
            messages.add_message(request,messages.ERROR,"Sus datos no fueron actualizados en datos.gov.co")
            return redirect('/selectmodify')

    ExcelFile=FinalExcel(request.session['ExcelName'],
                            request.session['sheet'],
                            request.session['columns'])
    #Replacing NaN for ""
    ExcelFile=ExcelFile.replace(pd.np.nan,'', regex=True)
    # Showing the entire ExcelFile
    ExcelFile=ExcelFile.to_html(classes='table-striped " id = "my_table',index=False)
    DatasetInfo=Datasets.objects.filter(dataset_id=request.session['dataset_id'])
    if DatasetInfo[0].public:
        public="Publico"
    else:
        public="Privado"
    return render(request,'etl/modifypreview.html',{'ExcelFile':ExcelFile,
                                                    'title':DatasetInfo[0].title,
                                                    'created':DatasetInfo[0].created,
                                                    'modified':DatasetInfo[0].modified,
                                                    'public':public})









#________________________________________ 
#----------------------------------------   
#Views used in DELETE DATASET
#________________________________________
#----------------------------------------


#View that allows to select a datase that will be deleted, Using DATATABLES
@LoginValidation
def  selectdelete(request):

    #-----------------------
    #POST GET BY JQUERY
    if request.method=='GET':
        id_number= request.GET.get("celda", None)
        print('dateadef')
        print(id_number)
        if id_number:            
            request.session['dataset_id']=id_number

           
    

    #------------------------------------
    #getting data from DB
    #getting data from DB and Checking user restriction
    UserData=Users.objects.filter(user=request.session['user'])
    if UserData[0].admin:
        DatasetsTable=Datasets.objects.all().values('user_id__user','user__name' ,'dataset_id',
                                                'title','created','modified', 'public')
        ETLTable=ETLS.objects.all().values('user_id__user', 'user__name','dataset_id',
                                                'title','created','modified', 'public')
    else:

        DatasetsTable=Datasets.objects.filter(user=request.session['user_id']).values(
                                                'user_id__user','user__name','dataset_id',
                                                'title','created','modified', 'public')
        ETLTable=ETLS.objects.filter(user=request.session['user_id']).values(
                                                'user_id__user','user__name','dataset_id',
                                                'title','created','modified', 'public')
    print('OK')
    tableD=pd.DataFrame(list(DatasetsTable))
    tableD= tableD.assign(Tipo=pd.Series('Dataset',index=tableD.index))
    tableE=pd.DataFrame(list(ETLTable))
    tableE = tableE.assign(Tipo=pd.Series('ETL',index=tableE.index))
    table=pd.concat([tableD, tableE])
    print('OK')
    print(list(table))    
    if list(table)==['Tipo']:
        #The table is empty 
        table=''
    else:
        # Changing True for Si and False for NO
        table['public']=table['public'].map({False:"No",True:"Si"})
        #Renaming columns
        table=table.rename(columns={'user_id__user':'Usuario', 'user__name':'Nombre' ,'dataset_id':'id','title':'Título',
                                    'public':'Público','created':'Creado','modified':'Modificado'})   
        #Generate HTML Table 
        table=table.to_html(classes='display table-responsive" id = "my_table" style="width:100%',
                            index=False) 

    return render(request,'etl/selectdelete.html',{'table':table})


#View that deletes a dataset on datos.gov.co
@LoginValidation
def deletepreview(request):

    if request.method=='POST':
        print('post')
        info=DeleteDataset(request.session['dataset_id'])
        if info=='OK':
            user=request.session['user']
            user_id=request.session['user_id']
            name=request.session['name']
            admin=request.session['admin']
            # delete database register on DATASET table or ETLS table. 
            Datasets.objects.filter(dataset_id=request.session['dataset_id']).delete()
            ETLS.objects.filter(dataset_id=request.session['dataset_id']).delete()
            #delete all sessions 
            request.session.flush()
            #Saving needed sessions
            request.session['Saved']=True
            request.session['user']=user
            request.session['name']=name
            request.session['admin']=admin
            request.session['user_id']=user_id
            request.session['Logged']=True
            messages.add_message(request,messages.SUCCESS, "Conjunto de Datos eliminado exitosamente")            
            return redirect('/selectdelete')
        else:
            messages.add_message(request,messages.ERROR,"No se pudo eliminar el Conjunto de Datos seleccionado")
            return redirect('/selectdelete')
    else:
        try:
            # If the data is stored in dataset model
            DatasetsData=Datasets.objects.filter(dataset_id=request.session['dataset_id'])
            title=DatasetsData[0].title
        except:
            # if the data is stored on ETLS models
            DatasetsData=ETLS.objects.filter(dataset_id=request.session['dataset_id'])
            title=DatasetsData[0].title
        dataset_id=request.session['dataset_id']
        table,vistas=getDataset(dataset_id)
        if DatasetsData[0].public:
            public="Publico"
        else:
            public="Privado"

    return render(request,'etl/deletepreview.html',{'title':title,
                                                    'dataset_id':dataset_id,
                                                    'table':table,
                                                    'created':DatasetsData[0].created,
                                                    'modified':DatasetsData[0].modified,
                                                    'public':public,
                                                    'visit':vistas})

#________________________________
#--------------------------------
#User Profile administration
#--------------------------------
#________________________________

@LoginValidation
def changepass(request):

    if request.method=='POST':
        form=ChangePassword(request.POST)
        if form.is_valid():
            UserData=Users.objects.filter(user=request.session['user'])
            if check_password(form.cleaned_data['oldpass'],UserData[0].password):
                if form.cleaned_data['newpass']==form.cleaned_data['newpass2']:
                    try:
                        #Password encryption
                        password=make_password(form.cleaned_data['newpass'])
                        UserData=Users.objects.get(id=request.session['user_id'])
                        #Changing password values
                        UserData.password=password
                        #saving Objects
                        UserData.save()
                        
                        messages.add_message(request, messages.SUCCESS, "Se editó la contraseña con éxito")
                        return redirect('/options')
                    except:
                        
                        messages.add_message(request, messages.ERROR,"Ocurrió un error")
                        return redirect('/options')

                else:
                    messages.add_message(request, messages.ERROR,'Las contraseñas no coinciden')

            else:
                messages.add_message(request, messages.ERROR,'Contraseña Incorrecta')
    else:
        form=ChangePassword()
    return render(request,'etl/changepass.html',{'form':form})


#_______________________________________________
#-----------------------------------------------
# ADMIN ACCESS VALIDATION
#_______________________________________________
#-----------------------------------------------

def AdminValidation(view):
    def wrap(request, *args, **kwargs):
            #Start Login check
        try:
            #looking for user permissons
            UserData=Users.objects.filter(user=request.session['user'])
            print(UserData[0].admin)
            if UserData[0].admin==False and request.session['Logged']==True:
                return redirect('/options')
            elif request.session['Logged']==False:
                return redirect('/')
            else:
                return view(request, *args, **kwargs)
        except:
            #if the user did not logged, create de sessión as False
            request.session['Logged']=False
            return redirect('/')
        #End Login Check
    return wrap


#ORIGINAL ADMIN VALIDATION
# #Start Login check
    # try:
    #     #looking for user permissons
    #     UserData=Users.objects.filter(user=request.session['user'])
    #     if UserData[0].admin==False and request.session['Logged']==True:
    #         return redirect('/options')
    #     elif request.session['Logged']==False:
    #         return redirect('/')
    # except:
    #     #if the user did not logged, create de sessión as False
    #     request.session['Logged']=False
    #     return redirect('/')
    # #End Login Check    
    
#________________________________________ 
#----------------------------------------   
#ADMIN views
#________________________________________
#----------------------------------------

#view that creates a user
@AdminValidation
def createusers(request):

    info=''
    if request.method=='POST':
        form=NewUser(request.POST)
        #If there are Errors with the email...
        if form.errors.as_data():
            for e in form.errors['email'].as_data():
                e=str(e)
                e=e[2:len(e)-2]
                messages.add_message(request, messages.ERROR,e)
        if form.is_valid():
            email=form.cleaned_data['email']
            name=form.cleaned_data['name']
            password=form.cleaned_data['password']
            admin=form.cleaned_data['admin']
            #since it is a foreign key, it is necessary to create a
            #Secretary instance
            sec_id=form.cleaned_data['secretary']
            sec=Secretaries.objects.only('id').get(id=sec_id)
            if password==form.cleaned_data['password2']:
                try:
                    #Password encryption
                    password=make_password(password)
                    data=Users(user=email,name=name,password=password,secretaria=sec, admin=admin)
                    data.save()
                    messages.add_message(request, messages.SUCCESS, "Se creó el usuario con éxito")
                    return redirect("/createusers")
                except:
                    messages.add_message(request, messages.ERROR,'Este e-mail ya está registrado')
            else:
                messages.add_message(request, messages.ERROR,'Las contraseñas no coinciden')
            
    else:
        form=NewUser()
    return render(request, 'etl/createusers.html',{'form':form})

#view shows users
@AdminValidation
def selectusers(request):
    
    #-----------------------
    #POST GET BY JQUERY
    if request.method=='GET':
        id_number= request.GET.get("celda", None)
        if id_number:            
            request.session['edit_id']=id_number
           
    

    #------------------------------------
    UserTable=Users.objects.all().values('id','user', 'name','state','created',
                                            'modified','secretaria_id__secretary')
    table=pd.DataFrame(list(UserTable))
    #Renaming columns
    table=table.rename(columns={'user':'Usuario', 'name':'Nombre', 'secretaria_id__secretary':'Secretaria',
                                'state':'Estado','created':'Creado','modified':'Modificado'})
    #Slice the table
    #table=table[['id','Usuario','Secretaria',
    #            'Estado','Creado','Modificado']]
    #A=Activo, I=Inactivo, D=Eliminado
    table['Estado']=table['Estado'].map({'A':'Activo','I':'Inactivo','D':'Eliminado'})
    #Generate HTML Table
    table=table.to_html(classes='display table-responsive" id = "my_table" style="width:100%',
                        index=False)
 
    return render(request,'etl/selectusers.html',{'table':table})


#View that modify a selected user
@AdminValidation
def modifyusers(request):
    
    if request.method=='POST':
        form=EditUser(request.POST, user_id=request.session['edit_id'])
        #Wrong Email Validations
        if form.errors.as_data():
            for e in form.errors['email'].as_data():
                e=str(e)
                e=e[2:len(e)-2]
                messages.add_message(request, messages.ERROR,e)
        if form.is_valid():
            email=form.cleaned_data['email']
            name=form.cleaned_data['name']
            password=form.cleaned_data['password']
            password2=form.cleaned_data['password2']
            sec_id=form.cleaned_data['secretary']
            #since it is a foreign key, it is necessary to create a
            #Secretary instance
            sec=Secretaries.objects.only('id').get(id=sec_id)
            state=form.cleaned_data['state']
            admin=form.cleaned_data['admin']
            try:
                #Getting Existing objects
                data=Users.objects.get(id=request.session['edit_id'])
                #Changing object values
                data.user=email
                data.name=name
                data.secretaria=sec
                data.state=state
                data.admin=admin
                #Checking if the password will change
                if password==form.cleaned_data['password2'] and password!='' and password2!='':
                    if password==form.cleaned_data['password2']:
                        # Password encryption
                        password=make_password(password)
                        data.password=password
                    else:
                        messages.add_message(request, messages.ERROR,'Las contraseñas no coinciden')
                #saving Objects
                data.save()
                messages.add_message(request, messages.SUCCESS,'Se editó el usuario con éxito')
                return redirect('selectusers')
            except:
                messages.add_message(request, messages.ERROR,'Este e-mail ya está registrado')     
            # else:
            #     messages.add_message(request, messages.ERROR,'Las contraseñas no coinciden')

    else:
        form=EditUser(user_id=request.session['edit_id'])
    return render(request,'etl/modifyusers.html',{'form':form})

@AdminValidation
def databaseoptions(request):
    return render(request,'etl/databaseoptions.html')
#View that select a DataSet
@AdminValidation
def selectdata(request):

    #-----------------------
    #POST GET BY JQUERY
    if request.method=='GET':
        id_number= request.GET.get("celda", None)
        print('dateadef')
        print(id_number)
        if id_number:            
            request.session['dataset_id']=id_number

           
    

    #------------------------------------
    #getting data from DB
    #getting data from DB and Checking user restriction
    UserData=Users.objects.filter(user=request.session['user'])
    if UserData[0].admin:
        DatasetsTable=Datasets.objects.all().values('user_id__user','user__name','dataset_id',
                                                'title','created','modified', 'public')
        ETLTable=ETLS.objects.all().values('user_id__user','user__name','dataset_id','title','created','modified', 'public')
    else:

        DatasetsTable=Datasets.objects.filter(user=request.session['user_id']).values(
                                                'user_id__user','user__name','dataset_id',
                                                'title','created','modified','public')
        ETLTable=ETLS.objects.filter(user=request.session['user_id']).values(
                                                'user_id__user','user__name','dataset_id',
                                                'title','created','modified','public')
    tableD=pd.DataFrame(list(DatasetsTable))
    tableD = tableD.assign(Tipo=pd.Series('Dataset',index=tableD.index))
    tableE=pd.DataFrame(list(ETLTable))
    tableE = tableE.assign(Tipo=pd.Series('ETL',index=tableE.index))
    table=pd.concat([tableD, tableE]) 
    if list(table)==['Tipo']:
        #The table is empty 
        table=''
    else:
        # Changing True for Si and False for No
        table['public']=table['public'].map({False:"No",True:"Si"})
        #Renaming columns
        table=table.rename(columns={'user_id__user':'Usuario','user__name':'Nombre','dataset_id':'id','title':'Título',
                                    'public':'Público','created':'Creado','modified':'Modificado'})   
        #Generate HTML Table 
        table=table.to_html(classes='display table-responsive" id = "my_table" style="width:100%',
                            index=False) 

    return render(request,'etl/selectdata.html',{'table':table})

#Preview data that will be Public/private
@AdminValidation
def permissonpreview(request):
    if request.method=='POST':
        return redirect(datamanager)
    else:
        try:
            # If the data is stored in dataset model
            DatasetsData=Datasets.objects.filter(dataset_id=request.session['dataset_id'])
            title=DatasetsData[0].title
        except:
            # if the data is stored on ETLS models
            DatasetsData=ETLS.objects.filter(dataset_id=request.session['dataset_id'])
            title=DatasetsData[0].title
        dataset_id=request.session['dataset_id']
        table,vistas=getDataset(dataset_id)
        if DatasetsData[0].public:
            public="Publico"
        else:
            public="Privado"

    return render(request,'etl/permissonpreview.html',{'title':title,
                                                    'dataset_id':dataset_id,
                                                    'table':table,
                                                    'created':DatasetsData[0].created,
                                                    'modified':DatasetsData[0].modified,
                                                    'public':public,
                                                    'visit':vistas})
#View that publish and set private Datasets    
@AdminValidation
def datamanager(request):
    
    try:
        # If the data is stored in dataset model
        Data=Datasets.objects.filter(dataset_id=request.session['dataset_id'])
        dataset=Datasets.objects.get(id=Data[0].id)
    except:
        # if the data is stored on ETLS models
        Data=ETLS.objects.filter(dataset_id=request.session['dataset_id'])
        dataset=ETLS.objects.get(id=Data[0].id)

    if Data[0].public:
        info=Private(request.session['dataset_id'])
        if info=='OK':
            dataset.public=False
            dataset.save()
            messages.add_message(request,messages.SUCCESS, "Sus datos ahora son privados") 
        else:
            messages.add_message(request,messages.ERROR, "Ocurrió un error al intentar cambiar los permisos") 
    else:
        info=Public(request.session['dataset_id'])
        if info=='OK':
            dataset.public=True
            dataset.save()
            messages.add_message(request,messages.SUCCESS, "Sus datos ahora son públicos") 
        else:
            messages.add_message(request,messages.ERROR, "Ocurrió un error al intentar cambiar los permisos") 
    return redirect("selectdata")

#________________________________________ 
#----------------------------------------   
#RESET PASSWORD
#________________________________________
#----------------------------------------

#View that Generate a Token and Send an EMAIL
def password_reset(request):
    if request.method=='POST':
        form=ResetEmail(request.POST)
        #If there are Errors with the email...
        if form.errors.as_data():
            for e in form.errors['email'].as_data():
                e=str(e)
                e=e[2:len(e)-2]
                messages.add_message(request, messages.ERROR,e)

        if form.is_valid():
            #Generating Token and saving in a DataBase
            token=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            #getting UserObject, That is a user that is in de DB
            try:
                UserData=Users.objects.only('id').get(user=form.cleaned_data['email'])
                data=Token(user=UserData,token=token)
                data.save()
                UserData=Users.objects.filter(user=form.cleaned_data['email'])
                rootpath=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'ResetEmail.txt')
                msg=open(rootpath, 'r').read() %(UserData[0].name,token)
                send_mail(
                            'REESTABLECER CONTRASEÑA',
                            msg,
                            'german0917@gmail.com',
                            [form.cleaned_data['email']],
                            fail_silently=False,
                        )
            except BaseException as e:
                error=str(e)
                print('Error description:')
                print(error)
                messages.add_message(request, messages.ERROR,'No existe este correo en la base de datos')
                return redirect('/password_reset')
            
            return redirect('/password_reset_done')
    form=ResetEmail()
    return render(request,'etl/password_reset.html',{'form':form})
#Show succes at reset Password
def password_reset_done(request):
    return render(request,'etl/password_reset_done.html')


def password_reset_confirm(request,token):
    #check if the TOKEN Exist
    if  list(Token.objects.filter(token=token))==[]:
        return redirect('/')

    if request.method=='POST':
        form=ResetPassword(request.POST)
        data_id=Token.objects.filter(token=token)
        #Getting Existing objects
        data=Users.objects.get(id=data_id[0].user_id)
        if form.is_valid():
            password=form.cleaned_data['newpass']
            password2=form.cleaned_data['newpass2']
            if password==password2:
                password=make_password(password)
                data.password=password
                #saving password change
                data.save()
                #Deleting Token
                data_id.delete()
                return redirect('/password_reset_complete')
            else:
                messages.add_message(request, messages.ERROR,'Las contraseñas no coinciden')
    form=ResetPassword()
    return render(request,'etl/password_reset_confirm.html',{'form':form})


def password_reset_complete(request):
    return render(request,'etl/password_reset_complete.html')

#________________________________________ 
#----------------------------------------   
#Automated Dataset from ORACLE DB
#________________________________________
#----------------------------------------

#Selecting the Oracle db view
@AdminValidation
def selectdatabase(request):
    if request.method=='GET':
        id_number= request.GET.get("celda", None)
        print(id_number)
        if id_number:            
            request.session['view_name']=id_number
    #getting user viewlist
    table=ViewList()
    #Generate HTML Table 
    table=table.to_html(classes='display table-responsive" id = "my_table" style="width:100%',
                            index=False) 
    return render(request,'etl/selectdatabase.html',{'table':table})
#Metadata form
@AdminValidation
def metadataetl(request):
    
    if request.method=='POST':
        form=ETLform(request.POST)
        if form.is_valid():
            #getting data from the form
            title=form.cleaned_data['title']
            request.session['title']=title
            description=form.cleaned_data['description']
            request.session['description']=description
            tags=form.cleaned_data['tags']
            request.session['tags']=tags
            category=form.cleaned_data['category']
            request.session['category']=category
            update=form.cleaned_data['update']
            request.session['update']=update
            integer=form.cleaned_data['integer']
            request.session['integer']=integer
            return redirect('etlpreview')
    else:
        form=ETLform() 
    return render(request,'etl/metadataetl.html',{'form':form})

#Preview
@AdminValidation
def etlpreview(request):
    #DATA
    view_data=getView(request.session['view_name'])
    table=view_data.to_html(classes='display table-responsive" id = "my_table" style="width:100%',
                            index=False)
    #METADATA
    title=request.session['title']
    description=request.session['description']
    tags=request.session['tags']
    category=request.session['category']
    update=request.session['update']
    integer=request.session['integer']
    if update=='D':
        #Update every X days
        update_period='%sD' %(integer)
        next_update=datetime.now()+timedelta(days=integer)
        if integer!=1:
            update='Cada %s día' %(integer)
        else:
            update='diariamente'
    elif update=='H':
        #update every X hours
        next_update=datetime.now()+timedelta(hours=integer)
        update_period='%sH' %(integer)
        if integer!=1:
            update='Cada %s horas' %(integer)
        else:
            update='Cada Hora'
    elif update=='M':
        #update every X months (1month=30days)
        update_period='%sM' %(integer)
        next_update=datetime.now()+timedelta(days=integer*30)
        if integer!=1:
            update='Cada %s Meses' %(integer)
        else:
            update='Mensualmente'
    else:
        update='No se actualiza'
        update_period=None
        next_update=None
    # POST request    
    if request.method=='POST':
        info,dataset_id=CreateETL(view_data,title,description,category,tags)
        if info=='OK':
            #Saving info in the data base
            ip=get_client_ip(request)
            UserData=Users.objects.only('id').get(id=request.session['user_id'])
            data=ETLS(user=UserData,
                            ip_address=ip,
                            title=request.session['title'],
                            dataset_id=dataset_id,
                            next_update=next_update,
                            view=request.session['view_name'],
                            update_period=update_period)
            data.save()
            del request.session['view_name'];del request.session['update']
            del request.session['title']; del request.session['description'] 
            del request.session['tags']; del request.session['category']
            
            messages.add_message(request, messages.SUCCESS,'Se ha creado la ETL')
            return redirect('selectdatabase')
        else:
            messages.add_message(request, messages.ERROR,'Ocurrió un error creando la ETL')
            return redirect('selectdatabase')
    return render(request,'etl/etlpreview.html',{'title':title,
                                                'description':description,
                                                'tags':tags,
                                                'category':category,
                                                'update':update,
                                                'next_update':next_update,
                                                'table':table})

#Seletcting automated dataset
@AdminValidation
def selectETL(request):

    #-----------------------
    #POST GET BY JQUERY
    if request.method=='GET':
        id_number= request.GET.get("celda", None)
        print('dateadef')
        print(id_number)
        if id_number:            
            request.session['dataset_id']=id_number

           
    

    #------------------------------------
    #getting data from DB
    #getting data from DB and Checking user restriction
    UserData=Users.objects.filter(user=request.session['user'])
    if UserData[0].admin:
        ETLTable=ETLS.objects.all().values('user_id__user','user__name','dataset_id','title','created','modified', 'public')
    else:
        ETLTable=ETLS.objects.filter(user=request.session['user_id']).values(
                                                'user_id__user','user__name','dataset_id',
                                                'title','created','modified','public')
    table=pd.DataFrame(list(ETLTable))
    if list(table)==[]:
        #The table is empty 
        table=''
    else:
        # Changing True for Si and False for No
        table['public']=table['public'].map({False:"No",True:"Si"})
        #Renaming columns
        table=table.rename(columns={'user_id__user':'Usuario','user__name':'Nombre','dataset_id':'id','title':'Título',
                                    'public':'Público','created':'Creado','modified':'Modificado'})   
        #Generate HTML Table 
        table=table.to_html(classes='display table-responsive" id = "my_table" style="width:100%',
                            index=False)

    return render(request,'etl/selectETL.html',{'table': table})

#modify update_period
@AdminValidation
def modifyETL(request):

    if request.method=='POST':
        form=EditETL(request.POST)
        if form.is_valid():
            update=form.cleaned_data['update']
            integer=form.cleaned_data['integer']
            #Getting Existing ETL object
            data=ETLS.objects.get(dataset_id=request.session['dataset_id'])
            if update=='D':
                #Update every X days
                update_period='%sD' %(integer)
                next_update=datetime.now()+timedelta(days=integer)
                if integer!=1:
                    update='Cada %s día' %(integer)
                else:
                    update='diariamente'
            elif update=='H':
                #update every X hours
                next_update=datetime.now()+timedelta(hours=integer)
                update_period='%sH' %(integer)
                if integer!=1:
                    update='Cada %s horas' %(integer)
                else:
                    update='Cada Hora'
            elif update=='M':
                #update every X months (1month=30days)
                update_period='%sM' %(integer)
                next_update=datetime.now()+timedelta(days=integer*30)
                if integer!=1:
                    update='Cada %s Meses' %(integer)
                else:
                    update='Mensualmente'
            else:
                update='No se actualiza'
                update_period=None
                next_update=None
            data.update_period=update_period
            data.next_update=next_update
            data.save()
            messages.add_message(request,messages.SUCCESS, "Ha cambiado la frecuencia de actualización")
            return redirect('/selectETL')
    else:
        form=EditETL()
    return render(request,'etl/modifyETL.html',{'form':form})

#Update on Demand    
@AdminValidation
def updatenow(request):
    try:
        ETL=ETLS.objects.filter(dataset_id=request.session['dataset_id'])
        view_data=getView(ETL[0].view)
        info=UpdateDataset(view_data,ETL[0].dataset_id)
        if info=='OK':
            data=ETLS.objects.get(dataset_id=ETL[0].dataset_id)
            ip=get_client_ip(request)
            data.ip_address=ip
            data.save()
            messages.add_message(request,messages.SUCCESS, "Sus datos fueron actualizados")
            del request.session['dataset_id']
            return redirect('/selectETL')
    except BaseException as e:
        error=str(e)
        print('Error description:')
        print(error)
        messages.add_message(request,messages.ERROR, "Ocurrio un Error al actualizar sus datos")
        return redirect('/selectETL')
