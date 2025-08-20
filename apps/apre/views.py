import os
import google.generativeai as genai
from django.shortcuts import render
from django.db import connection
from datetime import datetime, date, timedelta
import calendar
from dateutil.relativedelta import relativedelta #type: ignore
from .forms import ApreForm
from django.conf import settings
import oracledb
import logging
import pandas as pd
from django.http import HttpResponse, JsonResponse
import io
import json

logger = logging.getLogger(__name__)

model = genai.GenerativeModel("gemini-1.5-flash")

def _get_rename_map(selected_apre_type):
    """Devuelve el diccionario de renombrado de columnas para el tipo de APRE."""
    if selected_apre_type in ['apre_compensados', 'apre_sincompensados']:
        return {
            'PROVINTMESANT': '% Provis / Interes mes ant',
            'PROVINTMES': '% Provis / Interes corte',
            'SUCURSAL': 'Sucursal',
            'PYG_CORTE': 'P y G Final CON compensados',
            'COMPENNETO': 'Compensado $ Neto',
            'COMPENGASTOS': 'Compensado $ gastos',
            'COMPENINGRESOS': 'Compensado $ ingresos',
            'COMPENFINANCIEROS': 'Compensado $ financieros',
            'TOTALPYG': 'Total P y G contable',
            'TOTALGASYCOS': 'Total gastos y costos',
            'OTROSGASYCOS': 'Otras gastos y costos',
            'GASTOPROV': 'Gasto provisión',
            'TOTALING': 'Total ingresos',
            'INGREPRESTAMOS': 'Ingresos por préstamos',
            'OTROSINGRE': 'Otros ingresos',
            'COSTODEPO': 'Costo de po (Depósitos)',
            'GASOPEIMPU': 'Gasto Operativo + impuestos',
            'DEPOSITOS': 'Depósitos',
            'DEPOANOCOR': 'Depósitos año corrido',
            'APORTES': 'Aportes',
            'APORANOCOR': 'Aportes año corrido',
            'CARTERA': 'Cartera',
            'CARANOCOR': 'Cartera año corrido',
            'ASOCIADOS': 'Asociados',
            'ASOANOCOR': 'Asociados año corrido',
            'CARTERAVENCIDA': 'Cartera vencida',
            'CARVENANOCOR': 'Cartera vencida año corrido',
            'CARIMPROANCOR': 'Cartera improductiva año corrido',
            'TASAVENCID': '% Tasa Vencida',
            'TASAIMPROD': '% Tasa Improductiva',
            'TASAMARG': '% Tasa Marginal',
            'TASACART': '% Tasa Cartera',
            'TASADEPO': '% Tasa Depósitos',
        }
    elif selected_apre_type == 'apre_basico':
        return {
            'PROVINTMESANT': '% Provis / Interes mes ant',
            'PROVINTMES': '% Provis / Interes corte',
            'SUCURSAL': 'Sucursal',
            'CARTERA': 'Cartera',
            'CARVARMES': 'Cartera Var Mes',
            'CARANOCOR': 'Cartera Año Corrido',
            'CALIDAD': 'Calidad',
            'CALVARMES': 'Calidad Var Mes',
            'CARANOMES': 'Cartera Año Mes',
            'CARTERAIMPRO': 'Cartera Improductiva',
            'CARIMPROMES': 'Cartera Improductiva Mes',
            'CARIMPROANCOR': 'Cartera Improductiva Año Corrido',
            'APORTES': 'Aportes',
            'APORVARMES': 'Aportes Var Mes',
            'APORANOCOR': 'Aportes Año Corrido',
            'DEPOSITOS': 'Depósitos',
            'DEPOVARMES': 'Depósitos Var Mes',
            'DEPOANOCOR': 'Depósitos Año Corrido',
            'ASOCIADOS': 'Asociados',
            'ASOVARMES': 'Asociados Var Mes',
            'ASOANOCOR': 'Asociados Año Corrido',
            'TASAMARG': 'Tasa Marginal',
            'MARGANO': 'Margen Año',
            'MARGVARMES': 'Margen Var Mes',
            'TASADEPO': 'Tasa Depósitos',
            'TASADEPOMES': 'Tasa Depósitos Mes',
            'TASADEPOANO': 'Tasa Depósitos Año',
            'TASACART': 'Tasa Cartera',
            'TASACARTMES': 'Tasa Cartera Mes',
            'TASACARTANO': 'Tasa Cartera Año',
            'EXCEDENTES': 'Excedentes',
            'PYG_CORTE': 'P y G Corte',
        }
    elif selected_apre_type == 'apre_diferencia':
        return {
            'PROVINTMESANT': '% Provis / Interes mes ant',
            'INGREPRESTAMOSANT': 'Ingresos por préstamos Ant',
            'OTROSINGREANT': 'Otros Ingresos Ant',
            'GASTOPROVANT': 'Gasto Provisión Ant',
            'OTROSGASYCOSANT': 'Otros Gastos y Costos Ant',
            'EXCEDENTESANTESCOMANT': 'Excedentes Antes Comp. Ant',
            'COMPENINGANT': 'Compensado Ingresos Ant',
            'COMPENGASANT': 'Compensado Gastos Ant',
            'EXCEDENTEFINALANT': 'Excedente Final Ant',
            'PROVINTMES': '% Provis / Interes mes',
            'INGREPRESTAMOS': 'Ingresos por préstamos',
            'OTROSINGRE': 'Otros Ingresos',
            'GASTOPROV': 'Gasto Provisión',
            'OTROSGASYCOS': 'Otros Gastos y Costos',
            'EXCEDENTESANTESCOM': 'Excedentes Antes Comp.',
            'COMPENING': 'Compensado Ingresos',
            'COMPENGAS': 'Compensado Gastos',
            'EXCEDENTEFINAL': 'Excedente Final',
        }
    return {}

