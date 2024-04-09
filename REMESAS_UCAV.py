import pandas as pd                        # Tratamiento de Datos.
import numpy as np                         # Tratamiento de Datos.
import streamlit as st                     # Página Web.
from datetime import datetime, timedelta   # Fechas.
import io                                  # Descarga y manejo de EXCEL.
import re                                  # Expresiones Regulares (Tratamiento de Texto).


def PAGO_NOMINAS_UCAV(EXCEL_CODIGO_EMPLEADOS, REMESA_NOMINA, Fecha, Num_Documento, Mes_Pago):

## A) TRATAMIENTO DEL EXCEL DE EMPLEADOS:
    ## A.0º) Lectura de los datos CÓDIGO EMPLEADOS:
    df_codigo_empleados= pd.read_excel(EXCEL_CODIGO_EMPLEADOS)
    df_codigo_empleados= df_codigo_empleados.map(lambda s: s.upper() if type(s)==str else s)  # Conversión de todos los campos a MAYÚSCULAS.
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    for columna in ['Nombre', 'Primer apellido', 'Segundo apellido']:
        ## A.1º) Eliminación de las tildes y cambio de Ñ por N:
        df_codigo_empleados[columna]= df_codigo_empleados[columna].replace({'Á':'A', 'É':'E', 'Í':'I', 'Ó':'O', 'Ú':'U', 'Ñ':'N'}, regex=True)
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        ## A.2º) Eliminación de espacios innecesarios al principio y al final de cada cadena de texto:
        df_codigo_empleados[columna]= df_codigo_empleados[columna].str.strip()
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        ## A.3º) Sustitución de "M." y "Mª" por MARIA:
        df_codigo_empleados[columna]= df_codigo_empleados[columna].replace({'Mª':'MARIA', 'M[.]':'MARIA '}, regex=True)
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        ## A.4º) Eliminación de "." y "-":
        df_codigo_empleados[columna]= df_codigo_empleados[columna].str.replace('[.]','', regex=True)
        df_codigo_empleados[columna]= df_codigo_empleados[columna].str.replace('-',' ', regex=True)
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        ## A.5.1º) Eliminación de los "determinantes" (palabras con un espacio antes y después) y sustituirlos por un espacio en blanco (para evitar juntar Nombre y Apellido):
        determinantes= [' EL ',' LA ',' LO ',' LE ',' LES ',' LOS ',' LAS ',' DE ',' DEL ',' DA ',' DO ',' DI ',' UN ',' UNA ',' UNOS ',' UNAS ',' MAC ',' MC ',' VAN ',' VON ',' Y ', ' E ',' THE ','THE ',' OF ']
        for deter in determinantes:
            df_codigo_empleados[columna]= df_codigo_empleados[columna].replace({deter:' '}, regex=True)

        ## A.5.2º) Eliminación de los "determinantes" del PRINCIPIO (palabras con un espacio después) y sustituirlos por una cadena de texto vacía (para evitar espacios innecesarios):
        determinantes2= ['EL ','LA ','LO ','LE ','LES ','LOS ','LAS ','DE ','DEL ','DA ','DO ','DI ','UN ','UNA ','UNOS ','UNAS ','MAC ','MC ','VAN ','VON ','Y ', 'E ','THE ','OF ']
        for deter in determinantes2:
            df_codigo_empleados[columna]= df_codigo_empleados[columna].replace({'^' + deter:''}, regex=True)
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # A.6º) Crear una columna con este orden APELLIDO1 + APELLIDO2 + NOMBRE (ya "limpios") y otra columna con el "NOMBRE COMPLETO"-> Teniendo en cuenta si tienen 2º APLL., 1º y 2º APLL. ...:
    # a) COLUMNA-> "APELLIDO1 + APELLIDO2 + NOMBRE":
    def crear_columna_Apellidos_Nombre(row):
        if pd.notna(row['Nombre']) and pd.notna(row['Primer apellido']) and pd.notna(row['Segundo apellido']):   # Si NO es NULO-> Nombre, 1º Apll. y 2º Apll. ...
            return f"{row['Primer apellido']} {row['Segundo apellido']} {row['Nombre']}"                               # Devuelve-> 1º Apll. + 2º Apll. + Nombre.
        elif pd.notna(row['Nombre']) and pd.notna(row['Primer apellido']) and pd.isna(row['Segundo apellido']):  # Si NO es NULO-> Nombre y 1º Apll.; Pero SÍ es NULO 2º Apll. ...
            return f"{row['Primer apellido']} {row['Nombre']}"                                                         # Devuelve-> 1º Apll. + Nombre.
        elif pd.notna(row['Nombre']) and pd.isna(row['Primer apellido']) and pd.isna(row['Segundo apellido']):   # Si NO es NULO-> Nombre; Pero SÍ es NULO 1º Apll. y 2º Apll. ...
            return row['Nombre']                                                                                       # Devuelve-> Nombre.

    # Aplica la función a cada fila y crea la nueva columna:
    df_codigo_empleados['Apellidos_Nombre_Cod_Empleado']= df_codigo_empleados.apply(crear_columna_Apellidos_Nombre, axis=1)
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    ############# CASO EXCEPCIONAL ELENA EUGENIA BALANYA RODRIGUEZ-PARETS-> Poner ELENA EUGEN BALANYA RODRIGUEZ-PARETS:
    df_codigo_empleados['Apellidos_Nombre_Cod_Empleado']= df_codigo_empleados['Apellidos_Nombre_Cod_Empleado'].replace('BALANYA RODRIGUEZ PARETS ELENA EUGENIA', 'BALANYA RODRIGUEZ PARETS ELENA EUGEN')
    
    #............................................................................#
    # b) COLUMNA-> "NOMBRE COMPLETO":
    def crear_columna_Nombre_Completo(row):
        if pd.notna(row['Nombre']) and pd.notna(row['Primer apellido']) and pd.notna(row['Segundo apellido']):   # Si NO es NULO-> Nombre, 1º Apll. y 2º Apll. ...
            return f"{row['Nombre']} {row['Primer apellido']} {row['Segundo apellido']}"                               # Devuelve-> Nombre + 1º Apll. + 2º Apll.
        elif pd.notna(row['Nombre']) and pd.notna(row['Primer apellido']) and pd.isna(row['Segundo apellido']):  # Si NO es NULO-> Nombre y 1º Apll.; Pero SÍ es NULO 2º Apll. ...
            return f"{row['Nombre']} {row['Primer apellido']}"                                                         # Devuelve-> Nombre + 1º Apll.
        elif pd.notna(row['Nombre']) and pd.isna(row['Primer apellido']) and pd.isna(row['Segundo apellido']):   # Si NO es NULO-> Nombre; Pero SÍ es NULO 1º Apll. y 2º Apll. ...
            return row['Nombre']                                                                                       # Devuelve-> Nombre.

    # Aplica la función a cada fila y crea la nueva columna
    df_codigo_empleados['Nombre Completo']= df_codigo_empleados.apply(crear_columna_Nombre_Completo, axis=1)
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # A.7º) Quedarse sólo con las columnas que interesan:
    df_codigo_empleados= df_codigo_empleados[['Nº', 'Nombre Completo', 'Apellidos_Nombre_Cod_Empleado']]
#==========================================================================================================================================================================================#

## B) TRATAMIENTO DEL EXCEL DE LA REMESA DEL BANCO:
    ## B.0º) Lectura de los datos BANCO:
    df_banco_nomina= pd.read_excel(REMESA_NOMINA, header=15)  # Cargo los datos de la REMESA de NÓMINA e indico la Fila del Encabezado.
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    ## B.1º) Eliminación de las tildes y cambio de Ñ por N:
    df_banco_nomina['APELL_NOMB_BANCO'] = df_banco_nomina['Beneficiario'].replace({'Á':'A', 'É':'E', 'Í':'I', 'Ó':'O', 'Ú':'U', 'Ñ':'N'}, regex=True)
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    ## B.2º) Eliminación de espacios innecesarios al principio y al final de cada cadena de texto:
    df_banco_nomina['APELL_NOMB_BANCO'] = df_banco_nomina['APELL_NOMB_BANCO'].str.strip()
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    ## B.3º) Sustitución de "M." y "Mª" por MARIA:
    df_banco_nomina['APELL_NOMB_BANCO'] = df_banco_nomina['APELL_NOMB_BANCO'].replace({'Mª':'MARIA', 'M[.]':'MARIA '}, regex=True)
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    ## B.4º) Eliminación de "." y "-" y "EUR" (del IMPORTE):
    df_banco_nomina['APELL_NOMB_BANCO']= df_banco_nomina['APELL_NOMB_BANCO'].str.replace('[.]','', regex=True)
    df_banco_nomina['APELL_NOMB_BANCO']= df_banco_nomina['APELL_NOMB_BANCO'].str.replace('-',' ', regex=True)
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    ## B.5.1º) Eliminación de los "determinantes" (palabras con un espacio antes y después) y sustituirlos por un espacio en blanco (para evitar juntar Nombre y Apellido):
    determinantes= [' EL ',' LA ',' LO ',' LE ',' LES ',' LOS ',' LAS ',' DE ',' DEL ',' DA ',' DO ',' DI ',' UN ',' UNA ',' UNOS ',' UNAS ',' MAC ',' MC ',' VAN ',' VON ',' Y ', ' E ',' THE ','THE ',' OF ']
    for deter in determinantes:
        df_banco_nomina['APELL_NOMB_BANCO'] = df_banco_nomina['APELL_NOMB_BANCO'].replace({deter:' '}, regex=True)

    ## B.5.2º) Eliminación de los "determinantes" del PRINCIPIO (palabras con un espacio después) y sustituirlos por una cadena de texto vacía (para evitar espacios innecesarios):
    determinantes2= ['EL ','LA ','LO ','LE ','LES ','LOS ','LAS ','DE ','DEL ','DA ','DO ','DI ','UN ','UNA ','UNOS ','UNAS ','MAC ','MC ','VAN ','VON ','Y ', 'E ','THE ','OF ']
    for deter in determinantes2:
        df_banco_nomina['APELL_NOMB_BANCO'] = df_banco_nomina['APELL_NOMB_BANCO'].replace({'^' + deter:''}, regex=True)
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    ## B.6º) Modificación de la columna del IMPORTE:
    df_banco_nomina['Importe']= df_banco_nomina['Importe'].str.replace(' EUR','', regex=True)      # Eliminar "EUR".
    df_banco_nomina['Importe']= '-' + df_banco_nomina['Importe'].str.replace('[.]','', regex=True) # Eliminar el "." y poner el Importe en NEGATIVO.
#==========================================================================================================================================================================================#

## C) UNIÓN DE LOS 2 DF SEGÚN EL NOMBRE "TRATADO"-> PARA CONSEGUIR EL "CODIGO_EMPLEADO":
    df_resultado= pd.merge(df_banco_nomina, df_codigo_empleados,                                 # Df's a unir.
                           left_on='APELL_NOMB_BANCO', right_on='Apellidos_Nombre_Cod_Empleado', # A la izquierda el Df_BANCO y a la derecha Df_CÓDIGO_EMPLEADOS.
                           how='left')                                                           # Unión por el Df de la Izquierda (BANCO).

    # C.1º) "np.where" para dejar el 'CÓDIGO' sólo cuando COINCIDEN (y deja los demás como 'NaN'):
    df_resultado['Nº']= np.where(df_resultado['Nº'].notna(), df_resultado['Nº'], np.nan)

    # C.2º) Convierte la columna 'Código' a 'Int64' (Nº ENTERO):
    df_resultado['Nº']= df_resultado['Nº'].astype('Int64')

    # C.3º) Columnas que se mantendrán en el resultado:
    df_resultado= df_resultado[['Nº','Beneficiario', 'Concepto', 'Importe']]
#==========================================================================================================================================================================================#

