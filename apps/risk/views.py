import oracledb
import logging
from datetime import date, timedelta
from collections import OrderedDict
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views import View
from django.http import JsonResponse
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
import pandas as pd
import statistics

from apps.accounts.decorators import role_required
from .forms import UploadFileForm
from .models import ParametrosRiesgo

logger = logging.getLogger(__name__)

# Definición explícita del orden de los indicadores, según lo solicitado.
INDICADORES_LIMITES_ORDER = [
    'Total Cartera',
    'Maximo Cartera Consumo',
    'Maximo Cartera Microcredito',
    'Maximo Cartera Comercial',
    'Máximo de Cartera Otras Garantías',
    'Máximo de Cartera Sin Garantías',
    'Máximo de Cartera Hipoteca',
    'Máximo de Cartera Rentas',
    'Máximo de Cartera Otras Admisibles',
    'Máximo de cartera Fondos de garantía',
    'Maximo Indicador Morosidad',
    'Limite de Acumulacion',
    'Concentración por deudor',
    'Concentración por línea de crédito',
    'Concentración por clasificación de cartera',
    'Concentración por plazo al vencimiento',
    'Concentración por zona',
    'Concentración por sector económico',
]

INDICADORES_GRAFICABLES_ORDER = [
    'Indicador De Cartera Vencida Por Temporalidad (Mora)',
    'Indicador De Cartera Vencida Por Riesgo (Riesgo)',
    'Indicador De Cartera Improductiva',
    'Rodamiento General De Cartera',
    'Rodamiento De Cartera A-B',
    'Indicador De Fallo',
    'Reverso General del Deterioro',
    'Indicador De Cobertura',
    'Relacion Riesgo / Mora',
    'Cartera Castigada',
    'Cartera Reestructurada',
    'Calidad De Cosechas',
    'Crecimiento Cartera Bruta',
]

# Mapa de código a nombre, usado para el procesamiento de datos.
INDICADOR_MAP = {
    '1': 'Total Cartera',
    '2': 'Maximo Cartera Consumo',
    '3': 'Maximo Cartera Microcredito',
    '4': 'Maximo Cartera Comercial',
    '5': 'Máximo de Cartera Otras Garantías',
    '6': 'Máximo de Cartera Sin Garantías',
    '7': 'Máximo de Cartera Hipoteca',
    '8': 'Máximo de Cartera Rentas',
    '9': 'Máximo de Cartera Otras Admisibles',
    '10': 'Máximo de cartera Fondos de garantía',
    '11': 'Maximo Indicador Morosidad',
    '12': 'Limite de Acumulacion',
    '13': 'Concentración por deudor',
    '14': 'Concentración por línea de crédito',
    '15': 'Concentración por clasificación de cartera',
    '16': 'Concentración por plazo al vencimiento',
    '17': 'Concentración por zona',
    '18': 'Concentración por sector económico',
    '1G': 'Indicador De Cartera Vencida Por Temporalidad (Mora)',
    '2G': 'Indicador De Cartera Vencida Por Riesgo (Riesgo)',
    '3G': 'Indicador De Cartera Improductiva',
    '4G': 'Rodamiento General De Cartera',
    '5G': 'Rodamiento De Cartera A-B',
    '6G': 'Indicador De Fallo',
    '7G': 'Reverso General del Deterioro',
    '8G': 'Indicador De Cobertura',
    '9G': 'Relacion Riesgo / Mora',
    '10G': 'Cartera Castigada',
    '11G': 'Cartera Reestructurada',
    '12G': 'Calidad De Cosechas',
    '13G': 'Crecimiento Cartera Bruta',
}

def get_fecha_corte():
    """
    Calcula la fecha de corte según las reglas del procedimiento
    """
    hoy = date.today()
    primer_dia_mes_actual = hoy.replace(day=1)
    corte = primer_dia_mes_actual - timedelta(days=1)
    return corte.strftime('%Y%m')

def obtener_datos_sarc_sp(fecha_corte):
    try:
        db = settings.DATABASES['oracle']
        dsn = f"{db['HOST']}:{db['PORT']}/{db['NAME']}"
        with oracledb.connect(user=db['USER'], password=db['PASSWORD'], dsn=dsn) as conn:
            with conn.cursor() as cursor:
                ref_cursor_out = cursor.var(oracledb.CURSOR)
                cursor.callproc('SP_INDICADORESRIESGOS', [fecha_corte, ref_cursor_out])
                cur = ref_cursor_out.getvalue()
                if cur:
                    cols = [c[0] for c in cur.description]
                    return [dict(zip(cols, row)) for row in cur]
        return []
    except Exception as e:
        logger.error(f"Error en obtener_datos_sarc_sp: {e}", exc_info=True)
        return []

