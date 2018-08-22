import json
from sodapy import Socrata
import pandas as pd
import os
import cx_Oracle
from .models import Categories, Secretaries, Users
#Getting data from configuration file
cfg=json.loads(open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'cfg.txt'),'r').read())

def Sheets(filename):
    path=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Excel/%s' % filename)
    ExcelFile=pd.read_excel(path,sheetname=None,index=False)
    sheets=list(ExcelFile)
    for i in range(0,len(sheets)):
        sheets[i]=(sheets[i],sheets[i])
    sheets=tuple(sheets)
    return sheets

def Columns(filename, sheet):
    path=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Excel/%s' % filename)
    #print(sheet)
    #print(filename)
    ExcelFile=pd.read_excel(path,sheetname=sheet,index=False)
    #print(ExcelFile)
    columns=list(ExcelFile)
    for i in range(0,len(columns)):
        columns[i]=(columns[i],columns[i])        
    return columns, ExcelFile

def FinalExcel(filename,sheet,columns):
    path=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Excel/%s' % filename)
    ExcelFile=pd.read_excel(path,sheetname=sheet,index=False)
    ExcelFile=ExcelFile[columns]
    return ExcelFile


def CreateMetadata(filename,sheetname,FirstCol,LastCol,tags,title):
    #Create Socrata client
    client=Socrata(cfg["web"],cfg["token"],username=cfg["email"],password=cfg["password"])
    #preparing Excel file
    parse_cols='%s:%s' %(FirstCol,LastCol)
    #getting path of the excel file
    path=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'documents/%s' % filename.replace(" ","_"))
    #Reading excel with Panda
    ExcelFile=pd.read_excel(path,sheetname=sheetname,parse_cols=parse_cols,index=False)
    #Defining columns automatically
    cols=list(ExcelFile)
    columns=[{"fieldName": cols[0].lower(), "name": cols[0], "dataTypeName": "text"}]

    for i in range(1,len(cols)):
        x={"fieldName": cols[i].lower(), "name": cols[i], "dataTypeName": "text"}
        columns.append(x)

    #create dataset
    NewDataSet=client.create(title,description="Lista de antenas Wi-fi en el atlántico",columns=columns, tags=tags,category="Ciencia, Tecnología e Innovación")
    ## Publish dataset NewDataSet.get('id') get the dataset ID
    client.publish(NewDataSet.get('id'))
    client.set_permission(NewDataSet.get('id'), "public")
    # Reemplazar datos
    # Conversion a JSON
    datajson = ExcelFile.to_json(None, orient='records')
    # Conversion a list
    datajson=json.loads(datajson)
    client.replace(NewDataSet.get('id'),datajson)
    print('Socrata done')
    client.close()

#Create dataset
def UploadDataset(ExcelFile,title,description,category,tags):
    #preparing data
    cols=list(ExcelFile)
    columns=[{"fieldName": cols[0].lower(), "name": cols[0], "dataTypeName": "text"}]
    for i in range(1,len(cols)):
        x={"fieldName": cols[i].lower(), "name": cols[i], "dataTypeName": "text"}
        columns.append(x)
    tags=tags.split(",")
    #Uploadin data     
    try:
        #Creating Socrata Client
        client=Socrata(cfg["web"],cfg["token"],username=cfg["email"],password=cfg["password"])
        NewDataSet=client.create(title,description=description,
                                    columns=columns, tags=tags,category=category)

        client.publish(NewDataSet.get('id'))
        client.set_permission(NewDataSet.get('id'), "private")
        # Convertion to JSON
        datajson = ExcelFile.to_json(None, orient='records')
        # JSON to list
        datajson=json.loads(datajson)
        client.replace(NewDataSet.get('id'),datajson)
        print('Socrata done')
        error='OK'
        dataset_id=NewDataSet.get('id')
        client.close()
    except BaseException as e:
    #if there is an error, reload login with error message
        error=str(e)
        print('Error description:')
        print(error)
        dataset_id='NoData'    
    return error,dataset_id
    