## D) CREACIÓN DEL DataFrame PARA SUBIR A "BUSINESS CENTRAL":
    df_NOMINA= pd.DataFrame()
    df_NOMINA['Descripcion']= 'PAGO ' + df_resultado['Concepto'] + df_resultado['Beneficiario'].apply(lambda x: f' {Mes_Pago} - {x}')
    df_NOMINA['Importe']= df_resultado['Importe']
    df_NOMINA['Fecha']= pd.to_datetime(Fecha, format='%d/%m/%Y')
    df_NOMINA['No. Documento']= Num_Documento
    df_NOMINA['Tipo mov']= 'Banco'
    df_NOMINA['Banco']= 'SANTANDER02'
    df_NOMINA['CECO']= None
    df_NOMINA['No. Empleado']= df_resultado['Nº']
    df_NOMINA['Cta Contrapartida']= '46500000'

    df_NOMINA= df_NOMINA[['Fecha','No. Documento','Descripcion','Importe','Tipo mov','Banco','CECO','No. Empleado','Cta Contrapartida']] # ORDENAR COLUMNAS DEL CSV FINAL-> Para BUSINESS CENTRAL.
    df_NOMINA= df_NOMINA.sort_values(by='Descripcion', ascending=True)                                                                # ORDENAR los VALORES según la "Descripción".
    df_NOMINA= df_NOMINA.reset_index(drop=True)                                                                                       # RESETEO del ÍNDICE.
#==========================================================================================================================================================================================#

## E) VISUALIZAR SÓLO LOS CASOS EN LOS QUE NO SE HA CONSEGUIDO UNIR EL "CODIGO EMPLEADO":
    Códigos_FALTANTES= df_resultado[df_resultado['Nº'].isna()].copy()                     # QUEDARSE CON LOS QUE NO COINCIDEN CON EL CÓDIGO.
    Códigos_FALTANTES= Códigos_FALTANTES.sort_values(by='Beneficiario', ascending=True)   # ORDENAR los VALORES según la "Descripción".
    Códigos_FALTANTES= Códigos_FALTANTES.reset_index(drop=True)                           # RESETEO del ÍNDICE.
#==========================================================================================================================================================================================#

## F) COMPARACIÓN Nº FILAS BANCO vs. Nº FILAS UNIÓN:
    num_Filas_BANCO= len(df_banco_nomina)
    num_Filas_UNION= len(df_resultado)

    return df_NOMINA, Códigos_FALTANTES, num_Filas_BANCO, num_Filas_UNION
#############################################################################################################################################################################################

def INGRESOS_SEGUROS_UCAV(ARCHIVO_EXCEL_SEGUROS, Fecha, Num_Documento, Mes, COMISION_BANCO):
        ## 1º) LEER DATOS DEL BANCO (+ Modificaciones en la columna de "IMPORTE"):
        df2= pd.read_excel(ARCHIVO_EXCEL_SEGUROS, header=16).iloc[:-4, :-1]        # CARGAR DATOS (ENCABEZADO + QUITAR ÚLTIMAS FILAS + QUITAR ÚLTIMA COLUMNA) !!!
        df2['Importe']= '-' + df2['Importe'].replace(' EUR','', regex=True)        # Eliminación de " EUR" + Importe en NEGATIVO.
        #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

        ## 2º) CREAR DataFrame RESULTADO (A falta de la 1ª (Ingreso Banco) y ÚLTIMA FILA (Comisiones Banco)):
        df= pd.DataFrame()
        df['Importe (DL)']= df2['Importe']
        df['Descripción']= 'INGRESO SEGUROS SALUD ' + df2['Deudor'].apply(lambda x: f' {Mes} - {x}')
        df['Fecha registro']= pd.to_datetime(Fecha, format='%d/%m/%Y').strftime('%d/%m/%Y')
        df['Fecha de IVA']= df['Fecha registro']
        df['Tipo documento']= 'Pago'
        df['Nº documento']= Num_Documento
        df['Tipo mov.']= 'Cuenta'
        df['Nº cuenta']= '77800000'
        df['Tipo contrapartida']= 'Cuenta'
        df['Op. triangular']='No'
        df['Corrección']= 'No'
        df[['Nº asiento','Importe debe','Importe haber','Importe','Liq. por nº documento','Liq. por tipo documento','Tipo de registro gen.','Grupo contable neg. gen.','Grupo contable prod. gen.','Tipo regis. contrapartida',
        'Gr. contable negocio contrap.','Gr. contable producto contrap.','Código de fraccionamiento','Comentario','Tipo de id.','Nombre de empresa correcto','CIF/NIF correcto','Titulacion Código',
        'Cód. dim. acceso directo 4','Interface Code','Nombre de cuenta','Cta. contrapartida','Empleados Código','CECO Código']]=None
        #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

        ## 3º) CÁLCULO del IMPORTE TOTAL:
        Importe_Total= -df['Importe (DL)'].str.replace(',','.').astype(float).sum()       # IMPORTE TOTAL.
        Importe_Total_Linea_BANCO = '{:,.2f}'.format(Importe_Total).replace(',','').replace('.',',') # IMPORTE TOTAL (FORMATO PARA BUSINESS CENTRAL [Con "," y sin "."]).
        Importe_Total_VISUALIZACION = '{:,.2f}'.format(Importe_Total).replace(',','_').replace('.',',').replace('_','.') # IMPORTE TOTAL PARA VISUALIZAR POR PANTALLA.
        #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

        ## 4º) Fila INICIAL-> INGRESO BANCO:
        Fila_BANCO = pd.DataFrame([{'Importe (DL)': Importe_Total_Linea_BANCO,
                                'Descripción': f'INGRESO SEGUROS SALUD {Mes}',
                                'Fecha registro': pd.to_datetime(Fecha, format='%d/%m/%Y').strftime('%d/%m/%Y'),
                                'Fecha de IVA': pd.to_datetime(Fecha, format='%d/%m/%Y').strftime('%d/%m/%Y'),
                                'Tipo documento': 'Pago',
                                'Nº documento': Num_Documento,
                                'Tipo mov.': 'Banco',
                                'Nº cuenta': 'SANTANDER02',
                                'Tipo contrapartida': 'Cuenta',

                                'Op. triangular': 'No', 'Corrección': 'No', 'Nº asiento': None, 'Importe debe': None, 'Importe haber': None, 'Importe': None, 'Liq. por nº documento': None, 'Liq. por tipo documento': None,
                                'Tipo de registro gen.': None, 'Grupo contable neg. gen.': None, 'Grupo contable prod. gen.': None, 'Tipo regis. contrapartida': None, 'Gr. contable negocio contrap.': None,
                                'Gr. contable producto contrap.': None, 'Código de fraccionamiento': None, 'Comentario': None, 'Tipo de id.': None, 'Nombre de empresa correcto': None, 'CIF/NIF correcto': None,
                                'Titulacion Código': None, 'Cód. dim. acceso directo 4': None, 'Interface Code': None, 'Nombre de cuenta': None, 'Cta. contrapartida': None, 'Empleados Código': None, 'CECO Código': None}])
        #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

        ## 5º) Fila FINAL-> COMISIONES BANCO:
        Fila_COMISIONES_BANCO = pd.DataFrame([{'Importe (DL)': f'-{COMISION_BANCO}'.replace('.',','),
                                'Descripción': f'COM. INGRESO SEGUROS SALUD {Mes}',
                                'Fecha registro': pd.to_datetime(Fecha, format='%d/%m/%Y').strftime('%d/%m/%Y'),
                                'Fecha de IVA': pd.to_datetime(Fecha, format='%d/%m/%Y').strftime('%d/%m/%Y'),
                                'Tipo documento': 'Pago',
                                'Nº documento': Num_Documento,
                                'Tipo mov.': 'Banco',
                                'Nº cuenta': 'SANTANDER02',
                                'Tipo contrapartida': 'Cuenta',
                                
                                'Op. triangular': 'No', 'Corrección': 'No', 'Nº asiento': None, 'Importe debe': None, 'Importe haber': None, 'Importe': None, 'Liq. por nº documento': None, 'Liq. por tipo documento': None,
                                'Tipo de registro gen.': None, 'Grupo contable neg. gen.': None, 'Grupo contable prod. gen.': None, 'Tipo regis. contrapartida': None, 'Gr. contable negocio contrap.': None,
                                'Gr. contable producto contrap.': None, 'Código de fraccionamiento': None, 'Comentario': None, 'Tipo de id.': None, 'Nombre de empresa correcto': None, 'CIF/NIF correcto': None,
                                'Titulacion Código': None, 'Cód. dim. acceso directo 4': None, 'Interface Code': None, 'Nombre de cuenta': None, 'Cta. contrapartida': '62600000', 'Empleados Código': None, 'CECO Código': None}])
        #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

        ## 6º) UNIÓN DE LOS 3 DataFrames:
        df_FINAL= pd.concat([Fila_BANCO, df, Fila_COMISIONES_BANCO]).reset_index(drop=True)
        #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

        ## 7º) ORDENACIÓN DE VALORES (por Descripción) Y DE COLUMNAS:
        df= df.sort_values(by= 'Descripción').reset_index(drop=True)

        df_FINAL= df_FINAL[['Fecha registro', 'Fecha de IVA', 'Nº asiento', 'Tipo documento', 'Nº documento', 'Tipo mov.', 'Nº cuenta', 'Nombre de cuenta', 'Descripción', 'Importe debe', 'Importe haber', 'Importe',
                'Importe (DL)', 'Tipo contrapartida', 'Cta. contrapartida', 'Liq. por nº documento', 'Liq. por tipo documento', 'Op. triangular', 'Empleados Código', 'CECO Código', 'Tipo de registro gen.',
                'Grupo contable neg. gen.', 'Grupo contable prod. gen.', 'Tipo regis. contrapartida', 'Gr. contable negocio contrap.', 'Gr. contable producto contrap.', 'Código de fraccionamiento', 'Corrección',
                'Comentario', 'Tipo de id.', 'Nombre de empresa correcto', 'CIF/NIF correcto', 'Titulacion Código', 'Cód. dim. acceso directo 4', 'Interface Code']]

        return df_FINAL, Importe_Total_VISUALIZACION
############################################################################################################################################################################################

def PAGO_RETENCIONES_UCAV(ARCHIVO_EXCEL_RETENCIONES, Fecha, Num_Documento, TRIMESTRE):
### A) TRABAJADORES:
    ## A.1º) LEER DATOS DEL BANCO (+ Modificaciones en la columna de 'Importe', 'Nº cuenta' y 'Empleados Código'):
    df1= pd.read_excel(ARCHIVO_EXCEL_RETENCIONES, sheet_name='TRABAJADORES')    # CARGAR DATOS.

    for cuenta in ['Nº cuenta', 'Empleados Código']: # A tipo "INT".
        df1[cuenta]= df1[cuenta].astype('int')
    # Poner el IMPORTE en POSITIVO:
    df1['Importe']= -df1['Importe']

    # Casos en los que el IMPORTE==0:
    Reten_Importe_0_Trabajadores= df1[df1['Importe'] == 0]['Empleados Código']
    # Quedarse SÓLO con los casos en los que el IMPORTE != 0:
    df1= df1[df1['Importe'] != 0]
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

    ## A.2º) CREAR DataFrame RESULTADO-> TRABAJADORES:
    df_TRABAJADORES= pd.DataFrame()
    df_TRABAJADORES['Importe (DL)']= df1['Importe'].astype(str).str.replace('.', ',')
    df_TRABAJADORES['Descripción']= f'PAGO RETENCIONES  {TRIMESTRE}'
    df_TRABAJADORES['Fecha registro']= pd.to_datetime(Fecha, format='%d/%m/%Y').strftime('%d/%m/%Y')
    df_TRABAJADORES['Fecha de IVA']= df_TRABAJADORES['Fecha registro']
    df_TRABAJADORES['Tipo documento']= 'Pago'
    df_TRABAJADORES['Nº documento']= Num_Documento
    df_TRABAJADORES['Tipo mov.']= 'Cuenta'
    df_TRABAJADORES['Nº cuenta']= '47510001'                                # RETENCIONES de TRABAJADORES !!!
    df_TRABAJADORES['Tipo contrapartida']= 'Cuenta'
    df_TRABAJADORES['Op. triangular']='No'
    df_TRABAJADORES['Corrección']= 'No'
    df_TRABAJADORES['Empleados Código']= df1['Empleados Código']            # RETENCIONES de TRABAJADORES !!!
    df_TRABAJADORES[['Nº asiento','Importe debe','Importe haber','Importe','Liq. por nº documento','Liq. por tipo documento','Tipo de registro gen.','Grupo contable neg. gen.','Grupo contable prod. gen.','Tipo regis. contrapartida',
    'Gr. contable negocio contrap.','Gr. contable producto contrap.','Código de fraccionamiento','Comentario','Tipo de id.','Nombre de empresa correcto','CIF/NIF correcto','Titulacion Código',
    'Cód. dim. acceso directo 4','Interface Code','Nombre de cuenta','Cta. contrapartida','CECO Código']]=None
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

    ## A.3º) CÁLCULO del IMPORTE TOTAL + Nº Retenciones de Trabajadores:
    Importe_Total_Trabajadores= df1.Importe.sum()    # TOTAL IMPORTE.
    Importe_Total_Trabajadores_VISUALIZACION = '{:,.2f} €'.format(Importe_Total_Trabajadores).replace(',','_').replace('.',',').replace('_','.') # IMPORTE TOTAL PARA VISUALIZAR POR PANTALLA.
    Num_Retenc_Trabajadores= len(df_TRABAJADORES)    # Nº Retenciones de Trabajadores.