def parse_fecha_mes(fecha_valor):
    if not isinstance(fecha_valor, str) or '-' not in fecha_valor:
        return None, None
    try:
        mes_abbr, anio = fecha_valor.strip().split('-')
        mes_num_map = {
            'ENE': 1, 'FEB': 2, 'MAR': 3, 'ABR': 4, 'MAY': 5, 'JUN': 6,
            'JUL': 7, 'AGO': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DIC': 12
        }
        mes_num = mes_num_map.get(mes_abbr.upper().strip())
        if mes_num and anio.strip().isdigit():
            anio_str = anio.strip()
            anio_completo = int(f"20{anio_str}") if len(anio_str) == 2 else int(anio_str)
            fecha_obj = date(anio_completo, mes_num, 1)
            month_key = f"{mes_abbr.upper()}-{anio_str[-2:]}"
            return fecha_obj, month_key
    except (ValueError, KeyError, AttributeError) as e:
        logger.warning(f"Error parseando fecha '{fecha_valor}': {e}")
    return None, None

@method_decorator(login_required, name='dispatch')
@method_decorator(role_required(allowed_roles=['Riesgos']), name='dispatch')
class DashboardSarcView(TemplateView):
    template_name = "risk/dashboard/dashboardSarc.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fecha_corte = get_fecha_corte()
        raw_data = obtener_datos_sarc_sp(fecha_corte)
        parametros_manuales = {p.indicador_codigo: p for p in ParametrosRiesgo.objects.all()}
        
        unique_months = OrderedDict()
        for row in raw_data:
            _, month_key = parse_fecha_mes(row.get('MES'))
            if month_key and month_key not in unique_months:
                unique_months[month_key] = None
        
        months_columns = [{'key': k, 'display': k} for k in unique_months.keys()]
        latest_month_key = months_columns[-1]['key'] if months_columns else None

        limites_pivot, indicadores_pivot = self._pivot_data(raw_data, parametros_manuales, latest_month_key)

        context['limites_table_data'] = self._format_pivot_for_template(limites_pivot, months_columns, INDICADORES_LIMITES_ORDER)
        context['indicadores_table_data'] = self._format_pivot_for_template(indicadores_pivot, months_columns, INDICADORES_GRAFICABLES_ORDER)
        
        context['tabla_riesgo_limites'] = self._generar_tabla_riesgo(raw_data, parametros_manuales, is_graphable=False)
        context['tabla_riesgo_indicadores'] = self._generar_tabla_riesgo(raw_data, parametros_manuales, is_graphable=True)

        context['months_columns'] = months_columns
        return context

    def _pivot_data(self, raw_data, parametros_manuales, latest_month_key):
        pivot_data = {}
        for row in raw_data:
            indicador_code = str(row.get('INDICADOR', '')).strip()
            nombre_descriptivo = INDICADOR_MAP.get(indicador_code)
            _, month_key = parse_fecha_mes(row.get('MES'))
            if not all([nombre_descriptivo, month_key, row.get('VALOR') is not None]):
                continue

            valor = float(str(row['VALOR']).replace(',', '.'))
            if month_key == latest_month_key:
                parametro = parametros_manuales.get(indicador_code)
                if parametro and parametro.valor_override is not None:
                    valor = parametro.valor_override
            
            pivot_data.setdefault(nombre_descriptivo, {})[month_key] = valor
        
        limites_pivot = {k: v for k, v in pivot_data.items() if k in INDICADORES_LIMITES_ORDER}
        indicadores_pivot = {k: v for k, v in pivot_data.items() if k in INDICADORES_GRAFICABLES_ORDER}
        return limites_pivot, indicadores_pivot

    def _generar_tabla_riesgo(self, raw_data, parametros_manuales, is_graphable):
        resultados = []
        map_code_to_name = {k: v for k, v in INDICADOR_MAP.items()}
        map_name_to_code = {v: k for k, v in map_code_to_name.items()}
        order_list = INDICADORES_GRAFICABLES_ORDER if is_graphable else INDICADORES_LIMITES_ORDER

        for nombre_indicador in order_list:
            ind_code = map_name_to_code.get(nombre_indicador)
            if not ind_code: continue

            parametro = parametros_manuales.get(ind_code)
            valores_historicos = [float(str(d['VALOR']).replace(',', '.')) for d in raw_data if d.get('INDICADOR') == ind_code and d.get('VALOR') is not None]
            valor_actual = max(valores_historicos) if valores_historicos else 0

            if parametro and parametro.valor_override is not None:
                valor_actual = parametro.valor_override

            apetito, tolerancia, capacidad, riesgo = None, None, None, 'N/A'
            if parametro and all(p is not None for p in [parametro.apetito, parametro.tolerancia, parametro.capacidad]):
                apetito, tolerancia, capacidad = parametro.apetito, parametro.tolerancia, parametro.capacidad
                if valor_actual > capacidad:
                    riesgo = 'Alto'
                elif valor_actual > tolerancia:
                    riesgo = 'Medio'
                else:
                    riesgo = 'Bajo'
            
            resultados.append({
                "INDICADOR": nombre_indicador,
                "RIESGO": riesgo,
                "APETITO": apetito,
                "TOLERANCIA": tolerancia,
                "CAPACIDAD": capacidad,
            })
        return resultados

    def _format_pivot_for_template(self, pivot_data, months_columns, order_list):
        table_data = []
        for nombre in order_list:
            row_data = {'nombre': nombre, 'monthly_values': {}}
            for mc in months_columns:
                row_data['monthly_values'][mc['key']] = pivot_data.get(nombre, {}).get(mc['key'], '-')
            table_data.append(row_data)
        return table_data

