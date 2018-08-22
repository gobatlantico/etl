from django import forms
from .datos import Sheets
from .models import Categories, Datasets, Secretaries, Users
from django.core.validators import RegexValidator


class ExcelUpload(forms.Form):
    ExcelFile=forms.FileField(label='Seleccione Archivo de excel de donde se exportarán los datos:')
    #sheet=forms.ChoiceField(label='Seleccione la hoja',widget=forms.Select(attrs={'class':'dropdown-header'}))
    #title=forms.CharField(label='Título')

class SheetSelection(forms.Form):
    #Method that pass arguments to the form.
    def __init__(self,*args,**kwargs):
        sheetlist = kwargs.pop('sheetlist')
        super(SheetSelection,self).__init__(*args,**kwargs)
        self.fields['sheet'].choices = sheetlist

    sheet=forms.ChoiceField(label='Seleccione la hoja',widget=forms.Select(attrs=
                                {'class':'dropdown-header',
                                'style':'width:30%'}))

    title=forms.CharField(label='Título',max_length=150,widget=forms.TextInput(attrs=
                                {'class':'form-control',
                                'placeholder':'Título',
                                'style':'width:30%'}))

    description=forms.CharField(label='descripción',widget=forms.Textarea(attrs=
                                {'class':'form-control',
                                'placeholder':'Descripción corta',
                                'style':'width:30%', 'rows':'3'}))
    tags=forms.CharField(label='Etiquetas',widget=forms.TextInput(attrs=
                                {'class':'form-control',
                                'placeholder':'Etiquetas',
                                'style':'width:30%'}))
    choices=list(Categories.objects.values_list('category',flat=True))
    for i in range(0,len(choices)):
        choices[i]=(choices[i],choices[i])
    category=forms.ChoiceField(label='Seleccione Categoría',choices=choices,widget=forms.Select(attrs=
                                   {'class':'dropdown-header',
                                   'style':'width:30%'}))

class ColumnsSelection(forms.Form):
    def __init__(self,*args,**kwargs):
        columnslist = kwargs.pop('columnslist')
        super(ColumnsSelection,self).__init__(*args,**kwargs)
        self.fields['columns'].choices = columnslist

    columns=forms.MultipleChoiceField(label='Columnas',error_messages={'required': 'Seleccione al menos una Columna'},
                                        widget=forms.CheckboxSelectMultiple(attrs=
                                            {'class':'checkbox-inline',
                                            #'onchange':'calculate()'

                                            }))

class DatasetSelection(forms.Form):
    #def __init__(self, *args, **kwargs):
    #    user = kwargs.pop('user')
    #    super(DatasetSelection, self).__init__(*args, **kwargs)
    #    choices=list(Datasets.objects.values_list('title',flat=True).filter(user=user))
    #    for i in range(0,len(choices)):
    #        choices[i]=(choices[i],choices[i])
    #    self.fields['datasets'].choices = choices

    #datasets=forms.ChoiceField(label='Seleccione conjunto de datos que se actualizará',widget=forms.Select(attrs=
    #                               {'class':'dropdown-header',
    #                               'style':'width:30%'}))
    ExcelFile=forms.FileField(label='Seleccione Archivo de excel de donde se exportarán los datos nuevos:')

#Select sheet to modify dataset
class Sheet(forms.Form):
    #Method that pass arguments to the form.
    def __init__(self,*args,**kwargs):
        sheetlist = kwargs.pop('sheetlist')
        super(Sheet,self).__init__(*args,**kwargs)
        self.fields['sheet'].choices = sheetlist

    sheet=forms.ChoiceField(label='Seleccione la hoja',widget=forms.Select(attrs=
                                {'class':'dropdown-header',
                                'style':'width:30%'}))