#==================================================================================================================================================================================================#

### B) COLABORADORES:
    ## B.1º) LEER DATOS DEL BANCO (+ Modificaciones en la columna de 'Cuenta retención'):
    df2= pd.read_excel(ARCHIVO_EXCEL_RETENCIONES, sheet_name='COLABORADORES')    # CARGAR DATOS.
    df2['Cuenta retención']= df2['Cuenta retención'].astype('int')           # A tipo "INT".

    Reten_Importe_0_Colaboradores= df2[df2['Couta'] == 0]['Nombre tercero']
    # Quedarse SÓLO con los casos en los que el IMPORTE != 0:
    df2= df2[df2['Couta'] != 0]
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

    ## B.2º) CREAR DataFrame RESULTADO-> COLABORADORES:
    df_COLABORADORES= pd.DataFrame()
    df_COLABORADORES['Importe (DL)']= df2['Couta'].astype(str).str.replace('.', ',')
    df_COLABORADORES['Descripción']= f'PAGO RETENCIONES {TRIMESTRE} - '+ df2['Nombre tercero'].apply(lambda x: f'{x}')
    df_COLABORADORES['Fecha registro']= pd.to_datetime(Fecha, format='%d/%m/%Y').strftime('%d/%m/%Y')
    df_COLABORADORES['Fecha de IVA']= df_COLABORADORES['Fecha registro']
    df_COLABORADORES['Tipo documento']= 'Pago'
    df_COLABORADORES['Nº documento']= Num_Documento
    df_COLABORADORES['Tipo mov.']= 'Cuenta'
    df_COLABORADORES['Nº cuenta']= '47510002'                                # RETENCIONES de COLABORADORES !!!
    df_COLABORADORES['Tipo contrapartida']= 'Cuenta'
    df_COLABORADORES['Op. triangular']='No'
    df_COLABORADORES['Corrección']= 'No'
    df_COLABORADORES['Empleados Código']= None                               # RETENCIONES de COLABORADORES !!!
    df_COLABORADORES[['Nº asiento','Importe debe','Importe haber','Importe','Liq. por nº documento','Liq. por tipo documento','Tipo de registro gen.','Grupo contable neg. gen.','Grupo contable prod. gen.','Tipo regis. contrapartida',
    'Gr. contable negocio contrap.','Gr. contable producto contrap.','Código de fraccionamiento','Comentario','Tipo de id.','Nombre de empresa correcto','CIF/NIF correcto','Titulacion Código',
    'Cód. dim. acceso directo 4','Interface Code','Nombre de cuenta','Cta. contrapartida','CECO Código']]=None
    # ORDENACIÓN por DESCRIPCIÓN:
    df_COLABORADORES= df_COLABORADORES.sort_values(by= 'Descripción').reset_index(drop=True)
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

    ## B.3º) CÁLCULO del IMPORTE TOTAL + Nº Retenciones de Colaboradores:
    Importe_Total_Colaboradores= df2['Couta'].sum()    # TOTAL IMPORTE.
    Importe_Total_Colaboradores_VISUALIZACION = '{:,.2f} €'.format(Importe_Total_Colaboradores).replace(',','_').replace('.',',').replace('_','.') # IMPORTE TOTAL PARA VISUALIZAR POR PANTALLA.
    Num_Retenc_Colaboradores= len(df_COLABORADORES)    # Nº Retenciones de Colaboradores.
#==================================================================================================================================================================================================#

### C) PROFESIONALES:
    ## C.1º) LEER DATOS DEL BANCO (+ Modificaciones en la columna de 'Cuenta retención'):
    df3= pd.read_excel(ARCHIVO_EXCEL_RETENCIONES, sheet_name='PROFESIONALES')    # CARGAR DATOS.
    df3['Cuenta retención']= df3['Cuenta retención'].astype('int')           # A tipo "INT".

    # Casos en los que el IMPORTE==0:
    Reten_Importe_0_Profesionales= df3[df3['Couta'] == 0]['Nombre tercero']
    # Quedarse SÓLO con los casos en los que el IMPORTE != 0:
    df3= df3[df3['Couta'] != 0]
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

    ## C.2º) CREAR DataFrame RESULTADO-> PROFESIONALES:
    df_PROFESIONALES= pd.DataFrame()
    df_PROFESIONALES['Importe (DL)']= df3['Couta'].astype(str).str.replace('.', ',')
    df_PROFESIONALES['Descripción']= f'PAGO RETENCIONES {TRIMESTRE} - '+ df3['Nombre tercero'].apply(lambda x: f'{x}')
    df_PROFESIONALES['Fecha registro']= pd.to_datetime(Fecha, format='%d/%m/%Y').strftime('%d/%m/%Y')
    df_PROFESIONALES['Fecha de IVA']= df_PROFESIONALES['Fecha registro']
    df_PROFESIONALES['Tipo documento']= 'Pago'
    df_PROFESIONALES['Nº documento']= Num_Documento
    df_PROFESIONALES['Tipo mov.']= 'Cuenta'
    df_PROFESIONALES['Nº cuenta']= '47510003'                                # RETENCIONES de COLABORADORES !!!
    df_PROFESIONALES['Tipo contrapartida']= 'Cuenta'
    df_PROFESIONALES['Op. triangular']='No'
    df_PROFESIONALES['Corrección']= 'No'
    df_PROFESIONALES['Empleados Código']= None                               # RETENCIONES de COLABORADORES !!!
    df_PROFESIONALES[['Nº asiento','Importe debe','Importe haber','Importe','Liq. por nº documento','Liq. por tipo documento','Tipo de registro gen.','Grupo contable neg. gen.','Grupo contable prod. gen.','Tipo regis. contrapartida',
    'Gr. contable negocio contrap.','Gr. contable producto contrap.','Código de fraccionamiento','Comentario','Tipo de id.','Nombre de empresa correcto','CIF/NIF correcto','Titulacion Código',
    'Cód. dim. acceso directo 4','Interface Code','Nombre de cuenta','Cta. contrapartida','CECO Código']]=None
    # ORDENACIÓN por DESCRIPCIÓN:
    df_PROFESIONALES= df_PROFESIONALES.sort_values(by= 'Descripción').reset_index(drop=True)
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

    ## C.3º) CÁLCULO del IMPORTE TOTAL:
    Importe_Total_Profesionales= df3['Couta'].sum()    # TOTAL IMPORTE.
    Importe_Total_Profesionales_VISUALIZACION = '{:,.2f} €'.format(Importe_Total_Profesionales).replace(',','_').replace('.',',').replace('_','.') # IMPORTE TOTAL PARA VISUALIZAR POR PANTALLA.
    Num_Retenc_Profesionales= len(df_PROFESIONALES)    # Nº Retenciones de Profesionales.
#==================================================================================================================================================================================================#

### D) DataFrame FINAL:
    ## D.1º) CÁLCULO del IMPORTE TOTAL-> BANCO:
    Importe_Total_Linea_BANCO= (Importe_Total_Trabajadores + Importe_Total_Colaboradores + Importe_Total_Profesionales).round(2)
    Importe_Total_Linea_BANCO_VISUALIZACION = '{:,.2f} €'.format(Importe_Total_Linea_BANCO).replace(',','_').replace('.',',').replace('_','.') # IMPORTE TOTAL PARA VISUALIZAR POR PANTALLA.
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

    ## D.2º) Fila INICIAL-> INGRESO BANCO:
    Fila_BANCO = pd.DataFrame([{'Importe (DL)': f'-{Importe_Total_Linea_BANCO}'.replace('.', ','),
                            'Descripción': f'PAGO RETENCIONES {TRIMESTRE}',
                            'Fecha registro': pd.to_datetime(Fecha, format='%d/%m/%Y').strftime('%d/%m/%Y'),
                            'Fecha de IVA': pd.to_datetime(Fecha, format='%d/%m/%Y').strftime('%d/%m/%Y'),
                            'Tipo documento': 'Pago',
                            'Nº documento': Num_Documento,
                            'Tipo mov.': 'Banco',
                            'Nº cuenta': 'SANTANDER02',
                            'Tipo contrapartida': 'Cuenta',

                            'Op. triangular': 'No', 'Corrección': 'No', 'Nº asiento': None, 'Importe debe': None, 'Importe haber': None, 'Importe': None, 'Liq. por nº documento': None, 'Liq. por tipo documento': None,
                            'Tipo de registro gen.': None, 'Grupo contable neg. gen.': None, 'Grupo contable prod. gen.': None, 'Tipo regis. contrapartida': None, 'Gr. contable negocio contrap.': None,
                            'Gr. contable producto contrap.': None, 'Código de fraccionamiento': None, 'Comentario': None, 'Tipo de id.': None, 'Nombre de empresa correcto': None, 'CIF/NIF correcto': None,
                            'Titulacion Código': None, 'Cód. dim. acceso directo 4': None, 'Interface Code': None, 'Nombre de cuenta': None, 'Cta. contrapartida': None, 'Empleados Código': None, 'CECO Código': None}])
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

    ## D.3º) UNIÓN DE Fila_BANCO + LOS 3 DataFrames:
    df_FINAL= pd.concat([Fila_BANCO, df_TRABAJADORES, df_COLABORADORES, df_PROFESIONALES]).reset_index(drop=True)
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

    ## D.4º) ORDENACIÓN DE COLUMNAS:
    df_FINAL= df_FINAL[['Fecha registro', 'Fecha de IVA', 'Nº asiento', 'Tipo documento', 'Nº documento', 'Tipo mov.', 'Nº cuenta', 'Nombre de cuenta', 'Descripción', 'Importe debe', 'Importe haber', 'Importe',
            'Importe (DL)', 'Tipo contrapartida', 'Cta. contrapartida', 'Liq. por nº documento', 'Liq. por tipo documento', 'Op. triangular', 'Empleados Código', 'CECO Código', 'Tipo de registro gen.',
            'Grupo contable neg. gen.', 'Grupo contable prod. gen.', 'Tipo regis. contrapartida', 'Gr. contable negocio contrap.', 'Gr. contable producto contrap.', 'Código de fraccionamiento', 'Corrección',
            'Comentario', 'Tipo de id.', 'Nombre de empresa correcto', 'CIF/NIF correcto', 'Titulacion Código', 'Cód. dim. acceso directo 4', 'Interface Code']]
#==================================================================================================================================================================================================#
    return df_FINAL, Importe_Total_Linea_BANCO_VISUALIZACION, Importe_Total_Trabajadores_VISUALIZACION, Importe_Total_Colaboradores_VISUALIZACION, Importe_Total_Profesionales_VISUALIZACION, Num_Retenc_Trabajadores, Num_Retenc_Colaboradores, Num_Retenc_Profesionales, Reten_Importe_0_Trabajadores, Reten_Importe_0_Colaboradores, Reten_Importe_0_Profesionales