def _rename_data(data, rename_map):
    """Renombra las claves de una lista de diccionarios."""
    if not rename_map or not data:
        return data
    
    renamed_data = []
    for row in data:
        renamed_data.append({rename_map.get(k, k): v for k, v in row.items()})
    return renamed_data

#? ====== FUNCION PARA VER Y OBTENER LOS DATOS DEL APRE CON COMPENSADOS ==========#
def obtener_datos_apre(request, form):
    """Obtiene los datos desde Oracle usando SP_APRECOMPENSADOS."""
    try:
        periodicidad = form.cleaned_data.get('periodicidad')
        if periodicidad == 'diario':
            today = date.today()
            selected_date = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        else:
            selected_date = form.cleaned_data['fecha']
        logger.info(f"Fecha seleccionada: {selected_date}")
        
        periodo_actual = selected_date.strftime('%Y/%m/%d')
        periodo_anterior = (selected_date.replace(day=1) - timedelta(days=1)).strftime('%Y/%m/%d')
        hace_dos_meses = (selected_date - relativedelta(months=2)).strftime('%Y/%m/%d')
        ano_anterior = (selected_date.replace(month=1, day=1) -timedelta(days=1)).strftime('%Y/%m/%d')
        logger.info(f"Parámetros calculados para SP_APRE CON COMPENSADOS:")
        logger.info(f"  - periodo_actual: {periodo_actual}")
        logger.info(f"  - periodo_anterior: {periodo_anterior}")
        logger.info(f"  - hace_dos_meses: {hace_dos_meses}")
        logger.info(f"  - ano_anterior: {ano_anterior}")

        # Conexión Oracle
        db = settings.DATABASES['oracle']
        dsn = f"{db['HOST']}:{db['PORT']}/{db['NAME']}"

        with oracledb.connect(user=db['USER'], password=db['PASSWORD'], dsn=dsn) as conn:
            with conn.cursor() as cursor:
                ref_cursor_out = cursor.var(oracledb.CURSOR)
                cursor.callproc('SP_APRECOMPENSADOS', [periodo_actual, periodo_anterior, ano_anterior, hace_dos_meses,ref_cursor_out])
                cur = ref_cursor_out.getvalue()

                if cur:
                    cols = [c[0] for c in cur.description]
                    return [dict(zip(cols, row)) for row in cur]

        return []

    except Exception as e:
        logger.error(f"Error en obtener_datos_APRE: {e}", exc_info=True)
        return []