@method_decorator(login_required, name='dispatch')
@method_decorator(role_required(allowed_roles=['Riesgos']), name='dispatch')
class UploadParametrosRiesgoView(View):
    template_name = 'risk/upload_parametros.html'
    form_class = UploadFileForm
    
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, "Formulario inválido.")
            return render(request, self.template_name, {'form': form})
        
        file = request.FILES['file']
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file, dtype={'indicador_codigo': str})
            elif file.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file, dtype={'indicador_codigo': str})
            else:
                messages.error(request, "Formato de archivo no soportado. Use CSV o Excel.")
                return redirect(request.path)

            df.columns = [col.strip().lower() for col in df.columns]
            updated_count, created_count = 0, 0

            for _, row in df.iterrows():
                indicador_codigo = row.get('indicador_codigo')
                if pd.isna(indicador_codigo):
                    continue
                
                indicador_codigo = str(indicador_codigo).strip()
                if not indicador_codigo:
                    continue

                defaults = {}
                for col in ['apetito', 'tolerancia', 'capacidad', 'valor_override']:
                    if col in row and pd.notna(row[col]):
                        defaults[col] = row[col]

                if not defaults:
                    continue

                _, created = ParametrosRiesgo.objects.update_or_create(
                    indicador_codigo=indicador_codigo,
                    defaults=defaults
                )
                if created: created_count += 1
                else: updated_count += 1
            
            messages.success(request, f"Archivo procesado. {created_count} registros creados, {updated_count} actualizados.")
        except Exception as e:
            logger.error(f"Error al procesar el archivo de parámetros: {e}", exc_info=True)
            messages.error(request, f"Ocurrió un error al procesar el archivo: {e}")
        
        return redirect(request.path)

class DashboardSarcDataJsonView(TemplateView):
    def get(self, request, *args, **kwargs):
        fecha_corte = get_fecha_corte()
        raw_data = obtener_datos_sarc_sp(fecha_corte)
        parametros_manuales = {p.indicador_codigo: p for p in ParametrosRiesgo.objects.all()}
        map_name_to_code = {v: k for k, v in INDICADOR_MAP.items()}

        indicators_data = {}
        unique_dates = {}
        
        for row in raw_data:
            indicador_code = str(row.get('INDICADOR', '')).strip()
            if 'G' not in indicador_code: continue

            nombre_descriptivo = INDICADOR_MAP.get(indicador_code)
            valor = row.get('VALOR')
            fecha_valor = row.get('MES')

            if not all([nombre_descriptivo, valor is not None, fecha_valor]): continue
            
            fecha_obj, month_key = parse_fecha_mes(fecha_valor)
            if not fecha_obj or not month_key: continue
            
            try:
                valor_float = float(str(valor).replace(',', '.'))
            except (ValueError, TypeError):
                valor_float = 0
            
            unique_dates[month_key] = fecha_obj
            indicators_data.setdefault(nombre_descriptivo, {})[month_key] = {
                'fecha': fecha_obj, 'valor': valor_float
            }
        
        sorted_dates = sorted(unique_dates.items(), key=lambda x: x[1])
        chart_x_labels = [k for k, _ in sorted_dates]
        
        trend_data = []
        for nombre in INDICADORES_GRAFICABLES_ORDER:
            monthly_data = indicators_data.get(nombre, {})
            points = [{"fecha": label, "valor": monthly_data.get(label, {}).get('valor')} for label in chart_x_labels]
            
            indicador_code = map_name_to_code.get(nombre)
            parametro = parametros_manuales.get(indicador_code)
            
            apetito, capacidad = None, None
            if parametro:
                apetito = parametro.apetito
                capacidad = parametro.capacidad

            trend_data.append({
                "nombre_limite": nombre, 
                "data_points": points,
                "apetito": apetito,
                "capacidad": capacidad
            })
        
        return JsonResponse({"trend_data": trend_data, "chart_labels": chart_x_labels}, safe=False)