############################################################################################################################################################################################


def PAGO_REMESA_PROVEEDORES(LISTA_PROVEEDORES, EXCEL_REMESA_PROVEEDORES, Fecha, Num_Documento):
## A) TRATAMIENTO DEL EXCEL DE PROVEEDORES:
    # A.0º) Lectura de los datos LISTA PROVEEDORES:
    df_codigo_proveedores= pd.read_excel(LISTA_PROVEEDORES)
    df_codigo_proveedores= df_codigo_proveedores.map(lambda s: s.upper() if type(s)==str else s)  # Conversión de todos los campos a MAYÚSCULAS.
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # A.1º) Eliminación de las tildes y cambio de Ñ por N:
    df_codigo_proveedores['Nombre']= df_codigo_proveedores['Nombre'].replace({'Á':'A', 'É':'E', 'Í':'I', 'Ó':'O', 'Ú':'U', 'Ñ':'N', 'A. ':'A ', "D'":'D'}, regex=True)
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # A.2º) Sustitución de "M." y "Mª" por MARIA:
    df_codigo_proveedores['Nombre']= df_codigo_proveedores['Nombre'].replace({'Mª':'MARIA', 'M[.]':'MARIA ', 'M[?]':'MARIA '}, regex=True)
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # A.3º) Añadir un ESPACIO (Temporal) detrás de cada coma:
    df_codigo_proveedores['Nombre']= df_codigo_proveedores['Nombre'].str.replace(',', ', ')
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # A.4º) Eliminación de "." "," y "-":
    df_codigo_proveedores['Nombre'] = df_codigo_proveedores['Nombre'].apply(lambda x: re.sub(r'\. ', '', str(x)))   # Quitar "." + Espacio (Y luego quitar el ".")!!
    df_codigo_proveedores['Nombre']= df_codigo_proveedores['Nombre'].str.replace('[.,]','', regex=True)
    df_codigo_proveedores['Nombre']= df_codigo_proveedores['Nombre'].str.replace('-',' ', regex=True)
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # A.5º) Eliminación de texto entre paréntesis (ó "(..."):
    df_codigo_proveedores['Nombre']= df_codigo_proveedores['Nombre'].astype(str).apply(lambda x: re.sub(r'\(.*\)', '', x))
    df_codigo_proveedores['Nombre']= df_codigo_proveedores['Nombre'].astype(str).apply(lambda x: re.sub(r'\(.*', '', x))
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # A.6º) Eliminación de espacios innecesarios al principio y al final de cada cadena de texto:
    df_codigo_proveedores['Nombre']= df_codigo_proveedores['Nombre'].str.strip()
    def eliminar2espacios(texto):
        if isinstance(texto, str):
            return re.sub(r'\s{2,}', ' ', texto)   # CAMBIAR 2 ó + ESPACIOS-> Por 1 SÓLO.
        else:
            return texto
    df_codigo_proveedores['Nombre']= df_codigo_proveedores['Nombre'].apply(eliminar2espacios) # Aplica la función anterior a la columna 'Nombre'.
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # A.7º) Quedarse sólo con las columnas que interesan:
    df_codigo_proveedores= df_codigo_proveedores[['Nº', 'Nombre', 'Nº teléfono', 'Contacto', 'Alias', 'Saldo (DL)', 'Saldo vencido (DL)', 'Pagos (DL)']]
#==========================================================================================================================================================================================#

## B) TRATAMIENTO DEL EXCEL DE LA REMESA DEL BANCO:
    # B.0º) Lectura de los datos BANCO:
    df_banco_proveedores= pd.read_excel(EXCEL_REMESA_PROVEEDORES, header=15)  # Cargo los datos de la REMESA de PROVEEDORES e indico la Fila del Encabezado.
    df_banco_proveedores= df_banco_proveedores.map(lambda s: s.upper() if type(s)==str else s)  # Conversión de todos los campos a MAYÚSCULAS.
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # B.1º) Eliminación de las tildes y cambio de Ñ por N:
    df_banco_proveedores['Beneficiario_tratado'] = df_banco_proveedores['Beneficiario'].replace({'Á':'A', 'É':'E', 'Í':'I', 'Ó':'O', 'Ú':'U', 'Ñ':'N', 'A. ':'A ', "D'":'D'}, regex=True)
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # B.2º) Sustitución de "M." y "Mª" por MARIA:
    df_banco_proveedores['Beneficiario_tratado'] = df_banco_proveedores['Beneficiario_tratado'].replace({'Mª':'MARIA', 'M[.]':'MARIA ', 'M[?]':'MARIA '}, regex=True)
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # B.3º) Añadir un ESPACIO (Temporal) detrás de cada coma:
    df_banco_proveedores['Beneficiario_tratado']= df_banco_proveedores['Beneficiario_tratado'].str.replace(',', ', ')
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # B.4º) Eliminación de "." "," y "-":
    df_banco_proveedores['Beneficiario_tratado'] = df_banco_proveedores['Beneficiario_tratado'].apply(lambda x: re.sub(r'\. ', '', str(x)))   # Quitar "." + Espacio (Y luego quitar el ".")!!
    df_banco_proveedores['Beneficiario_tratado']= df_banco_proveedores['Beneficiario_tratado'].str.replace('[.,]','', regex=True)
    df_banco_proveedores['Beneficiario_tratado']= df_banco_proveedores['Beneficiario_tratado'].str.replace('-',' ', regex=True)
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # B.5º) Eliminación de texto entre paréntesis (ó "(..."):
    df_banco_proveedores['Beneficiario_tratado']= df_banco_proveedores['Beneficiario_tratado'].astype(str).apply(lambda x: re.sub(r'\(.*\)', '', x))
    df_banco_proveedores['Beneficiario_tratado']= df_banco_proveedores['Beneficiario_tratado'].astype(str).apply(lambda x: re.sub(r'\(.*', '', x))
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # B.6º) Eliminación de espacios innecesarios al principio y al final de cada cadena de texto:
    df_banco_proveedores['Beneficiario_tratado']= df_banco_proveedores['Beneficiario_tratado'].str.strip()
    def eliminar2espacios(texto):
        if isinstance(texto, str):
            return re.sub(r'\s{2,}', ' ', texto)   # CAMBIAR 2 ó + ESPACIOS-> Por 1 SÓLO.
        else:
            return texto
    df_banco_proveedores['Beneficiario_tratado']= df_banco_proveedores['Beneficiario_tratado'].apply(eliminar2espacios) # Aplica la función anterior a la columna 'Nombre'.
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # B.7º) Modificación de la columna del IMPORTE:
    df_banco_proveedores['Importe']= df_banco_proveedores['Importe'].str.replace(' EUR','', regex=True)      # Eliminar "EUR".
    df_banco_proveedores['Importe']= '-' + df_banco_proveedores['Importe'].str.replace('[.]','', regex=True) # Eliminar el "." y poner el Importe en NEGATIVO.
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # B.8º) Creación de NUEVA COLUMNA-> "CONCEPTO - PROVEEDOR" para Business Central:
    df_banco_proveedores['DESCRIPCION_BC']= df_banco_proveedores.Concepto + ' - ' + df_banco_proveedores.Beneficiario
#==========================================================================================================================================================================================#

## C) UNIÓN DE LOS 2 DF SEGÚN EL NOMBRE "TRATADO"-> PARA CONSEGUIR EL " Nº PROVEEDOR":
    df_resultado= pd.merge(df_banco_proveedores, df_codigo_proveedores,                     # Df's a unir.
                            left_on='Beneficiario_tratado', right_on='Nombre',              # A la izquierda el Df_BANCO y a la derecha Df_CÓDIGO_PROVEEDORES.
                            how='left')                                                     # Unión por el Df de la Izquierda (BANCO).

    # C.1º) "np.where" para dejar el 'CÓDIGO' sólo cuando COINCIDEN (y deja los demás como 'NaN'):
    df_resultado['Nº']= np.where(df_resultado['Nº'].notna(), df_resultado['Nº'], np.nan)

    # C.2º) Columnas que se mantendrán en el resultado:
    df_resultado= df_resultado[['Nº','Beneficiario', 'Beneficiario_tratado', 'DESCRIPCION_BC', 'Importe']]
#==========================================================================================================================================================================================#

## D) CREACIÓN DEL DataFrame PARA SUBIR A "BUSINESS CENTRAL":
    df= pd.DataFrame()
    df['Importe (DL)']= df_resultado['Importe']
    df['Descripción']= df_resultado['DESCRIPCION_BC']
    df['Fecha registro']= pd.to_datetime(Fecha, format='%d/%m/%Y').strftime('%d/%m/%Y')
    df['Fecha de IVA']= df['Fecha registro']
    df['Tipo documento']= 'Pago'
    df['Nº documento']= Num_Documento
    df['Tipo mov.']= 'Banco'
    df['Nº cuenta']= 'SANTANDER02'
    df['Tipo contrapartida']= 'Proveedor'
    df['Cta. contrapartida']= df_resultado['Nº']
    df['Op. triangular']='No'
    df['Corrección']= 'No'
    df[['Nº asiento','Importe debe','Importe haber','Importe','Liq. por nº documento','Liq. por tipo documento','Tipo de registro gen.','Grupo contable neg. gen.','Grupo contable prod. gen.','Tipo regis. contrapartida',
    'Gr. contable negocio contrap.','Gr. contable producto contrap.','Código de fraccionamiento','Comentario','Tipo de id.','Nombre de empresa correcto','CIF/NIF correcto','Titulacion Código',
    'Cód. dim. acceso directo 4','Interface Code','Nombre de cuenta','Empleados Código','CECO Código']]=None
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

    # D.1º) ORDENACIÓN DE COLUMNAS:
    df_FINAL= df[['Fecha registro', 'Fecha de IVA', 'Nº asiento', 'Tipo documento', 'Nº documento', 'Tipo mov.', 'Nº cuenta', 'Nombre de cuenta', 'Descripción', 'Importe debe', 'Importe haber', 'Importe',
            'Importe (DL)', 'Tipo contrapartida', 'Cta. contrapartida', 'Liq. por nº documento', 'Liq. por tipo documento', 'Op. triangular', 'Empleados Código', 'CECO Código', 'Tipo de registro gen.',
            'Grupo contable neg. gen.', 'Grupo contable prod. gen.', 'Tipo regis. contrapartida', 'Gr. contable negocio contrap.', 'Gr. contable producto contrap.', 'Código de fraccionamiento', 'Corrección',
            'Comentario', 'Tipo de id.', 'Nombre de empresa correcto', 'CIF/NIF correcto', 'Titulacion Código', 'Cód. dim. acceso directo 4', 'Interface Code']]
#==========================================================================================================================================================================================#

## E) VISUALIZAR SÓLO LOS CASOS EN LOS QUE NO SE HA CONSEGUIDO UNIR EL "CODIGO PROVEEDOR":
    Códigos_FALTANTES= df_resultado[df_resultado['Nº'].isna()].copy()                # QUEDARSE CON LOS QUE NO COINCIDEN CON EL CÓDIGO.
#==========================================================================================================================================================================================#

## F) COMPARACIÓN Nº FILAS BANCO vs. Nº FILAS UNIÓN:
    num_Filas_BANCO= len(df_banco_proveedores)
    num_Filas_UNION= len(df_resultado)

    return df_FINAL, Códigos_FALTANTES, num_Filas_BANCO, num_Filas_UNION
############################################################################################################################################################################################

## A) CONFIGURACIÓN GENERAL DE LA PÁGINA WEB:
st.set_page_config(page_title="REMESAS UCAV",                                                                             # Nombre en el Navegador.
                   page_icon="https://raw.githubusercontent.com/Miguelgargor/IMAGENES_APPs/main/logoUcav_navegador.png",  # Icono del Navegador.
                   layout="wide",                                                                                         # Mostrarlo en toda la pantalla.
                   initial_sidebar_state="expanded")                                                                      # Mostrar la barra lateral inicialmente.
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