#Saving Excel into the server
def SaveFile(f):
    with open('some/file/name.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


#Saving all categories in the database run once
def CreateCategories():
    Categorias=['Agricultura y Desarrollo Rural',
                'Ambiente y Desarrollo Sostenible',
                'Ciencia, Tecnología e Innovación',
                'Comercio, Industria y Turismo',
                'Cultura',
                'DataJam - Desarrollo Rural',
                'Datathon Latam 2017',
                'Deporte y Recreación,'
                'Economía y Finanzas',
                'Educación',
                'Estadísticas Nacionales',
                'Función Pública',
                'Gastos Gubernamentales',
                'Hacienda y Crédito Público',
                'Inclusión Social y Reconciliación',
                'Justicia y Derecho',
                'Mapas Nacionales',
                'Minas y Energía',
                'Ordenamiento Territorial',
                'Organismos de Control',
                'Participación ciudadana',
                'Presupuestos Gubernamentales',
                'Resultados Electorales',
                'Salud y Protección Social',
                'Seguridad y Defensa',
                'Trabajo',
                'Transporte',
                'Vivienda, Ciudad y Territorio']
    for i in range(0,len(Categorias)):
        C=Categories(id=i+1,category=Categorias[i])
        C.save()

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def DatasetColumns(dataset_id):
    try:
        #Creating Socrata Client
        client=Socrata(cfg["web"],cfg["token"],username=cfg["email"],password=cfg["password"])
        data=client.get(dataset_id, limit=2)
        data=sorted(data[0].keys())
        #getting columns that could be used in the dataframe
        columns=str(data).upper()
        columns=columns.replace("[","")
        columns=columns.replace("]","")
        columns=columns.replace("'","")
        columns=columns.replace(" ","")
        columns=columns.split(",")
        #getting data to compare with the uploaded data
        for i in range(0,len(data)):
            data[i]=(str(data[i]).upper(),str(data[i]).upper())
        client.close()
    except BaseException as e:
    #if there is an error, reload login with error message
        error=str(e)
        print('Error description:')
        print(error)
        data=None
        columns=None
        client.close()
    return data,columns


def ModifyDataset(ExcelFile,dataset_id):
    try:
        #Creating Socrata Client
        client=Socrata(cfg["web"],cfg["token"],username=cfg["email"],password=cfg["password"])
        # Convertion to JSON
        datajson = ExcelFile.to_json(None, orient='records')
        # JSON to list
        datajson=json.loads(datajson)
        client.replace(dataset_id,datajson)
        print('Socrata done')
        error='OK'
        client.close()
    except BaseException as e:
    #if there is an error, reload login with error message
        error=str(e)
        print('Error description:')
        print(error)
    return error

def getDataset(dataset_id):
    table=''
    try:
        # Creating Socrata Client
        client=Socrata(cfg["web"],cfg["token"],username=cfg["email"],password=cfg["password"])
        data=client.get(dataset_id, content_type="json")
        data=str(data)
        data=data.replace("'","\"")
        data=data.upper()
        #getting data to compare with the uploaded data
        #print(type(data))
        #print(data)
        table=pd.read_json(data)
        #Replacing NaN for ''
        table=table.replace(pd.np.nan,'',regex=True)
        table=table.to_html(classes='table-striped " id = "my_table',index=False)
        vistas=client.get_metadata(dataset_id)
        vistas=str(vistas.get("viewCount"))
        client.close()
    except BaseException as e:
    #if there is an error, reload login with error message
        error=str(e)
        print('Error description:')
        print(error)
        client.close()
    return table, vistas

def DeleteDataset(dataset_id):
    print('El id')
    print(dataset_id)
    try:
        # Creating Socrata Client
        client=Socrata(cfg["web"],cfg["token"],username=cfg["email"],password=cfg["password"])
        client.delete(dataset_id)
        error='OK'
        client.close()
    except BaseException as e:
    #if there is an error, reload login with error message
        error=str(e)
        print('Error description:')
        print(error)
        client.close()
    return error

# Save Secretaries in de DB
def CreateSecretaries():
    Secretarias=['Agua Potable',
                'Capital Social',
                'Cultura y Patrimonio',
                'Ciudadela Universitaria',
                'Control Interno',
                'Desarrollo Económico',
                'Educación',
                'General',
                'Hacienda',
                'Secretaría TIC',
                'Infraestructura',
                'Interior',
                'Jurídica',
                'Mujer y Equidad',
                'Planeación',
                'Privada',
                'Quejas y Control Disciplinario',
                'Salud'
                ]
    for i in range(0,len(Secretarias)):
        C=Secretaries(id=i+1,secretary=Secretarias[i])
        C.save()

def Public(dataset_id):
    try:
        client=Socrata(cfg["web"],cfg["token"],username=cfg["email"],password=cfg["password"])
        client.set_permission(dataset_id, "public")
        info="OK"
    except:
        info="ERROR"
    return info

def Private(dataset_id):
    try:
        client=Socrata(cfg["web"],cfg["token"],username=cfg["email"],password=cfg["password"])
        client.set_permission(dataset_id, "private")
        info="OK"
    except:
        info="ERROR"
    return info

def ViewList():
    # gobernación: IP=10.10.10.73 Port=1521 SID=goatl1
    #ip = 'localhost'
    #port = 1521
    #SID = 'xe'
    view_list=None
    try:
        ip=cfg["ip"]; port=cfg["port"]; SID=cfg["SID"]
        #Conexión y Creación del DataFrame
        dsn_tns = cx_Oracle.makedsn(ip, port, SID)
        connection = cx_Oracle.connect(cfg["DBuser"], cfg["DBpassword"], dsn_tns)
        view_list=pd.read_sql('SELECT VIEW_NAME AS "Nombre de la Vista" FROM user_views', con=connection)
        connection.close()
    except BaseException as e:
    #if there is an error, reload login with error message
        error=str(e)
        print('Error description:')
        print(error)
        view_list=None
    return view_list

def getView(view_name):
     # gobernación: IP=10.10.10.73 Port=1521 SID=goatl1
    #ip = 'localhost'
    #port = 1521
    #SID = 'xe'
    ip=cfg["ip"]; port=cfg["port"]; SID=cfg["SID"]
    #Conexión y Creación del DataFrame
    dsn_tns = cx_Oracle.makedsn(ip, port, SID)
    connection = cx_Oracle.connect(cfg["DBuser"], cfg["DBpassword"], dsn_tns)
    query='SELECT *  FROM %s' %(view_name)
    view_data=pd.read_sql(query, con=connection)
    connection.close()
    return view_data

#Create dataset
def CreateETL(view_data,title,description,category,tags):
    #preparing data
    cols=list(view_data)
    columns=[{"fieldName": cols[0].lower(), "name": cols[0], "dataTypeName": "text"}]
    for i in range(1,len(cols)):
        x={"fieldName": cols[i].lower(), "name": cols[i], "dataTypeName": "text"}
        columns.append(x)
    tags=tags.split(",")
    #Uploadin data     
    try:
        client=Socrata(cfg["web"],cfg["token"],username=cfg["email"],password=cfg["password"])
        print(tags)
        print(category)
        print(description)
        print(columns)
        print(cols)

        NewDataSet=client.create(title,description=description,
                                    columns=columns, tags=tags,category=category)

        client.publish(NewDataSet.get('id'))
        client.set_permission(NewDataSet.get('id'), "private")
        # Convertion to JSON
        datajson = view_data.to_json(None, orient='records')
        # JSON to list
        datajson=json.loads(datajson)
        client.replace(NewDataSet.get('id'),datajson)
        print('Socrata done')
        error='OK'
        dataset_id=NewDataSet.get('id')
        client.close()
    except BaseException as e:
    #if there is an error, reload login with error message
        error=str(e)
        print('Error description:')
        print(error)
        dataset_id='NoData'    
    return error,dataset_id

def UpdateDataset(view_data,dataset_id):
    try:
        client=Socrata(cfg["web"],cfg["token"],username=cfg["email"],password=cfg["password"])
        # Convertion to JSON
        datajson = view_data.to_json(None, orient='records')
        # JSON to list
        datajson=json.loads(datajson)
        client.replace(dataset_id,datajson)
        #print('Socrata done')
        error='OK'
        client.close()
        print('Socrata Done')
    except BaseException as e:
    #if there is an error, reload login with error message
        error=str(e)
        print('Error description:')
        print(error)
    return error