class DatasetDelete(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(DatasetDelete, self).__init__(*args, **kwargs)
        choices=list(Datasets.objects.values_list('title',flat=True).filter(user=user))
        for i in range(0,len(choices)):
            choices[i]=(choices[i],choices[i])
        self.fields['datasets'].choices = choices

    datasets=forms.ChoiceField(label='Seleccione conjunto de datos que se elminará',widget=forms.Select(attrs=
                                   {'class':'dropdown-header',
                                   'style':'width:30%'}))


class LoginForm(forms.Form):
    email = forms.EmailField(label='Correo electrónico', max_length=40,
            error_messages={'invalid': 'Ingrese una direción de Correo válida'},
            validators=[
            RegexValidator(
            regex='^[a-zA-Z0-9]+@+.*$',
            message='El e-mail debe contener solo letras y números',
            code='invalid_username')],
            widget=forms.TextInput(attrs=
            {'class':'form-control',
            'placeholder':'e-mail',
            'style':'width:30%'}))
    password = forms.CharField(label='Contraseña', min_length=6, max_length=12,
    widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Contraseña','style':'width:30%'}))


class NewUser(forms.Form):
    email = forms.EmailField(label='Correo electrónico', max_length=40,
            error_messages={'invalid': 'Ingrese una direción de Correo válida'},
            validators=[
            RegexValidator(
            regex='^[a-zA-Z0-9]+@+.*$',
            message='El e-mail debe contener solo letras y números',
            code='invalid_username')],
            widget=forms.TextInput(attrs={'class':'form-control',
                                'placeholder':'e-mail',
                                'style':'width:30%'}))
    name=forms.CharField(label='Nombre y Apellido',max_length=150,widget=forms.TextInput(attrs=
                                {'class':'form-control',
                                'placeholder':'Nombre y Apellido',
                                'style':'width:30%'}))

    password = forms.CharField(label='Contraseña', min_length=6, max_length=12,
    widget=forms.PasswordInput(attrs={'class':'form-control',
                                    'placeholder':'Contraseña',
                                    'style':'width:30%'}))
    password2 = forms.CharField(label='Repetir Contraseña', min_length=6, max_length=12,
    widget=forms.PasswordInput(attrs={'class':'form-control',
                                    'placeholder':'Contraseña',
                                    'style':'width:30%'}))
    choices=list(Secretaries.objects.values_list('secretary',flat=True))
    ids=list(Secretaries.objects.values_list('id',flat=True))
    for i in range(0,len(choices)):
        choices[i]=(ids[i],choices[i])
    secretary=forms.ChoiceField(label='Seleccione Secretaría',choices=choices,widget=forms.Select(attrs=
                                   {'class':'dropdown-header',
                                   'style':'width:30%'}))
    #User state, type, Dates (Done)
    admin=forms.BooleanField(label='Usuario administrador',widget=forms.CheckboxInput(attrs=
                                  {'class':'form-check-input'}),required=False)

class EditUser(forms.Form):
    def __init__(self,*args,**kwargs):
        user_id = kwargs.pop('user_id')
        super(EditUser,self).__init__(*args,**kwargs)
        #Getting user previous info
        UserData=Users.objects.filter(id=user_id)
        self.fields['email'].initial = UserData[0].user 
        self.fields['admin'].initial= UserData[0].admin
        self.fields['state'].initial= UserData[0].state
        self.fields['secretary'].initial=UserData[0].secretaria_id
        self.fields['name'].initial=UserData[0].name

    email = forms.EmailField(label='Correo electrónico', max_length=40,
            error_messages={'invalid': 'Ingrese una direción de Correo válida'},
            validators=[
            RegexValidator(
            regex='^[a-zA-Z0-9]+@+.*$',
            message='El e-mail debe contener solo letras y números',
            code='invalid_username')],
            widget=forms.TextInput(attrs={'class':'form-control',
                                'placeholder':'e-mail',
                                'style':'width:30%'}))
    
    name=forms.CharField(label='Nombre y Apellido',max_length=150,widget=forms.TextInput(attrs=
                                {'class':'form-control',
                                'placeholder':'Nombre y Apellido',
                                'style':'width:30%'}))

    password = forms.CharField(label='Contraseña', min_length=6, max_length=12,
    widget=forms.PasswordInput(attrs={'class':'form-control',
                                   'placeholder':'Contraseña',
                                   'style':'width:30%;display:none'}), required=False)
    password2 = forms.CharField(label='Confirmar Contraseña', min_length=6, max_length=12,
    widget=forms.PasswordInput(attrs={'class':'form-control',
                                    'placeholder':'Contraseña',
                                    'style':'width:30%;display:none'}), required=False)

    choices=list(Secretaries.objects.values_list('secretary',flat=True))
    ids=list(Secretaries.objects.values_list('id',flat=True))
    for i in range(0,len(choices)):
        choices[i]=(ids[i],choices[i])
    secretary=forms.ChoiceField(label='Seleccione Secretaría',choices=choices,widget=forms.Select(attrs=
                                   {'class':'dropdown-header',
                                   'style':'width:30%'}))
    #User state, type, Dates (Done)
    admin=forms.BooleanField(label='Usuario administrador',widget=forms.CheckboxInput(attrs=
                                  {'class':'form-control'}),required=False)
    #States (Done)
    states=(('A','Activo'),('I','Inactivo'),('D','Eliminado'))
    state=forms.ChoiceField(label='Estado del usuario',widget=forms.Select(attrs=
                                                {'class':'dropdown-header',
                                                 'align':'center'}),choices=states)

class ChangePassword(forms.Form):   

    oldpass=forms.CharField(label='Contraseña Actual', min_length=6, max_length=12,widget=forms.PasswordInput(attrs=
                                                                {'class':'form-control',
                                                                'placeholder':'Contraseña',
                                                                'style':'width:30%'}))
    newpass=forms.CharField(label='Nueva Contraseña', min_length=6, max_length=12,widget=forms.PasswordInput(attrs=
                                                                {'class':'form-control',
                                                                'placeholder':'Contraseña',
                                                                'style':'width:30%'}))
    newpass2=forms.CharField(label='Confirmar Nueva Contraseña', min_length=6, max_length=12,widget=forms.PasswordInput(attrs=
                                                                {'class':'form-control',
                                                                'placeholder':'Contraseña',
                                                                'style':'width:30%'}))


class ResetPassword(forms.Form):


    newpass=forms.CharField(label='Nueva Contraseña', min_length=6, max_length=12,widget=forms.PasswordInput(attrs=
                                                                {'class':'form-control',
                                                                'placeholder':'Contraseña',
                                                                'style':'width:30%'}))
    newpass2=forms.CharField(label='Confirmar Nueva Contraseña', min_length=6, max_length=12,widget=forms.PasswordInput(attrs=
                                                                {'class':'form-control',
                                                                'placeholder':'Contraseña',
                                                                'style':'width:30%'}))

class ResetEmail(forms.Form):
    email = forms.EmailField(label='Correo electrónico', max_length=40,
            error_messages={'invalid': 'Ingrese una direción de Correo válida'},
            validators=[
            RegexValidator(
            regex='^[a-zA-Z0-9]+@+.*$',
            message='El e-mail debe contener solo letras y números',
            code='invalid_username')],
            widget=forms.TextInput(attrs={'class':'form-control',
                                'placeholder':'e-mail',
                                'style':'width:30%'}))

class ETLform(forms.Form):

    title=forms.CharField(label='Título',max_length=150,widget=forms.TextInput(attrs=
                                {'class':'form-control',
                                'placeholder':'Título',
                                'style':'width:30%'}))

    description=forms.CharField(label='descripción',widget=forms.Textarea(attrs=
                                {'class':'form-control',
                                'placeholder':'Descripción corta',
                                'style':'width:30%', 'rows':'3'}))

    tags=forms.CharField(label='Etiquetas',widget=forms.TextInput(attrs=
                                {'class':'form-control',
                                'placeholder':'Etiquetas',
                                'style':'width:30%'}))
    choices=list(Categories.objects.values_list('category',flat=True))
    for i in range(0,len(choices)):
        choices[i]=(choices[i],choices[i])
    category=forms.ChoiceField(label='Seleccione Categoría',choices=choices,widget=forms.Select(attrs=
                                   {'class':'dropdown-header',
                                   'style':'width:30%'}))
    #('VALUE','TEXT')
    periods=(('N','No actualizar'),('D','Días'),('M','Meses'),('H','Horas'))

    integer=forms.IntegerField(label='Frecuencia de actualización',max_value=24,
                                min_value=1,widget=forms.NumberInput(attrs=
                                   {'class':'form-control',
                                'placeholder':'1-24',
                                'style':'width:80px'}))

    update=forms.ChoiceField(label='',choices=periods,widget=forms.Select(attrs=
                                   {'class':'dropdown-header',
                                   'style':'width:150px'}))

class EditETL(forms.Form):
    #('VALUE','TEXT')
    periods=(('N','No actualizar'),('D','Días'),('M','Meses'),('H','Horas'))

    integer=forms.IntegerField(label='Frecuencia de actualización',max_value=24,
                                min_value=1,widget=forms.NumberInput(attrs=
                                   {'class':'form-control',
                                'placeholder':'1-24',
                                'style':'width:80px'}))

    update=forms.ChoiceField(label='',choices=periods,widget=forms.Select(attrs=
                                   {'class':'dropdown-header',
                                   'style':'width:150px'}))
