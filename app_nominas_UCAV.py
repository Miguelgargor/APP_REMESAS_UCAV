import pandas as pd                        #  Tratamiento de Datos.
import numpy as np                         # Tratamiento de Datos.
import streamlit as st                     # Página Web.
from datetime import datetime, timedelta   # Fechas.

def PAGO_NOMINAS_UCAV(EXCEL_CODIGO_EMPLEADOS, REMESA_NOMINA, Fecha, Num_Documento, Mes_Pago):

## A) TRATAMIENTO DEL EXCEL DE EMPLEADOS:
    ## A.0º) Lectura de los datos CÓDIGO EMPLEADOS:
    df_codigo_empleados= pd.read_excel(EXCEL_CODIGO_EMPLEADOS)
    df_codigo_empleados= df_codigo_empleados.applymap(lambda s: s.upper() if type(s)==str else s)  # Conversión de todos los campos a MAYÚSCULAS.
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    for columna in ['Nombre', 'Primer apellido', 'Segundo apellido']:
        ## A.1º) Eliminación de las tildes y cambio de Ñ por N:
        df_codigo_empleados[columna].replace({'Á':'A', 'É':'E', 'Í':'I', 'Ó':'O', 'Ú':'U', 'Ñ':'N'}, regex=True, inplace=True)
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        ## A.2º) Eliminación de espacios innecesarios al principio y al final de cada cadena de texto:
        df_codigo_empleados[columna]= df_codigo_empleados[columna].str.strip()
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        ## A.3º) Sustitución de "M." y "Mª" por MARIA:
        df_codigo_empleados[columna].replace({'Mª':'MARIA', 'M[.]':'MARIA '}, regex=True, inplace=True)
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        ## A.4º) Eliminación de "." y "-":
        df_codigo_empleados[columna]= df_codigo_empleados[columna].str.replace('[.]','', regex=True)
        df_codigo_empleados[columna]= df_codigo_empleados[columna].str.replace('-',' ', regex=True)
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
        ## A.5.1º) Eliminación de los "determinantes" (palabras con un espacio antes y después) y sustituirlos por un espacio en blanco (para evitar juntar Nombre y Apellido):
        determinantes= [' EL ',' LA ',' LO ',' LE ',' LES ',' LOS ',' LAS ',' DE ',' DEL ',' DA ',' DO ',' DI ',' UN ',' UNA ',' UNOS ',' UNAS ',' MAC ',' MC ',' VAN ',' VON ',' Y ', ' E ',' THE ','THE ',' OF ']
        for deter in determinantes:
            df_codigo_empleados[columna].replace({deter:' '}, regex=True, inplace=True)

        ## A.5.2º) Eliminación de los "determinantes" del PRINCIPIO (palabras con un espacio después) y sustituirlos por una cadena de texto vacía (para evitar espacios innecesarios):
        determinantes2= ['EL ','LA ','LO ','LE ','LES ','LOS ','LAS ','DE ','DEL ','DA ','DO ','DI ','UN ','UNA ','UNOS ','UNAS ','MAC ','MC ','VAN ','VON ','Y ', 'E ','THE ','OF ']
        for deter in determinantes2:
            df_codigo_empleados[columna].replace({'^' + deter:''}, regex=True, inplace=True)
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
    df_NOMINA.sort_values(by='Descripcion', ascending=True, inplace=True)                                                                # ORDENAR los VALORES según la "Descripción".
    df_NOMINA.reset_index(drop=True, inplace=True)                                                                                       # RESETEO del ÍNDICE.
#==========================================================================================================================================================================================#

## E) VISUALIZAR SÓLO LOS CASOS EN LOS QUE NO SE HA CONSEGUIDO UNIR EL "CODIGO EMPLEADO":
    Códigos_FALTANTES= df_resultado[df_resultado['Nº'].isna()].copy()                # QUEDARSE CON LOS QUE NO COINCIDEN CON EL CÓDIGO.
    Códigos_FALTANTES.sort_values(by='Beneficiario', ascending=True, inplace=True)   # ORDENAR los VALORES según la "Descripción".
    Códigos_FALTANTES.reset_index(drop=True, inplace=True)                           # RESETEO del ÍNDICE.
#==========================================================================================================================================================================================#

## F) COMPARACIÓN Nº FILAS BANCO vs. Nº FILAS UNIÓN:
    num_Filas_BANCO= len(df_banco_nomina)
    num_Filas_UNION= len(df_resultado)

    return df_NOMINA, Códigos_FALTANTES, num_Filas_BANCO, num_Filas_UNION
############################################################################################################################################################################################

## A) CONFIGURACIÓN GENERAL DE LA PÁGINA WEB:
st.set_page_config(page_title="PAGO NOMINAS UCAV",                                                                        # Nombre en el Navegador.
                   page_icon="https://raw.githubusercontent.com/Miguelgargor/IMAGENES_APPs/main/logoUcav_navegador.png",  # Icono del Navegador.
                   layout="wide",                                                                                         # Mostrarlo en toda la pantalla.
                   initial_sidebar_state="expanded")                                                                      # Mostrar la barra lateral inicialmente.
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