## B) BARRA LATERAL: (Indicar el Tipo de Remesa):
st.sidebar.title('⚙️ :red[REMESAS]') # TÍTULO BARRA LATERAL.
# OPCIONES:
INICIO=':house: **INICIO**'; NOMINAS=':moneybag: **NÓMINAS**'; SEGUROS_SALUD=':heart: **SEGUROS SALUD**'; RETENCIONES=':classical_building: **RETENCIONES**'; PROVEEDORES= ':package: **PAGO FRAS. PROVEEDORES/REC. COL.**'
ELEGIR_OPCION= st.sidebar.radio(label=' ', label_visibility='hidden',                                                                                                  # Título Oculto Selector.
                                options=[INICIO, NOMINAS, SEGUROS_SALUD, RETENCIONES, PROVEEDORES],                                                                    # Opciones.
                                captions=['','*Remesa de Nóminas.*', '*Ingreso de Seguros de Salud.*', '*Pago de Retenciones.*', '*Pago remesa de Proveedores y Rec. Colaboración.*'])     # Texto Explicativo debajo de cada Opción.

st.sidebar.divider() # Divisor.
st.sidebar.write(''); st.sidebar.write(''); st.sidebar.write(''); st.sidebar.write(''); st.sidebar.write(''); st.sidebar.write('')
st.sidebar.write(':e-mail: ***Contacto de ayuda:***')        ## CONTACTO (De ayuda) ##
st.sidebar.write('miguel.garcia@ucavila.es')
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

## C) CUERPO DE LA PÁGINA WEB-> INICIO: (PÁGINA POR DEFECTO):
if ELEGIR_OPCION== INICIO:
    col1, col2, col3 = st.columns([40, 0.5, 59.95])   # COLUMNAS CON DISTINTOS ANCHOS. (En %).
    with col1:                       # URL HIPERVÍNCULO #      # Se abrirá en una nueva pestaña #    # URL IMAGEN #                                                                     # ANCHO #
        col1 = st.markdown('<a href="https://www.ucavila.es/" target="_blank"><img src="https://raw.githubusercontent.com/Miguelgargor/IMAGENES_APPs/main/UCAV_logo.png" alt="UCAV Logo" width="300"></a>',
                        unsafe_allow_html=True) # Permitir usar HTML #

    with col3:               #h1: Encabezado# #Color#   #Texto#                #Permitir HTML#
        col3= st.markdown(f'<h1 style="color:#024868;">REMESAS UCAV</h1>', unsafe_allow_html=True)
    #--------------------------------------------------------------------------------------#
    st.write(''); st.write('') # LÍNEAS en BLANCO.
    # Escritura.
    st.markdown('#### Genera las remesas necesarias de manera precisa, facilitando su registro en Business Central.')
    st.markdown('#### Elija la remesa que desee en la barra lateral.')
############################################################################################################################################################################################

## D) CUERPO DE LA PÁGINA WEB-> NÓMINAS:
if ELEGIR_OPCION== NOMINAS:
    col1, col2, col3 = st.columns([40, 0.5, 59.95])   # COLUMNAS CON DISTINTOS ANCHOS. (En %).

    ## D.1.) IMAGEN CON HIPERVÍNCULO: (En la Columna 1) + TÍTULO PÁGINA WEB (En la Columna 3) + TEXTO EXPLICATIVO:
    with col1:                       # URL HIPERVÍNCULO #      # Se abrirá en una nueva pestaña #    # URL IMAGEN #                                                                     # ANCHO #
        col1 = st.markdown('<a href="https://www.ucavila.es/" target="_blank"><img src="https://raw.githubusercontent.com/Miguelgargor/IMAGENES_APPs/main/UCAV_logo.png" alt="UCAV Logo" width="300"></a>',
                        unsafe_allow_html=True) # Permitir usar HTML #

    with col3:               #h1: Encabezado# #Color#   #Texto#                        #Permitir HTML#
        col3= st.markdown(f'<h1 style="color:#024868;">PAGO DE NÓMINAS UCAV</h1>', unsafe_allow_html=True)
        #--------------------------------------------------------------------------------------#
    st.write(''); st.write('') # LÍNEAS en BLANCO.
    # Escritura.
    st.write('Genera el documento de ***Nóminas*** de manera precisa, facilitando su registro en Business Central. (Es importante ***abrir el archivo y guardarlo nuevamente*** debido a posibles incompatibilidades con Business Central).')
    st.write('Primero elige las opciones necesarias a continuación. Después, sólamente tienes que pulsar en *"**GENERAR ASIENTOS CONTABLES**"*.')
    st.write(''); st.write('') # LÍNEAS en BLANCO.
    #========================================================================================================================================================================================#

    ## D.2.) OPCIONES (INPUTS):
    st.divider()
    st.markdown('##### :red[OPCIONES]')    # Título en rojo.
    # 2 FILAS de COLUMNAS:
    c1, c2= st.columns(2)
    c3, c4, c5= st.columns(3)

    #.................................................................#
    with c1:
        st.markdown('###### :open_file_folder: LISTA DE EMPLEADOS:')              # Encabezado + SÍMBOLO CARPETA.
        with st.expander(':blue[**Cargar excel con la Lista de Empleados**]'): # BOTÓN QUE SE ABRE.
            LISTA_EMPLEADOS = st.file_uploader(label='Lista_Empleados', type=["xlsx", "xls"], label_visibility='collapsed')        # SUBIR UN ARCHIVO.
    #.................................................................#
    with c2:
        st.markdown('###### :open_file_folder: REMESA NÓMINAS BANCO:')            # Encabezado + SÍMBOLO CARPETA.
        with st.expander(':blue[**Cargar excel con la Remesa de Nóminas**]'):  # BOTÓN QUE SE ABRE.
            REMESA_NOMINAS_BANCO = st.file_uploader(label='Remesa_Banco', type=["xlsx", "xls"], label_visibility='collapsed')      # SUBIR UN ARCHIVO.
    #.................................................................#
    with c3:
        st.markdown('###### :calendar: FECHA DE PAGO:', help=':blue[**dd/mm/yyyy**] ')                           # TÍTULO + SÍMBOLO CALENDARIO.
        # Obtener la fecha del DÍA 28 del MES ANTERIOR al actual:
        Fecha_defecto= datetime.now() - timedelta(days=datetime.now().day)     # ÚLTIMO DÍA MES ANTERIOR (Fecha Actual - Día Actual de Este Mes= Último Día Mes Anterior).
        Fecha_defecto= Fecha_defecto.replace(day=28)                           # REEMPLAZAR POR EL DÍA 28.
        Fecha= st.date_input(label=":blue[**Fecha de Pago**]", value=Fecha_defecto, format="DD/MM/YYYY", label_visibility='collapsed') # ENTRADA DE FECHA.
    #.................................................................#
    with c4:
        st.markdown('###### :page_with_curl: Nº DOCUMENTO:', help=':blue[**Ejemplo:**] BS2324-0001') # TÍTULO + SÍMBOLO HOJA.
        Num_Documento= st.text_input(label='Nº Doc.', label_visibility='collapsed')                # ENTRADA DE TEXTO.
    #.................................................................#
    with c5:
        st.markdown('###### :lower_left_ballpoint_pen: MES PAGO (DESCRIPCIÓN):', help=':blue[**Ejemplo:**] ENE24')                 # TÍTULO + SÍMBOLO BOLSA DINERO.
        Mes_Pago= st.text_input(label='Mes_Pago', label_visibility='collapsed')                    # ENTRADA DE TEXTO.
    st.divider()                                                                               # LÍNEA HORIZONTAL.
    #========================================================================================================================================================================================#

    ## D.3.) BOTÓN de EJECUCIÓN:                                                             ## ¡¡FUNCIÓN!! ##
    if st.button(":blue[**GENERAR ASIENTOS CONTABLES**]"):    # De color AZUL (:blue[]) y en NEGRITA(** **).
        if LISTA_EMPLEADOS is not None and REMESA_NOMINAS_BANCO is not None:
            try:
                with st.spinner('Cargando...'):      ### CARGANDO... ###
                    # Llamar a la función:
                    df_BusinessCentral, Códigos_FALTANTES, num_Filas_BANCO, num_Filas_UNION= PAGO_NOMINAS_UCAV(LISTA_EMPLEADOS, REMESA_NOMINAS_BANCO, Fecha, Num_Documento, Mes_Pago)
                    #··································································#

        ## D.4.) VISUALIZAR Y GUARDAR EL RESULTADO:
                    Ver_df_BusinessCentral= df_BusinessCentral.copy()                       # a) COPIA para NO Modificar el original.
                    Ver_df_BusinessCentral= Ver_df_BusinessCentral.reset_index(drop=True)   # b) RESETEAR el ÍNDICE (y eliminar el anterior).
                    Ver_df_BusinessCentral.index= Ver_df_BusinessCentral.index+1            # c) Empezar el ÍNDICE desde el 1.

                    # d) FORMATO DE FECHA ¡EN STREAMLIT!:
                    Ver_df_BusinessCentral['Fecha']= Ver_df_BusinessCentral['Fecha'].apply(lambda x: x.strftime("%d/%m/%Y"))

                    # e) REPRESENTAR LOS NÚMERO DE EMPLEADO COMO STRINGS Y SUSTITUIR "<NA>" POR "":
                    Ver_df_BusinessCentral['No. Empleado'] = Ver_df_BusinessCentral['No. Empleado'].astype(str).replace('[,.]', '', regex=True).replace('<NA>','')

                    # f) CAMBIOS EN LA "," (Decimales) Y EL "." (Miles) DEL "IMPORTE": [.->_ // ,->. // _->,]:
                    Ver_df_BusinessCentral['Importe'] = Ver_df_BusinessCentral['Importe'].str.replace(',', '.').astype('float').apply(lambda x: '{:,.2f}'.format(x).replace('.', '_').replace(',', '.').replace('_', ','))

                    # g) 2 COLUMNAS-> IMPORTE_TOTAL y Si se han conseguido las FILAS correctas ó no. (El mismo Nº de Filas que la Remesa del Banco).
                    cl1, cl2= st.columns(2)
                    with cl1:
                        st.markdown(f"#### :blue[Importe Total:] {df_BusinessCentral['Importe'].replace(',','.',regex=True).astype('float').sum():,.2f} €".replace('.', '_').replace(',', '.').replace('_', ',')) # IMPORTE TOTAL DE LA REMESA "BC" (Con cambios necesarios: . y , // Y tipo FLOAT).

                    with cl2:
                        if num_Filas_BANCO==num_Filas_UNION:                               # COMPARACIÓN Nº FILAS BANCO vs. Nº FILAS UNIÓN.
                            st.success(' :blue[**Número de pagos correcto.** (No hay duplicados).]', icon="✅") # MENSAJE de ÉXITO.
                        else:
                            st.warning(f':red[***¡NÚMERO DE PAGOS INCORRECTO!***] (El Banco indica que este mes hay :red[**{num_Filas_BANCO}**] pagos; y se han obtenido :red[**{num_Filas_UNION}**]. **¡Revisar si hay DUPLICADOS (con diferente Nº Empleado) en la "Lista de Empleados"!**).', icon="⚠️")
                    st.write(''); st.write('') # LÍNEAS en BLANCO.  

                    #...........................................................................................................................................#
                    ## !! VISUALIZAR los CASOS_SIN Nº EMPLEADO:
                    Ver_Códigos_FALTANTES= Códigos_FALTANTES.copy()                     # a!) COPIA para NO Modificar el original.
                    Ver_Códigos_FALTANTES= Ver_Códigos_FALTANTES.reset_index(drop=True) # b!) RESETEAR el ÍNDICE (y eliminar el anterior).
                    Ver_Códigos_FALTANTES.index= Ver_Códigos_FALTANTES.index+1          # c!) Empezar el ÍNDICE desde el 1.

                    # d!) REPRESENTAR LOS NÚMERO DE EMPLEADO COMO STRINGS Y SUSTITUIR "<NA>" POR "":
                    Ver_Códigos_FALTANTES['Nº'] = Ver_Códigos_FALTANTES['Nº'].astype(str).replace('<NA>','')

                    # e!) CAMBIOS EN LA "," (Decimales) Y EL "." (Miles) DEL "IMPORTE": [.->_ // ,->. // _->,]:
                    Ver_Códigos_FALTANTES['Importe'] = Ver_Códigos_FALTANTES['Importe'].str.replace(',', '.').astype('float').apply(lambda x: '{:,.2f}'.format(x).replace('.', '_').replace(',', '.').replace('_', ','))

                    # f!) MOSTRAR los CASOS_SIN Nº EMPLEADO (En caso de que los haya [df>0]):
                    if len(Códigos_FALTANTES)>0:  # Si hay algún caso que no se encuentre el Nº Empleado... ("CÓDIO EMPLEADO"= NAN):
                        st.warning(f' :red[**NO SE HAN CONSEGUIDO LOS**] :green[**{len(Códigos_FALTANTES)}**] :red[**Nº DE EMPLEADO SIGUIENTES:** *(Comprobar los nombres del empleado)*:]', icon='⚠️') # WARNING.
                        st.dataframe(Ver_Códigos_FALTANTES)                                                      # MOSTRAR CASOS SIN Nº EMPLEADO.
                    #...........................................................................................................................................#

                    # h) MOSTRAR el DF_RESULTADO:
                    st.write(''); st.write('') # LÍNEAS en BLANCO.  
                    st.subheader('📍 ARCHIVO BUSINESS CENTRAL:')
                    st.dataframe(Ver_df_BusinessCentral)

                    ### i) DESCARGAR EL RESULTADO:
                    data_csv= df_BusinessCentral.to_csv(sep=';',                           # SEPARADOR (En Columnas).
                                                        encoding='utf-8',                  # ENCODING.
                                                        date_format='%d/%m/%Y',            # FORMATO de la FECHA.
                                                        index=False)                       # SIN Índice.
                    ## BOTÓN de DOWNLOAD!!
                    st.download_button(label=':green[**Descargar Nóminas**] :inbox_tray:', # NOMBRE del BOTÓN. (Verde y Negrita + Emoji).
                                    data= data_csv,                                     # DATOS.
                                    file_name= f'PAGO_NOMINAS_BC_{Mes_Pago}.csv')       # NOMBRE ARCHIVO que se GUARDA.
                #..................................................................................................................................................................#

            except Exception as e:             # Si al intentar ejecutar la FUNCIÓN hay un ERROR...
                st.error(f"Error: {str(e)}")
        else:
            st.warning(' ¡Cargue los archivos correctos con la lista de empleados y la remesa de nóminas del banco!', icon="⚠️") # Muestra como WARNING si NO has insertado los ARCHIVOS CORRECTOS de DATOS.