#? ============= AQUI TERMINA EL APRE CON COMPENSADOS ===========


#? ============= VER Y OBTENER DATOS DEL APRE SIN COMPENSADOS ==================#
def obtener_datos_apre_sincom(request, form):
    """
    FUNCION PARA OBTENER LOS DATOS DEL APRE SIN COMPENSADOS
    """
    try:
        periodicidad = form.cleaned_data.get('periodicidad')
        if periodicidad == 'diario':
            today = date.today()
            selected_date = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        else:
            selected_date = form.cleaned_data['fecha']
        logger.info(f"Fecha seleccionada: {selected_date}")

        periodo_actual = selected_date.strftime('%Y/%m/%d')
        periodo_anterior = (selected_date.replace(day=1) - timedelta(days=1)).strftime('%Y/%m/%d')
        hace_dos_meses = (selected_date - relativedelta(months=2)).strftime('%Y/%m/%d')
        ano_anterior = (selected_date.replace(month=1, day=1) - timedelta(days=1)).strftime('%Y/%m/%d')
        logger.info(f"Parámetros calculados para SP_APRE_SINCOMPENSADOS:")
        logger.info(f"  - periodo_actual: {periodo_actual}")
        logger.info(f"  - periodo_anterior: {periodo_anterior}")
        logger.info(f"  - hace_dos_meses: {hace_dos_meses}")
        logger.info(f"  - ano_anterior: {ano_anterior}")

        db = settings.DATABASES['oracle']
        dsn = f"{db['HOST']}:{db['PORT']}/{db['NAME']}"
        
        with oracledb.connect(user=db['USER'], password=db['PASSWORD'], dsn=dsn) as conn:
            with conn.cursor() as cursor:
                ref_cursor_out = cursor.var(oracledb.CURSOR)
                cursor.callproc('SP_APRESINCOMPENSADOS', [periodo_actual, periodo_anterior, ano_anterior, hace_dos_meses, ref_cursor_out])
                cur = ref_cursor_out.getvalue()

                if cur:
                    cols = [c[0] for c in cur.description]
                    return [dict(zip(cols, row)) for row in cur]
        return[]
    
    except Exception as e:
        logger.error(f"Error en obtener_datos_sin_compensados: {e}", exc_info=True)
        return[]
#? ============= AQUI TERMINA EL APRE SIN COMPENSADOS ==================#


#? =========== OBTENER DATOS DEL APRE BASICO PLENO ========================#
def obtener_datos_apre_basico(request, form):
    """
    Obtiene los datos desde Oracle usando SP_APRE
    """
    try:
        periodicidad = form.cleaned_data.get('periodicidad')
        if periodicidad == 'diario':
            today = date.today()
            selected_date = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        else:
            selected_date = form.cleaned_data['fecha']
        logger.info(f"Fecha seleccionada: {selected_date}")

        periodo_actual = selected_date.strftime('%Y/%m/%d')
        periodo_anterior = (selected_date.replace(day=1) - timedelta(days=1)).strftime('%Y/%m/%d')
        hace_dos_meses = (selected_date - relativedelta(months=2)).strftime('%Y/%m/%d')
        ano_anterior = (selected_date.replace(month=1, day=1) -timedelta(days=1)).strftime('%Y/%m/%d')
        logger.info(f"Parámetros calculados para SP_APRE BASICO:")
        logger.info(f"  - periodo_actual: {periodo_actual}")
        logger.info(f"  - periodo_anterior: {periodo_anterior}")
        logger.info(f"  - hace_dos_meses: {hace_dos_meses}")
        logger.info(f"  - ano_anterior: {ano_anterior}")

        db = settings.DATABASES['oracle']
        dsn = f"{db['HOST']}:{db['PORT']}/{db['NAME']}"

        with oracledb.connect(user=db['USER'], password=db['PASSWORD'], dsn=dsn) as conn:
            with conn.cursor() as cursor:
                ref_cursor_out = cursor.var(oracledb.CURSOR)
                cursor.callproc('SP_APRE', [periodo_actual, periodo_anterior, ano_anterior, hace_dos_meses, ref_cursor_out])
                cur = ref_cursor_out.getvalue()

                if cur:
                    cols = [c[0] for c in cur.description]
                    return [dict(zip(cols, row)) for row in cur]
                
        return []
    except Exception as e:
        logger.error(f"Error en Obtener datos Apre_Basico: {e}", exc_info=True)
        return []
