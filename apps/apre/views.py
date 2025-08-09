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
    print("REQUEST POST:", request.POST.dict())
    print("PERIODICIDAD DEL FORMULARIO:", form['periodicidad'].value())

    datos = []
    selected_apre_type = None

    if request.method == "POST":
        if form.is_valid():
            print("CLEANED DATA:", form.cleaned_data)
            selected_apre_type = form.cleaned_data['tipo_apre']
            if selected_apre_type == 'apre_compensados':
                datos = obtener_datos_apre(request, form)
            elif selected_apre_type == 'apre_sincompensados':
                datos = obtener_datos_apre_sincom(request, form)
            elif selected_apre_type == 'apre_basico':
                datos = obtener_datos_apre_basico(request, form)
                print("Estos son los datos",datos)
            elif selected_apre_type == 'apre_diferencia':
                datos = obtener_datos_apre_vs(request, form)

    return render(request, 'apre/apre_report.html', {
        "apre_list": datos,
        "form": form,
        "data": datos if datos else 'null',
        "selected_apre_type": selected_apre_type, # Pasar el tipo seleccionado al template
    })

def download_apre_excel(request):
    """
    Genera y devuelve un archivo Excel con los datos del reporte APRE.
    """
    logger.info("=== INICIANDO download_apre_excel ===")
    
    form = ApreForm(request.GET or None)
    if form.is_bound and form.is_valid():
        try:
            periodicidad = form.cleaned_data.get('periodicidad')
            if periodicidad == 'diario':
                today = date.today()
                selected_date = today.replace(day=calendar.monthrange(today.year, today.month)[1])
            else:
                selected_date = form.cleaned_data['fecha']
            
            selected_apre_type = form.cleaned_data['tipo_apre']
            logger.info(f"Generando Excel para fecha: {selected_date} y tipo: {selected_apre_type}")

            periodo_actual = selected_date.strftime('%Y/%m/%d')
            periodo_anterior = (selected_date.replace(day=1) - timedelta(days=1)).strftime('%Y/%m/%d')
            hace_dos_meses = (selected_date - relativedelta(months=2)).strftime('%Y/%m/%d')
            ano_anterior = (selected_date.replace(month=1, day=1) - timedelta(days=1)).strftime('%Y/%m/%d')

            db = settings.DATABASES['oracle']
            dsn = f"{db['HOST']}:{db['PORT']}/{db['NAME']}"
            
            data = []
            with oracledb.connect(user=db['USER'], password=db['PASSWORD'], dsn=dsn) as conn:
                logger.info("Conexión Oracle establecida para Excel")
                with conn.cursor() as cursor:
                    ref_cursor = cursor.var(oracledb.CURSOR)
                    if selected_apre_type == 'apre_compensados':
                        cursor.callproc('SP_APRECOMPENSADOS', [
                            periodo_actual, periodo_anterior, ano_anterior, hace_dos_meses, ref_cursor
                        ])
                    elif selected_apre_type == 'apre_sincompensados':
                        cursor.callproc('SP_APRESINCOMPENSADOS', [
                            periodo_actual, periodo_anterior, ano_anterior, hace_dos_meses, ref_cursor
                        ])
                    elif selected_apre_type == 'apre_basico':
                        cursor.callproc('SP_APRE', [
                            periodo_actual, periodo_anterior, ano_anterior, hace_dos_meses, ref_cursor
                        ])
                    elif selected_apre_type == 'apre_diferencia':
                        cursor.callproc('SP_APRESOLOMES', [
                            periodo_actual, periodo_anterior, ano_anterior, hace_dos_meses, ref_cursor
                        ])
                    
                    result_cursor = ref_cursor.getvalue()
                    
                    if result_cursor and result_cursor.description:
                        cols = [c[0] for c in result_cursor.description]
                        rows = result_cursor.fetchall()
                        data = [dict(zip(cols, row)) for row in rows]
                        result_cursor.close()

            if data:
                df = pd.DataFrame(data)
                # Renombrar columnas según el tipo de APRE
                if selected_apre_type == 'apre_compensados' or selected_apre_type == 'apre_sincompensados':
                    df.rename(columns={
                        'PROVINTMESANT': '% Provis / Interes mes ant', 'PROVINTMES': '% Provis / Interes corte',
                        'SUCURSAL': 'Sucursal', 'PYG_CORTE': 'P y G Final CON compensados', 'COMPENNETO': 'Compensado $ Neto',
                        'COMPENGASTOS': 'Compensado $ gastos', 'COMPENINGRESOS': 'Compensado $ ingresos',
                        'COMPENFINANCIEROS': 'Compensado $ financieros', 'TOTALPYG': 'Total P y G contable',
                        'TOTALGASYCOS': 'Total gastos y costos', 'OTROSGASYCOS': 'Otras gastos y costos',
                        'GASTOPROV': 'Gasto provisión', 'TOTALING': 'Total ingresos', 'INGREPRESTAMOS': 'Ingresos por préstamos',
                        'OTROSINGRE': 'Otros ingresos', 'COSTODEPO': 'Costo de po (Depósitos)',
                        'GASOPEIMPU': 'Gasto Operativo + impuestos', 'DEPOSITOS': 'Depósitos',
                        'DEPOANOCOR': 'Depósitos año corrido', 'APORTES': 'Aportes', 'APORANOCOR': 'Aportes año corrido',
                        'CARTERA': 'Cartera', 'CARANOCOR': 'Cartera año corrido', 'ASOCIADOS': 'Asociados',
                        'ASOANOCOR': 'Asociados año corrido', 'CARTERAVENCIDA': 'Cartera vencida',
                        'CARVENANOCOR': 'Cartera vencida año corrido', 'CARIMPROANCOR': 'Cartera improductiva año corrido',
                        'TASAVENCID': '% Tasa Vencida', 'TASAIMPROD': '% Tasa Improductiva', 'TASAMARG': '% Tasa Marginal',
                        'TASACART': '% Tasa Cartera', 'TASADEPO': '% Tasa Depósitos',
                    }, inplace=True)
                elif selected_apre_type == 'apre_basico':
                    df.rename(columns={
                        'PROVINTMESANT': '% Provis / Interes mes ant', 'PROVINTMES': '% Provis / Interes corte',
                        'SUCURSAL': 'Sucursal', 'CARTERA': 'Cartera', 'CARVARMES': 'Cartera Var Mes',
                        'CARANOCOR': 'Cartera Año Corrido', 'CALIDAD': 'Calidad', 'CALVARMES': 'Calidad Var Mes',
                        'CARANOMES': 'Cartera Año Mes', 'CARTERAIMPRO': 'Cartera Improductiva',
                        'CARIMPROMES': 'Cartera Improductiva Mes', 'CARIMPROANCOR': 'Cartera Improductiva Año Corrido',
                        'APORTES': 'Aportes', 'APORVARMES': 'Aportes Var Mes', 'APORANOCOR': 'Aportes Año Corrido',
                        'DEPOSITOS': 'Depósitos', 'DEPOVARMES': 'Depósitos Var Mes', 'DEPOANOCOR': 'Depósitos Año Corrido',
                        'ASOCIADOS': 'Asociados', 'ASOVARMES': 'Asociados Var Mes', 'ASOANOCOR': 'Asociados Año Corrido',
                        'TASAMARG': 'Tasa Marginal', 'MARGANO': 'Margen Año', 'MARGVARMES': 'Margen Var Mes',
                        'TASADEPO': 'Tasa Depósitos', 'TASADEPOMES': 'Tasa Depósitos Mes', 'TASADEPOANO': 'Tasa Depósitos Año',
                        'TASACART': 'Tasa Cartera', 'TASACARTMES': 'Tasa Cartera Mes', 'TASACARTANO': 'Tasa Cartera Año',
                        'EXCEDENTES': 'Excedentes', 'PYG_CORTE': 'P y G Corte',
                    }, inplace=True)
                elif selected_apre_type == 'apre_diferencia':
                    df.rename(columns={
                        'PROVINTMESANT': '% Provis / Interes mes ant', 'INGREPRESTAMOSANT': 'Ingresos por préstamos Ant',
                        'OTROSINGREANT': 'Otros Ingresos Ant', 'GASTOPROVANT': 'Gasto Provisión Ant',
                        'OTROSGASYCOSANT': 'Otros Gastos y Costos Ant', 'EXCEDENTESANTESCOMANT': 'Excedentes Antes Comp. Ant',
                        'COMPENINGANT': 'Compensado Ingresos Ant', 'COMPENGASANT': 'Compensado Gastos Ant',
                        'EXCEDENTEFINALANT': 'Excedente Final Ant', 'PROVINTMES': '% Provis / Interes mes',
                        'INGREPRESTAMOS': 'Ingresos por préstamos', 'OTROSINGRE': 'Otros Ingresos',
                        'GASTOPROV': 'Gasto Provisión', 'OTROSGASYCOS': 'Otros Gastos y Costos',
                        'EXCEDENTESANTESCOM': 'Excedentes Antes Comp.', 'COMPENING': 'Compensado Ingresos',
                        'COMPENGAS': 'Compensado Gastos', 'EXCEDENTEFINAL': 'Excedente Final',
                    }, inplace=True)
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Reporte APRE')
                output.seek(0)
                
                response = HttpResponse(
                    output,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = 'attachment; filename="reporte_apre.xlsx"'
                return response

        except Exception as e:
            logger.error(f"Error en download_apre_excel: {e}", exc_info=True)
            return HttpResponse(f"Ocurrió un error al generar el reporte: {str(e)}", status=500)

    return HttpResponse("No se pudieron generar los datos para el reporte.", status=400)

def generate_summary_view(request):
    """
    Genera un resumen técnico de los datos del reporte APRE usando IA.
    """
    logger.info("=== INICIANDO generate_summary_view ===")
    
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            report_data = body.get('data', [])
            if not report_data:
                return JsonResponse({'error': 'No se proporcionaron datos para el resumen.'}, status=400)

            prompt = f"""Actúa como un analista financiero experto..."""
            summary = """### Concepto Técnico Consolidado..."""

            return JsonResponse({'summary': summary})

        except Exception as e:
            logger.error(f"Error en generate_summary_view: {e}", exc_info=True)
            return JsonResponse({'error': 'Ocurrió un error interno.'}, status=500)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)