############################################################################################################################################################################################

## E) CUERPO DE LA PÁGINA WEB-> SEGUROS SALUD:
if ELEGIR_OPCION== SEGUROS_SALUD:
    col1, col2, col3 = st.columns([40, 0.5, 59.95])   # COLUMNAS CON DISTINTOS ANCHOS. (En %).

    ## E.1.) IMAGEN CON HIPERVÍNCULO: (En la Columna 1) + TÍTULO PÁGINA WEB (En la Columna 3) + TEXTO EXPLICATIVO:
    with col1:                       # URL HIPERVÍNCULO #      # Se abrirá en una nueva pestaña #    # URL IMAGEN #                                                                     # ANCHO #
        col1 = st.markdown('<a href="https://www.ucavila.es/" target="_blank"><img src="https://raw.githubusercontent.com/Miguelgargor/IMAGENES_APPs/main/UCAV_logo.png" alt="UCAV Logo" width="300"></a>',
                        unsafe_allow_html=True) # Permitir usar HTML #

    with col3:               #h1: Encabezado# #Color#   #Texto#                              #Permitir HTML#
        col3= st.markdown(f'<h1 style="color:#024868;">INGRESO SEGUROS DE SALUD UCAV</h1>', unsafe_allow_html=True)
        #--------------------------------------------------------------------------------------#
    st.write(''); st.write('') # LÍNEAS en BLANCO.
    # Escritura.
    st.write('Genera el documento de los ingresos mensuales de ***Seguros de Salud*** de manera precisa, para tan solo tener que ***copiar y pegar***, facilitando su registro en Business Central.')
    st.write('Primero elige las opciones necesarias a continuación. Después, sólamente tienes que pulsar en *"**GENERAR ASIENTOS CONTABLES**"*.')
    st.write(''); st.write('') # LÍNEAS en BLANCO.
    #========================================================================================================================================================================================#

    ## E.2.) OPCIONES (INPUTS):
    st.divider()
    st.markdown('##### :red[OPCIONES]')    # Título en rojo.
    # 2 FILAS de COLUMNAS:
    c1, c2= st.columns(2)
    c3, c4, c5= st.columns(3)

    #.................................................................#
    with c1:
        st.markdown('###### :open_file_folder: INGRESO SEGUROS DE SALUD BANCO:')                    # Encabezado + SÍMBOLO CARPETA.
        with st.expander(':blue[**Cargar excel con la remesa de Ingresos por Seguros de Salud**]'): # BOTÓN QUE SE ABRE.
            ARCHIVO_EXCEL_SEGUROS = st.file_uploader(label='SS_Banco', type=["xlsx", "xls"], label_visibility='collapsed')         # SUBIR UN ARCHIVO.
    #.................................................................#
    with c2:
        st.markdown('###### :heavy_dollar_sign: COMISIÓN BANCO:', help=':blue[**EN POSITIVO:**] (**Ejemplo:** 50,34)')         # Encabezado + SÍMBOLO CARPETA.
        COMISION_BANCO= st.number_input(label='Comisión Banco', label_visibility='collapsed')  # ENTRADA DE NÚMERO "FLOAT".
    #.................................................................#
    with c3:
        st.markdown('###### :calendar: FECHA:', help=':blue[**dd/mm/yyyy**] ')                           # TÍTULO + SÍMBOLO CALENDARIO.
        # Obtener la fecha del DÍA 28 del MES ANTERIOR al actual:
        Fecha_defecto= datetime.now() - timedelta(days=datetime.now().day)     # ÚLTIMO DÍA MES ANTERIOR (Fecha Actual - Día Actual de Este Mes= Último Día Mes Anterior).
        Fecha_defecto= Fecha_defecto.replace(day=28)                           # REEMPLAZAR POR EL DÍA 28.
        Fecha= st.date_input(label=":blue[**Fecha-SS**]", value=Fecha_defecto, format="DD/MM/YYYY", label_visibility='collapsed') # ENTRADA DE FECHA.
    #.................................................................#
    with c4:
        st.markdown('###### :page_with_curl: Nº DOCUMENTO:', help=':blue[**Ejemplo:**] BS2324-0001') # TÍTULO + SÍMBOLO HOJA.
        Num_Documento= st.text_input(label='Nº Doc-SS.', label_visibility='collapsed')               # ENTRADA DE TEXTO.
    #.................................................................#
    with c5:
        st.markdown('###### :lower_left_ballpoint_pen: MES (DESCRIPCIÓN):', help=':blue[**Ejemplo:**] ENE24')                # TÍTULO + SÍMBOLO BOLSA DINERO.
        Mes= st.text_input(label='Mes-SS', label_visibility='collapsed')                       # ENTRADA DE TEXTO.
    st.divider()                                                                               # LÍNEA HORIZONTAL.
    #========================================================================================================================================================================================#

    ## E.3.) BOTÓN de EJECUCIÓN:                                                             ## ¡¡FUNCIÓN!! ##
    if st.button(":blue[**GENERAR ASIENTOS CONTABLES**]"):    # De color AZUL (:blue[]) y en NEGRITA(** **).
        if ARCHIVO_EXCEL_SEGUROS is not None:
            try:
                with st.spinner('Cargando...'):      ### CARGANDO... ###
                    # Llamar a la función:
                    df_FINAL, Importe_Total_VISUALIZACION= INGRESOS_SEGUROS_UCAV(ARCHIVO_EXCEL_SEGUROS, Fecha, Num_Documento, Mes, COMISION_BANCO)
                    #··································································#

        ## E.4.) VISUALIZAR Y GUARDAR EL RESULTADO:
                    Ver_df_BusinessCentral= df_FINAL[['Fecha registro','Tipo documento','Nº documento','Tipo mov.',           # SÓLO COLUMNAS IMPORTANTES #
                                                      'Nº cuenta','Descripción','Importe (DL)','Tipo contrapartida','Cta. contrapartida']].copy() # a) COPIA para NO Modificar el original.
                    Ver_df_BusinessCentral= Ver_df_BusinessCentral.reset_index(drop=True)  # b) RESETEAR el ÍNDICE (y eliminar el anterior).
                    Ver_df_BusinessCentral.index= Ver_df_BusinessCentral.index+1           # c) Empezar el ÍNDICE desde el 1.

                    # d) 2 COLUMNAS-> IMPORTE_TOTAL y Si se han conseguido las FILAS correctas ó no. (El mismo Nº de Filas que la Remesa del Banco).
                    cl1, cl2= st.columns(2)
                    with cl1:
                        st.markdown(f"#### :blue[Importe Total:] {Importe_Total_VISUALIZACION} €") # IMPORTE TOTAL DE LA REMESA "BC".

                    with cl2:
                        st.success(f':blue[**Número de ingresos:**] :red[**{len(df_FINAL)-2}**]') # Nº INGRESOS (Nº Filas - 2 [Banco + Comisiones]).
                    st.write(''); st.write('') # LÍNEAS en BLANCO.  

                    # e) MOSTRAR el DF_RESULTADO:
                    st.write(''); st.write('') # LÍNEAS en BLANCO.  
                    st.subheader('📍 ARCHIVO BUSINESS CENTRAL:')
                    st.dataframe(Ver_df_BusinessCentral)

                    ### f) DESCARGAR EL RESULTADO:
                    Excel_buffer= io.BytesIO()                                              # Almacén de DATOS BINARIOS.
                    with pd.ExcelWriter(Excel_buffer, engine='xlsxwriter') as Excel_writer: # Cualquier cosa que se ESCRIBA dentro de esto-> Irá al BUFFER (Almacén) BINARIO.
                        df_FINAL.to_excel(Excel_writer, index=False, sheet_name='SEGUROS SALUD')    # Escribimos como EXCEL el DATAFRAME del resultado.

                    # Obtener el CONTENIDO BINARIO del archivo Excel:
                    Excel_Binario= Excel_buffer.getvalue()                                  # Conseguir el CONTENIDO del ARCHIVO anterior BINARIO (El del Buffer).

                    # BOTÓN de DOWNLOAD!!
                    st.download_button(label=':green[**Descargar Seguros de Salud**] :inbox_tray:', # NOMBRE del BOTÓN. (Verde y Negrita + Emoji).
                                       data=Excel_Binario,                                          # DATOS-> BINARIOS.
                                       file_name=f'INGRESO_SEGUROS_SALUD_BC_{Mes}.xlsx')            # NOMBRE ARCHIVO que se GUARDA.
                #..................................................................................................................................................................#

            except Exception as e:             # Si al intentar ejecutar la FUNCIÓN hay un ERROR...
                st.error(f"Error: {str(e)}")
        else:
            st.warning(' ¡Cargue el archivo correcto con la remesa de Seguros de Salud del banco!', icon="⚠️") # Muestra como WARNING si NO has insertado el ARCHIVO CORRECTO de DATOS.
############################################################################################################################################################################################
            