#? ================ AQUI TERMINA EL APRE BASICO ======================#


#? ================= OBTENER DATOS MES ANTERIOR VS ACTUAL ====================== #
def obtener_datos_apre_vs(request, form):
    """
    FUNCION PARA VER LOS DATOS SP_APRESOLOMES
    """
    try:
        periodicidad = form.cleaned_data.get('periodicidad')
        if periodicidad == 'diario':
            today = date.today()
            selected_date = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        else:
            selected_date = form.cleaned_data['fecha']
        logger.info(f"Fecha seleccionada: {selected_date}")

        periodo_actual = selected_date.strftime('%Y/%m/%d')
        periodo_anterior = (selected_date.replace(day=1) - timedelta(days=1)).strftime('%Y/%m/%d')
        hace_dos_meses = (selected_date - relativedelta(months=2)).strftime('%Y/%m/%d')
        ano_anterior = (selected_date.replace(month=1, day=1) - timedelta(days=1)).strftime('%Y/%m/%d')
        logger.info(f"Parámetros calculados para SP_APRE_MESANTVSACT:")
        logger.info(f"  - periodo_actual: {periodo_actual}")
        logger.info(f"  - periodo_anterior: {periodo_anterior}")
        logger.info(f"  - hace_dos_meses: {hace_dos_meses}")
        logger.info(f"  - ano_anterior: {ano_anterior}")

        db = settings.DATABASES['oracle']
        dsn = f"{db['HOST']}:{db['PORT']}/{db['NAME']}"

        with oracledb.connect(user=db['USER'], password=db['PASSWORD'], dsn=dsn) as conn:
            with conn.cursor() as cursor:
                ref_cursor_out = cursor.var(oracledb.CURSOR)
                cursor.callproc('SP_APRESOLOMES', [periodo_actual, periodo_anterior, ano_anterior, hace_dos_meses, ref_cursor_out])
                cur = ref_cursor_out.getvalue()

                if cur:
                    cols = [c[0] for c in cur.description]
                    return [dict(zip(cols, row)) for row in cur]
        return[]
    except Exception as e:
        logger.error(f"Error en obtener los datos del mesa anterior vs el actual: {e}", exc_info=True)
        return[]


#? VISTA PRINCIPAL DEL REPORTE APRE
def apre_report_view(request):
    form = ApreForm(request.POST or None)
    datos = []
    selected_apre_type = None

    if request.method == "POST":
        if form.is_valid():
            selected_apre_type = form.cleaned_data['tipo_apre']
            if selected_apre_type == 'apre_compensados':
                datos = obtener_datos_apre(request, form)
            elif selected_apre_type == 'apre_sincompensados':
                datos = obtener_datos_apre_sincom(request, form)
            elif selected_apre_type == 'apre_basico':
                datos = obtener_datos_apre_basico(request, form)
            elif selected_apre_type == 'apre_diferencia':
                datos = obtener_datos_apre_vs(request, form)

            # print("Obtener solo los codigos de sucursal",datos.CODSUCURSAL.unique())
            # Renombrar datos para la vista
            rename_map = _get_rename_map(selected_apre_type)
            datos = _rename_data(datos, rename_map)

    return render(request, 'apre/apre_report.html', {
        "apre_list": datos,
        "form": form,
        "data": datos if datos else 'null',
        "selected_apre_type": selected_apre_type,
    })