## B) BARRA LATERAL: (Indicar los parámetros de la Función):
with st.sidebar:                              # Barra Lateral.
    st.title('⚙️ :red[OPCIONES]')    # Título en rojo y con un círculo rojo a la izquierda.
    #.................................................................#
    st.subheader('1) LISTA DE EMPLEADOS: :open_file_folder:')              # Encabezado + SÍMBOLO CARPETA.
    with st.expander(':blue[**Cargar excel con la Lista de Empleados**]'): # BOTÓN QUE SE ABRE.
        LISTA_EMPLEADOS = st.file_uploader(label='Lista_Empleados', type=["xlsx", "xls"], label_visibility='collapsed')        # SUBIR UN ARCHIVO.
    #.................................................................#
    st.subheader('2) REMESA NÓMINAS BANCO: :open_file_folder:')            # Encabezado + SÍMBOLO CARPETA.
    with st.expander(':blue[**Cargar excel con la Remesa de Nóminas**]'):  # BOTÓN QUE SE ABRE.
        REMESA_NOMINAS_BANCO = st.file_uploader(label='Remesa_Banco', type=["xlsx", "xls"], label_visibility='collapsed')      # SUBIR UN ARCHIVO.
    st.divider()                                                           # LÍNEA HORIZONTAL.
    #.................................................................#
    st.subheader('3) FECHA DE PAGO: :calendar:')                           # TÍTULO + SÍMBOLO CALENDARIO.
    # Obtener la fecha del DÍA 28 del MES ANTERIOR al actual:
    Fecha_defecto= datetime.now() - timedelta(days=datetime.now().day)     # ÚLTIMO DÍA MES ANTERIOR (Fecha Actual - Día Actual de Este Mes= Último Día Mes Anterior).
    Fecha_defecto= Fecha_defecto.replace(day=28)                           # REEMPLAZAR POR EL DÍA 28.
    Fecha= st.date_input(label=":blue[**Fecha de Pago**]", value=Fecha_defecto, format="DD/MM/YYYY", label_visibility='collapsed') # ENTRADA DE FECHA.
    #.................................................................#
    st.subheader('4) Nº DOCUMENTO: :page_with_curl:', help=':blue[**Ejemplo:**] BS2324-0001') # TÍTULO + SÍMBOLO HOJA.
    Num_Documento= st.text_input(label='Nº Doc.', label_visibility='collapsed')                # ENTRADA DE TEXTO.
    #.................................................................#
    st.subheader('5) MES PAGO: 	:moneybag:', help=':blue[**Ejemplo:**] ENE24')                 # TÍTULO + SÍMBOLO BOLSA DINERO.
    Mes_Pago= st.text_input(label='Mes_Pago', label_visibility='collapsed')                    # ENTRADA DE TEXTO.
    st.divider()                                                                               # LÍNEA HORIZONTAL.
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

## C) CUERPO DE LA PÁGINA WEB:
col1, col2, col3 = st.columns([40, 0.5, 59.95])   # COLUMNAS CON DISTINTOS ANCHOS. (En %).

## C.1.) IMAGEN CON HIPERVÍNCULO: (En la Columna 1) + TÍTULO PÁGINA WEB (En la Columna 3):
with col1:                       # URL HIPERVÍNCULO #      # Se abrirá en una nueva pestaña #    # URL IMAGEN #                                                                     # ANCHO #
    col1 = st.markdown('<a href="https://www.ucavila.es/" target="_blank"><img src="https://raw.githubusercontent.com/Miguelgargor/IMAGENES_APPs/main/UCAV_logo.png" alt="UCAV Logo" width="300"></a>',
                       unsafe_allow_html=True) # Permitir usar HTML #

with col3:
    col3= st.header('PAGO DE NÓMINAS UCAV')

    #--------------------------------------------------------------------------------------#
st.write(''); st.write('') # LÍNEAS en BLANCO.
# Escritura.
st.write('Esta web te permitirá crear el documento de nóminas correcto para poder importarlo en Business Central para su registro.')
st.write('Primero elige las opciones necesarias en la barra lateral. Después, sólamente tienes que pulsar en "**NÓMINAS**".')
st.write(''); st.write('') # LÍNEAS en BLANCO.
    #--------------------------------------------------------------------------------------#

## C.2.) BOTÓN de EJECUCIÓN:                                                             ## ¡¡FUNCIÓN!! ##
if st.button(":blue[**NÓMINAS**]"):    # De color AZUL (:blue[]) y en NEGRITA(** **).
    if LISTA_EMPLEADOS is not None and REMESA_NOMINAS_BANCO is not None:
        try:
            with st.spinner('Cargando...'):      ### CARGANDO... ###
                # Llamar a la función:
                df_BusinessCentral, Códigos_FALTANTES, num_Filas_BANCO, num_Filas_UNION= PAGO_NOMINAS_UCAV(LISTA_EMPLEADOS, REMESA_NOMINAS_BANCO, Fecha, Num_Documento, Mes_Pago)
                #··································································#

     ##C.3.) VISUALIZAR Y GUARDAR EL RESULTADO:
                Ver_df_BusinessCentral= df_BusinessCentral.copy()                       # a) COPIA para NO Modificar el original.
                Ver_df_BusinessCentral.reset_index(drop=True, inplace=True)             # b) RESETEAR el ÍNDICE (y eliminar el anterior).
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
                Ver_Códigos_FALTANTES= Códigos_FALTANTES.copy()               # a!) COPIA para NO Modificar el original.
                Ver_Códigos_FALTANTES.reset_index(drop=True, inplace=True)    # b!) RESETEAR el ÍNDICE (y eliminar el anterior).
                Ver_Códigos_FALTANTES.index= Ver_Códigos_FALTANTES.index+1    # c!) Empezar el ÍNDICE desde el 1.

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
                st.header('📍 ARCHIVO PARA BUSINESS CENTRAL:')
                st.dataframe(Ver_df_BusinessCentral)

                ### i) DESCARGAR EL RESULTADO:
                data_csv= df_BusinessCentral.to_csv(sep=';',                           # SEPARADOR (En Columnas).
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
#####################################################################################################################################################################