## F) CUERPO DE LA PÁGINA WEB-> RETENCIONES:
if ELEGIR_OPCION== RETENCIONES:
    col1, col2, col3 = st.columns([40, 0.5, 59.95])   # COLUMNAS CON DISTINTOS ANCHOS. (En %).

    ## F.1.) IMAGEN CON HIPERVÍNCULO: (En la Columna 1) + TÍTULO PÁGINA WEB (En la Columna 3) + TEXTO EXPLICATIVO:
    with col1:                       # URL HIPERVÍNCULO #      # Se abrirá en una nueva pestaña #    # URL IMAGEN #                                                                     # ANCHO #
        col1 = st.markdown('<a href="https://www.ucavila.es/" target="_blank"><img src="https://raw.githubusercontent.com/Miguelgargor/IMAGENES_APPs/main/UCAV_logo.png" alt="UCAV Logo" width="300"></a>',
                        unsafe_allow_html=True) # Permitir usar HTML #

    with col3:               #h1: Encabezado# #Color#   #Texto#                              #Permitir HTML#
        col3= st.markdown(f'<h1 style="color:#024868;">PAGO RETENCIONES UCAV</h1>', unsafe_allow_html=True)
        #--------------------------------------------------------------------------------------#
    st.write(''); st.write('') # LÍNEAS en BLANCO.
    # Escritura.
    st.write('Genera el documento del pago de ***Retenciones (de Trabajadores, Colaboradores y Profesionales)*** de manera precisa, para tan solo tener que ***copiar y pegar***, facilitando su registro en Business Central.')
    st.write('Primero elige las opciones necesarias a continuación. Después, sólamente tienes que pulsar en *"**GENERAR ASIENTOS CONTABLES**"*.')
    st.write(''); st.write('') # LÍNEAS en BLANCO.

    st.subheader('**INDICACIONES:**')                   ## INDICACIONES para que funcione correctamente ##
    st.write('- El **nombre de las hojas del archivo Excel** deben ser: **TRABAJADORES**, **COLABORADORES** y **PROFESIONALES**.')
    st.write('- **NO** debe haber ningún ***"sumatorio"*** de ninguna tabla.')
    st.write(''); st.write('') # LÍNEAS en BLANCO.
    #========================================================================================================================================================================================#

    ## F.2.) OPCIONES (INPUTS):
    st.divider()
    st.markdown('##### :red[OPCIONES]')    # Título en rojo.
    # FILA de COLUMNAS:
    c1, c2, c3, c4= st.columns(4)

    #.................................................................#
    with c1:
        st.markdown('###### :open_file_folder: ARCHIVO DE RETENCIONES:')                    # Encabezado + SÍMBOLO CARPETA.
        with st.expander(':blue[**Cargar excel con la remesa de Retenciones**]'):           # BOTÓN QUE SE ABRE.
            ARCHIVO_EXCEL_RETENCIONES = st.file_uploader(label='Reten_Banco', type=["xlsx", "xls"], label_visibility='collapsed')         # SUBIR UN ARCHIVO.
    #.................................................................#
    with c2:
        st.markdown('###### :calendar: FECHA:', help=':blue[**dd/mm/yyyy**] ')      # TÍTULO + SÍMBOLO CALENDARIO.
        # Obtener la fecha del DÍA 28 del MES ANTERIOR al actual:
        Fecha_defecto= datetime.now() - timedelta(days=datetime.now().day)          # ÚLTIMO DÍA MES ANTERIOR (Fecha Actual - Día Actual de Este Mes= Último Día Mes Anterior).
        Fecha_defecto= Fecha_defecto.replace(day=28)                                # REEMPLAZAR POR EL DÍA 28.
        Fecha= st.date_input(label=":blue[**Fecha-Reten**]", value=Fecha_defecto, format="DD/MM/YYYY", label_visibility='collapsed') # ENTRADA DE FECHA.
    #.................................................................#
    with c3:
        st.markdown('###### :page_with_curl: Nº DOCUMENTO:', help=':blue[**Ejemplo:**] BS2324-0001')    # TÍTULO + SÍMBOLO HOJA.
        Num_Documento= st.text_input(label='Nº Doc-Reten.', label_visibility='collapsed')               # ENTRADA DE TEXTO.
    #.................................................................#
    with c4:
        st.markdown('###### :lower_left_ballpoint_pen: TRIMESTRE (DESCRIPCIÓN):', help=':blue[**Ejemplo:**] 2T 2024')  # TÍTULO + SÍMBOLO BOLSA DINERO.
        TRIMESTRE= st.text_input(label='Mes-Reten', label_visibility='collapsed')                                      # ENTRADA DE TEXTO.
    st.divider()                                                                                                       # LÍNEA HORIZONTAL.
    #========================================================================================================================================================================================#

    ## F.3.) BOTÓN de EJECUCIÓN:                                                             ## ¡¡FUNCIÓN!! ##
    if st.button(":blue[**GENERAR ASIENTOS CONTABLES**]"):    # De color AZUL (:blue[]) y en NEGRITA(** **).
        if ARCHIVO_EXCEL_RETENCIONES is not None:
            try:
                with st.spinner('Cargando...'):      ### CARGANDO... ###
                    # Llamar a la función:
                    df_FINAL, Importe_Total_Linea_BANCO_VISUALIZACION, Importe_Total_Trabajadores_VISUALIZACION, Importe_Total_Colaboradores_VISUALIZACION, Importe_Total_Profesionales_VISUALIZACION, Num_Retenc_Trabajadores, Num_Retenc_Colaboradores, Num_Retenc_Profesionales, Reten_Importe_0_Trabajadores, Reten_Importe_0_Colaboradores, Reten_Importe_0_Profesionales= PAGO_RETENCIONES_UCAV(ARCHIVO_EXCEL_RETENCIONES, Fecha, Num_Documento, TRIMESTRE)
                    #··································································#

        ## F.4.) VISUALIZAR Y GUARDAR EL RESULTADO:
                    Ver_df_BusinessCentral= df_FINAL[['Fecha registro','Tipo documento','Nº documento','Tipo mov.',           # SÓLO COLUMNAS IMPORTANTES #
                                                      'Nº cuenta','Descripción','Importe (DL)','Tipo contrapartida','Cta. contrapartida', 'Empleados Código']].copy() # a) COPIA para NO Modificar el original.
                    Ver_df_BusinessCentral['Empleados Código']= Ver_df_BusinessCentral['Empleados Código'].astype(str)  # b) Pasar a TIPO STRING (Para visualizar los Nº como String [Sin ","]).
                    Ver_df_BusinessCentral= Ver_df_BusinessCentral.reset_index(drop=True)  # c) RESETEAR el ÍNDICE (y eliminar el anterior).
                    Ver_df_BusinessCentral.index= Ver_df_BusinessCentral.index+1           # d) Empezar el ÍNDICE desde el 1.

                    # e) 2 COLUMNAS-> IMPORTE_TOTAL y Si se han conseguido las FILAS correctas ó no. (El mismo Nº de Filas que la Remesa del Banco).
                    cl1, cl2, cl3, cl4= st.columns(4)
                    with cl1:
                        st.markdown(f"#### :blue[Importe Total:] {Importe_Total_Linea_BANCO_VISUALIZACION}") # IMPORTE TOTAL DE LA REMESA "BC".
                    #...........................................................................................#
                    with cl2:
                        if len(Reten_Importe_0_Trabajadores)!= 0:               # SI HAY ALGÚN IMPORTE=0... #
                            Trabaj_Importe0= f':blue[ **- Nº Retenciones con Importe 0:**] :red[**{len(Reten_Importe_0_Trabajadores)}** (*Tenga en cuneta que dichos casos han sido eliminados, por lo que tendrá diferente número de retenciones.*)]'
                        else:
                            Trabaj_Importe0= f':blue[ **- Nº Retenciones con Importe 0:**] :red[**{len(Reten_Importe_0_Trabajadores)}**]'
                        
                                        #Trabajadores#    #Importe Total#    #Nº Retenciones#    #IMPORTE=0#
                        st.success(f'''
                                   **TRABAJADORES:**                                                           

                                   :blue[ **- Importe:**] :red[**{Importe_Total_Trabajadores_VISUALIZACION}**]

                                   :blue[ **- Nº Retenciones:**] :red[**{Num_Retenc_Trabajadores}**]

                                   {Trabaj_Importe0}
                                   ''')
                    #...........................................................................................#
                    with cl3:
                        if len(Reten_Importe_0_Colaboradores)!= 0:               # SI HAY ALGÚN IMPORTE=0... #
                            Colab_Importe0= f':blue[ **- Nº Retenciones con Importe 0:**] :red[**{len(Reten_Importe_0_Colaboradores)}** (*Tenga en cuneta que dichos casos han sido eliminados, por lo que tendrá diferente número de retenciones.*)]'
                        else:
                            Colab_Importe0= f':blue[ **- Nº Retenciones con Importe 0:**] :red[**{len(Reten_Importe_0_Colaboradores)}**]'
                        
                                        #Colaboradores#    #Importe Total#    #Nº Retenciones#    #IMPORTE=0#
                        st.success(f'''
                                   **COLABORADORES:**                                                           

                                   :blue[ **- Importe:**] :red[**{Importe_Total_Colaboradores_VISUALIZACION}**]

                                   :blue[ **- Nº Retenciones:**] :red[**{Num_Retenc_Colaboradores}**]

                                   {Colab_Importe0}
                                   ''')
                    #...........................................................................................#
                    with cl4:
                        if len(Reten_Importe_0_Profesionales)!= 0:               # SI HAY ALGÚN IMPORTE=0... #
                            Profesi_Importe0= f':blue[ **- Nº Retenciones con Importe 0:**] :red[**{len(Reten_Importe_0_Profesionales)}** (*Tenga en cuneta que dichos casos han sido eliminados, por lo que tendrá diferente número de retenciones.*)]'
                        else:
                            Profesi_Importe0= f':blue[ **- Nº Retenciones con Importe 0:**] :red[**{len(Reten_Importe_0_Profesionales)}**]'
                        
                                        #Profesionales#    #Importe Total#    #Nº Retenciones#    #IMPORTE=0#
                        st.success(f'''
                                   **PROFESIONALES:**                                                           

                                   :blue[ **- Importe:**] :red[**{Importe_Total_Profesionales_VISUALIZACION}**]

                                   :blue[ **- Nº Retenciones:**] :red[**{Num_Retenc_Profesionales}**]

                                   {Profesi_Importe0}
                                   ''')
                    #...........................................................................................#
                    st.write(''); st.write('') # LÍNEAS en BLANCO.  

                    # f) MOSTRAR el DF_RESULTADO:
                    st.write(''); st.write('') # LÍNEAS en BLANCO.  
                    st.subheader('📍 ARCHIVO BUSINESS CENTRAL:')
                    st.dataframe(Ver_df_BusinessCentral)

                    ### g) DESCARGAR EL RESULTADO:
                    Excel_buffer= io.BytesIO()                                              # Almacén de DATOS BINARIOS.
                    with pd.ExcelWriter(Excel_buffer, engine='xlsxwriter') as Excel_writer: # Cualquier cosa que se ESCRIBA dentro de esto-> Irá al BUFFER (Almacén) BINARIO.
                        df_FINAL.to_excel(Excel_writer, index=False, sheet_name='RETENCIONES')       # Escribimos como EXCEL el DATAFRAME del resultado.

                    # Obtener el CONTENIDO BINARIO del archivo Excel:
                    Excel_Binario= Excel_buffer.getvalue()                                  # Conseguir el CONTENIDO del ARCHIVO anterior BINARIO (El del Buffer).

                    # BOTÓN de DOWNLOAD!!
                    st.download_button(label=':green[**Descargar Pago de Retenciones**] :inbox_tray:', # NOMBRE del BOTÓN. (Verde y Negrita + Emoji).
                                       data=Excel_Binario,                                             # DATOS-> BINARIOS.
                                       file_name=f'PAGO_RETENCIONES_BC_{TRIMESTRE}.xlsx')              # NOMBRE ARCHIVO que se GUARDA.
                #..................................................................................................................................................................#

            except Exception as e:             # Si al intentar ejecutar la FUNCIÓN hay un ERROR...
                st.error(f"Error: {str(e)}")
        else:
            st.warning(' ¡Cargue el archivo correcto con la remesa de Retenciones!', icon="⚠️") # Muestra como WARNING si NO has insertado el ARCHIVO CORRECTO de DATOS.
############################################################################################################################################################################################