def download_apre_excel(request):
    """
    Genera y devuelve un archivo Excel con los datos del reporte APRE.
    """
    logger.info("=== INICIANDO download_apre_excel ===")
    if request.method == 'POST':
        form = ApreForm(request.POST)
        
        if form.is_valid():
            logger.info("Formulario válido, procediendo con la generación del Excel")
            try:
                selected_apre_type = form.cleaned_data['tipo_apre']
                datos_originales = []
                if selected_apre_type == 'apre_compensados':
                    datos_originales = obtener_datos_apre(request, form)
                elif selected_apre_type == 'apre_sincompensados':
                    datos_originales = obtener_datos_apre_sincom(request, form)
                elif selected_apre_type == 'apre_basico':
                    datos_originales = obtener_datos_apre_basico(request, form)
                elif selected_apre_type == 'apre_diferencia':
                    datos_originales = obtener_datos_apre_vs(request, form)

                if not datos_originales:
                    logger.warning("No se encontraron datos para generar el Excel")
                    return HttpResponse("No se encontraron datos para la fecha y tipo seleccionados.", status=404)

                logger.info(f"Creando DataFrame con {len(datos_originales)} registros")
                df = pd.DataFrame(datos_originales)

                # Renombrar columnas
                rename_map = _get_rename_map(selected_apre_type)
                df.rename(columns=rename_map, inplace=True)

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Reporte APRE')
                output.seek(0)

                selected_date = form.cleaned_data['fecha']
                filename = f"reporte_apre_{selected_apre_type}_{selected_date.strftime('%Y%m%d')}.xlsx"

                response = HttpResponse(
                    output,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                logger.info(f"Enviando archivo: {filename}")
                return response

            except Exception as e:
                logger.error(f"Error general en download_apre_excel: {e}", exc_info=True)
                return HttpResponse(f"Ocurrió un error al generar el reporte: {str(e)}", status=500)
        else:
            logger.error(f"Formulario no válido. Errores: {form.errors}")
            return HttpResponse(f"Datos del formulario no válidos: {form.errors}", status=400)
    else:
        logger.error(f"Método no permitido: {request.method}")
        return HttpResponse("Método no permitido. Use POST.", status=405)


def generate_summary_view(request):
    """
    Genera un resumen técnico de los datos del reporte APRE usando IA.
    """
    logger.info("=== INICIANDO generate_summary_view ===")
    
    if request.method == 'POST':
        try:
            if not settings.GEMINI_API_KEY:
                logger.error("GEMINI_API_KEY no está configurada en settings.py")
                return JsonResponse({'error': 'La clave de API de Gemini no está configurada.'}, status=500)
            
            genai.configure(api_key=settings.GEMINI_API_KEY)

            body = json.loads(request.body)
            report_data = body.get('data', [])
            if not report_data:
                return JsonResponse({'error': 'No se proporcionaron datos para el resumen.'}, status=400)

            prompt = f"""Actúa como un analista financiero experto y genera un concepto técnico consolidado del reporte APRE en formato HTML.
            Sé breve y conciso en cada sección.
            El análisis debe estar dividido en las siguientes secciones, usando etiquetas HTML como <h2>, <p> y <ul> para las listas:
            1.  <b>Análisis de Tendencias y Puntos Clave:</b> Utiliza <ul> y <li> para desglosar los 3 hallazgos principales.
            2.  <b>Anomalías e Información Relevante:</b> Destaca cualquier dato inusual o faltante.
            3.  <b>Recomendaciones:</b> Proporciona un listado de máximo 3 acciones a tomar usando <ul> y <li>.
            En todo el texto, usa la etiqueta <b> para resaltar los términos o datos más importantes. Los datos para el análisis son:
            {json.dumps(report_data, indent=2)}
            """
            
            try:
                response = model.generate_content(prompt)
                summary = response.text
            except Exception as gemini_error:
                logger.error(f"Error al llamar a la API de Gemini: {gemini_error}", exc_info=True)
                return JsonResponse({'error': 'Error al generar el resumen con IA.'}, status=500)

            return JsonResponse({'summary': summary})

        except Exception as e:
            logger.error(f"Error en generate_summary_view: {e}", exc_info=True)
            return JsonResponse({'error': 'Ocurrió un error interno.'}, status=500)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)