## H) CUERPO DE LA PÁGINA WEB-> REMESA PROVEEDORES:
if ELEGIR_OPCION== PROVEEDORES:
    col1, col2, col3 = st.columns([40, 0.5, 59.95])   # COLUMNAS CON DISTINTOS ANCHOS. (En %).

    ## H.1.) IMAGEN CON HIPERVÍNCULO: (En la Columna 1) + TÍTULO PÁGINA WEB (En la Columna 3) + TEXTO EXPLICATIVO:
    with col1:                       # URL HIPERVÍNCULO #      # Se abrirá en una nueva pestaña #    # URL IMAGEN #                                                                     # ANCHO #
        col1 = st.markdown('<a href="https://www.ucavila.es/" target="_blank"><img src="https://raw.githubusercontent.com/Miguelgargor/IMAGENES_APPs/main/UCAV_logo.png" alt="UCAV Logo" width="300"></a>',
                        unsafe_allow_html=True) # Permitir usar HTML #

    with col3:               #h1: Encabezado# #Color#   #Texto#                        #Permitir HTML#
        col3= st.markdown(f'<h1 style="color:#024868;">PAGO DE FACTURAS A PROVEEDORES UCAV</h1>', unsafe_allow_html=True)
        #--------------------------------------------------------------------------------------#
    st.write(''); st.write('') # LÍNEAS en BLANCO.
    # Escritura.
    st.write('Genera el documento con los ***pagos de facturas*** de los diferentes ***Proveedores ó Recibos de Colaboración*** de manera precisa, para tan solo tener que ***copiar y pegar***, facilitando su registro en Business Central.')
    st.write('Primero elige las opciones necesarias a continuación. Después, sólamente tienes que pulsar en *"**GENERAR ASIENTOS CONTABLES**"*.')
    st.write(''); st.write('') # LÍNEAS en BLANCO.
    #========================================================================================================================================================================================#

    ## H.2.) OPCIONES (INPUTS):
    st.divider()
    st.markdown('##### :red[OPCIONES]')    # Título en rojo.
    # 2 FILAS de COLUMNAS:
    c1, c2, c3, c4= st.columns(4)

    #.................................................................#
    with c1:
        st.markdown('###### :open_file_folder: LISTA DE PROVEEDORES:')              # Encabezado + SÍMBOLO CARPETA.
        with st.expander(':blue[**Cargar excel con la Lista de Proveedores**]'):    # BOTÓN QUE SE ABRE.
            LISTA_PROVEEDORES = st.file_uploader(label='Lista_Proveedores', type=["xlsx", "xls"], label_visibility='collapsed')        # SUBIR UN ARCHIVO.
    #.................................................................#
    with c2:
        st.markdown('###### :open_file_folder: REMESA NÓMINAS BANCO:')             # Encabezado + SÍMBOLO CARPETA.
        with st.expander(':blue[**Cargar excel con la Remesa de Proveedores**]'):  # BOTÓN QUE SE ABRE.
            EXCEL_REMESA_PROVEEDORES = st.file_uploader(label='Remesa_Banco_Prov', type=["xlsx", "xls"], label_visibility='collapsed')  # SUBIR UN ARCHIVO.
    #.................................................................#
    with c3:
        st.markdown('###### :calendar: FECHA DE PAGO:', help=':blue[**dd/mm/yyyy**] ')                           # TÍTULO + SÍMBOLO CALENDARIO.
        # Obtener la fecha del DÍA 28 del MES ANTERIOR al actual:
        Fecha_defecto= datetime.now() - timedelta(days=datetime.now().day)     # ÚLTIMO DÍA MES ANTERIOR (Fecha Actual - Día Actual de Este Mes= Último Día Mes Anterior).
        Fecha_defecto= Fecha_defecto.replace(day=28)                           # REEMPLAZAR POR EL DÍA 28.
        Fecha= st.date_input(label="Fecha de Pago", value=Fecha_defecto, format="DD/MM/YYYY", label_visibility='collapsed') # ENTRADA DE FECHA.
    #.................................................................#
    with c4:
        st.markdown('###### :page_with_curl: Nº DOCUMENTO:', help=':blue[**Ejemplo:**] BS2324-0001') # TÍTULO + SÍMBOLO HOJA.
        Num_Documento= st.text_input(label='Nº Doc. Prov', label_visibility='collapsed')             # ENTRADA DE TEXTO.
    st.divider()                                                                                     # LÍNEA HORIZONTAL.
    #========================================================================================================================================================================================#

    ## H.3.) BOTÓN de EJECUCIÓN:                                                             ## ¡¡FUNCIÓN!! ##
    if st.button(":blue[**GENERAR ASIENTOS CONTABLES**]"):    # De color AZUL (:blue[]) y en NEGRITA(** **).
        if LISTA_PROVEEDORES is not None and EXCEL_REMESA_PROVEEDORES is not None:
            try:
                with st.spinner('Cargando...'):      ### CARGANDO... ###
                    # Llamar a la función:
                    df_FINAL, Códigos_FALTANTES, num_Filas_BANCO, num_Filas_UNION= PAGO_REMESA_PROVEEDORES(LISTA_PROVEEDORES, EXCEL_REMESA_PROVEEDORES, Fecha, Num_Documento)
                    #··································································#

        ## H.4.) VISUALIZAR Y GUARDAR EL RESULTADO:
                    Ver_df_BusinessCentral= df_FINAL.copy()                               # a) COPIA para NO Modificar el original.
                    Ver_df_BusinessCentral= Ver_df_BusinessCentral.reset_index(drop=True) # b) RESETEAR el ÍNDICE (y eliminar el anterior).
                    Ver_df_BusinessCentral.index= Ver_df_BusinessCentral.index+1          # c) Empezar el ÍNDICE desde el 1.

                    # d) FORMATO DE FECHA ¡EN STREAMLIT!:
                    Ver_df_BusinessCentral['Fecha registro']= Ver_df_BusinessCentral['Fecha registro']

                    # e) REPRESENTAR LOS NÚMERO DE PROVEEDOR COMO STRINGS Y SUSTITUIR "<NA>" POR "":
                    Ver_df_BusinessCentral['Cta. contrapartida'] = Ver_df_BusinessCentral['Cta. contrapartida'].astype(str).replace('[,.]', '', regex=True).replace('<NA>','')

                    # f) CAMBIOS EN LA "," (Decimales) Y EL "." (Miles) DEL "IMPORTE": [.->_ // ,->. // _->,]:
                    Ver_df_BusinessCentral['Importe (DL)'] = Ver_df_BusinessCentral['Importe (DL)'].str.replace(',', '.').astype('float').apply(lambda x: '{:,.2f}'.format(x).replace('.', '_').replace(',', '.').replace('_', ','))

                    # g) 2 COLUMNAS-> IMPORTE_TOTAL y Si se han conseguido las FILAS correctas ó no. (El mismo Nº de Filas que la Remesa del Banco).
                    cl1, cl2= st.columns(2)
                    with cl1:
                        st.markdown(f"#### :blue[Importe Total:] {df_FINAL['Importe (DL)'].replace(',','.',regex=True).astype('float').sum():,.2f} €".replace('.', '_').replace(',', '.').replace('_', ',')) # IMPORTE TOTAL DE LA REMESA "BC" (Con cambios necesarios: . y , // Y tipo FLOAT).

                    with cl2:
                        if num_Filas_BANCO==num_Filas_UNION:                               # COMPARACIÓN Nº FILAS BANCO vs. Nº FILAS UNIÓN.
                            st.success(' :blue[**Número de pagos correcto.** (No hay duplicados).]', icon="✅") # MENSAJE de ÉXITO.
                        else:
                            st.warning(f':red[***¡NÚMERO DE PAGOS INCORRECTO!***] (El Banco indica que en esta remesa hay :red[**{num_Filas_BANCO}**] pagos; y se han obtenido :red[**{num_Filas_UNION}**]. **¡Revisar si hay DUPLICADOS (con diferente Nº Proveedor) en la "Lista de Proveedores"!**).', icon="⚠️")
                    st.write(''); st.write('') # LÍNEAS en BLANCO.  

                    #...........................................................................................................................................#
                    ## !! VISUALIZAR los CASOS_SIN Nº PROVEEDOR:
                    Ver_Códigos_FALTANTES= Códigos_FALTANTES.copy()                     # a!) COPIA para NO Modificar el original.
                    Ver_Códigos_FALTANTES= Ver_Códigos_FALTANTES.reset_index(drop=True) # b!) RESETEAR el ÍNDICE (y eliminar el anterior).
                    Ver_Códigos_FALTANTES.index= Ver_Códigos_FALTANTES.index+1          # c!) Empezar el ÍNDICE desde el 1.

                    # d!) REPRESENTAR LOS NÚMERO DE EMPLEADO COMO STRINGS Y SUSTITUIR "<NA>" POR "":
                    Ver_Códigos_FALTANTES['Nº'] = Ver_Códigos_FALTANTES['Nº'].astype(str).replace('<NA>','')

                    # e!) CAMBIOS EN LA "," (Decimales) Y EL "." (Miles) DEL "IMPORTE": [.->_ // ,->. // _->,]:
                    Ver_Códigos_FALTANTES['Importe'] = Ver_Códigos_FALTANTES['Importe'].str.replace(',', '.').astype('float').apply(lambda x: '{:,.2f}'.format(x).replace('.', '_').replace(',', '.').replace('_', ','))




                    # f!) MOSTRAR los CASOS_SIN Nº PROVEEDOR (En caso de que los haya [df>0]):
                    if len(Códigos_FALTANTES)>0:  # Si hay algún caso que no se encuentre el Nº Proveedor... ("CÓDIO PROVEEDOR"= NAN):
                        st.warning(f' :red[**NO SE HAN CONSEGUIDO LOS**] :green[**{len(Códigos_FALTANTES)}**] :red[**Nº DE PROVEEDORES SIGUIENTES:** *(Comprobar los nombres del proveedor)*:]', icon='⚠️') # WARNING.
                        st.dataframe(Ver_Códigos_FALTANTES)                                                 # MOSTRAR CASOS SIN Nº PROVEEDOR.
                    #...........................................................................................................................................#

                    # g) MOSTRAR el DF_RESULTADO:
                    st.write(''); st.write('') # LÍNEAS en BLANCO.  
                    st.subheader('📍 ARCHIVO BUSINESS CENTRAL:')
                    st.dataframe(Ver_df_BusinessCentral)

                    # h) DESCARGAR EL RESULTADO:
                    Excel_buffer= io.BytesIO()                                              # Almacén de DATOS BINARIOS.
                    with pd.ExcelWriter(Excel_buffer, engine='xlsxwriter') as Excel_writer: # Cualquier cosa que se ESCRIBA dentro de esto-> Irá al BUFFER (Almacén) BINARIO.
                        df_FINAL.to_excel(Excel_writer, index=False, sheet_name='PAGO PROVEEDORES')    # Escribimos como EXCEL el DATAFRAME del resultado.

                    # Obtener el CONTENIDO BINARIO del archivo Excel:
                    Excel_Binario= Excel_buffer.getvalue()                                  # Conseguir el CONTENIDO del ARCHIVO anterior BINARIO (El del Buffer).

                    # BOTÓN de DOWNLOAD!!
                    st.download_button(label=':green[**Descargar Pagos a Proveedores**] :inbox_tray:',    # NOMBRE del BOTÓN. (Verde y Negrita + Emoji).
                                       data=Excel_Binario,                                                # DATOS-> BINARIOS.
                                       file_name=f'PAGO_REMESA_PROVEEDORES_BC.xlsx')                      # NOMBRE ARCHIVO que se GUARDA.
                #..................................................................................................................................................................#

            except Exception as e:             # Si al intentar ejecutar la FUNCIÓN hay un ERROR...
                st.error(f"Error: {str(e)}")
        else:
            st.warning(' ¡Cargue los archivos correctos con la lista de proveedores y la remesa del banco!', icon="⚠️") # Muestra como WARNING si NO has insertado los ARCHIVOS CORRECTOS de DATOS.
############################################################################################################################################################################################
