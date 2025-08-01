import oracledb
import logging
from datetime import date, timedelta, datetime
from collections import OrderedDict
from django.conf import settings
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
# from .models import SarCIndicator, DatosMensualesSarC, SarLIndicator, DatosMensualesSarL
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import role_required
import statistics

#--------------------------------------------------------------------------------------#

logger = logging.getLogger(__name__)

#? =============
#? CONFIGURACIÓN
#? =============
INDICADOR_MAP = {
    # INDICADORES DE LIMITES (SIN G)
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
    # INDICADORES GRAFICABLES (CON G)
    '1G': 'Indicador De Cartera Vencida Por Temporalidad (Mora)',
    '2G': 'Indicador De Cartera Vencida Por Riesgo (Riesgo)',
    '3G': 'Indicador De Cartera Improductiva',
    '4G': 'Rodamiento General De Cartera',
    '5G': 'Rodamiento De Cartera A-B',
    '6G': 'Indicador De Fallo',
    '7G': 'Reverso General  Del Deterioro',
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
    if hoy.day == 1:
        corte = hoy - timedelta(days=1)
    else:
        primer_dia_mes_actual = hoy.replace(day=1)
        corte = primer_dia_mes_actual - timedelta(days=1)
    return corte.strftime('%Y%m')

    
def obtener_datos_sarc_sp(fecha_corte):
    try:
        db = settings.DATABASES['oracle']
        dsn = f"{db['HOST']}:{db['PORT']}/{db['NAME']}"
        fecha_corte_str = fecha_corte

        with oracledb.connect(user=db['USER'], password=db['PASSWORD'], dsn=dsn) as conn:
            with conn.cursor() as cursor:
                ref_cursor_out = cursor.var(oracledb.CURSOR)
                cursor.callproc('SP_INDICADORESRIESGOS', [fecha_corte_str, ref_cursor_out])
                cur = ref_cursor_out.getvalue()

                if cur:
                    cols = [c[0] for c in cur.description]
                    data = [dict(zip(cols, row)) for row in cur]
                    # logger.info(f"[SARC] Datos recibidos del SP_INDICADORESRIESGOS: {data}")
                    return data
        return []
    except Exception as e:
        logger.error(f"Error en obtener_datos_sarc_sp: {e}", exc_info=True)
        return []


def parse_fecha_mes(fecha_valor):
    """
    Función unificada para parsear fechas y evitar duplicados
    Retorna (fecha_obj, month_key) o (None, None) si falla
    """
    if not isinstance(fecha_valor, str) or '-' not in fecha_valor:
        return None, None
    
    try:
        mes_abbr, anio = fecha_valor.strip().split('-')
        mes_num_map = {
            'ENE': 1, 'FEB': 2, 'MAR': 3, 'ABR': 4, 'MAY': 5, 'JUN': 6,
            'JUL': 7, 'AGO': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DIC': 12
        }
        
        mes_abbr = mes_abbr.upper().strip()
        anio = anio.strip()
        
        if mes_abbr in mes_num_map and anio.isdigit():
            mes_num = mes_num_map[mes_abbr]
            
            # NORMALIZAR AÑO: siempre usar formato de 2 dígitos para month_key
            if len(anio) == 4:
                anio_completo = int(anio)
                anio_corto = anio[-2:]  # Últimos 2 dígitos
            elif len(anio) == 2:
                anio_completo = int(f"20{anio}")
                anio_corto = anio
            else:
                return None, None
            
            fecha_obj = date(anio_completo, mes_num, 1)
            # USAR SIEMPRE FORMATO CORTO PARA EVITAR DUPLICADOS: "ENE-22", "FEB-23", etc.
            month_key = f"{mes_abbr}-{anio_corto}"
            
            return fecha_obj, month_key
            
    except (ValueError, KeyError, AttributeError) as e:
        logger.warning(f"Error parseando fecha '{fecha_valor}': {e}")
        return None, None
    
    return None, None

def calcular_tabla_riesgo_sarc(datos):
    resultados = []

    #Agrupar los valores por INDICADOR
    indicadores = {}
    for d in datos:
        ind = d['INDICADOR']
        try:
            valor = float(d['VALOR'].replace(',', '.'))
        except (ValueError, AttributeError):
            continue
        indicadores.setdefault(ind, []).append(valor)

    for ind, valores in indicadores.items():
        if len(valores) < 2:
            continue # Necesita al menos 2 valores para calcular la variación

        # CALUCULAR LA DESVIACION DESVEST.M
        desv = statistics.stdev(valores)
        logger.debug(f"Desviación estándar para {ind}: {desv}")

        # TOLERANCIA
        tolerancia = statistics.mean(valores) * 2  # Usar desviación estándar como tolerancia

        # APETITO Y CAPACIDAD
        apetito = tolerancia - desv
        capacidad = tolerancia + desv

        # Máximo histórico
        maximo = max(valores)

        # Evaluar riesgo según la regla
        if capacidad > maximo > apetito:
            riesgo = 'Medio'
        else:
            riesgo = 'Alto'

        resultados.append({
            "INDICADOR": ind,
            "RIESGO": riesgo,
            "APETITO": apetito,
            "TOLERANCIA": tolerancia,
            "CAPACIDAD": capacidad,
            "VALOR": maximo,
        })
    
    return resultados

@method_decorator(login_required, name='dispatch')
@method_decorator(role_required(allowed_roles=['Riesgos']), name='dispatch')
class DashboardSarcView(TemplateView):
    template_name = "risk/dashboard/dashboardSarc.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fecha_corte = get_fecha_corte()
        raw_data = obtener_datos_sarc_sp(fecha_corte)

        # --- INTEGRACIÓN DE LA LÓGICA DE CÁLCULO DE RIESGO ---
        # Llamamos a la función que ya tienes para calcular la tabla de riesgo.
        tabla_riesgo = calcular_tabla_riesgo_sarc(raw_data)

        # DICCIONARIOS PARA PIVOTEAR LOS DATOS
        limites_pivot = {}
        indicadores_pivot = {}
        unique_months = {}  # Para evitar duplicados de meses
        
        # MANTENER EL ORDEN DEL PROCEDIMIENTO
        limites_order = []
        indicadores_order = []

        # Procesar datos
        for row in raw_data:
            indicador_code = str(row.get('INDICADOR', '')).strip()
            valor = row.get('VALOR')
            fecha_valor = row.get('MES')
            nombre_descriptivo = INDICADOR_MAP.get(indicador_code, f"Desconocido ({indicador_code})")

            # Validar que tenemos los datos necesarios
            if not all([indicador_code, valor is not None, fecha_valor]):
                continue

            # USAR FUNCIÓN UNIFICADA PARA PARSEAR FECHA
            fecha_obj, month_key = parse_fecha_mes(fecha_valor)
            
            if not fecha_obj or not month_key:
                logger.warning(f"No se pudo parsear la fecha: {fecha_valor}")
                continue

            # EVITAR DUPLICADOS DE MESES
            unique_months[month_key] = fecha_obj

            # Convertir valor a número
            try:
                if isinstance(valor, str):
                    valor = valor.replace(',', '.')
                    valor = float(valor)
                elif valor is None:
                    valor = 0
            except (ValueError, TypeError):
                logger.warning(f"Error convirtiendo valor: {valor}")
                valor = 0

            # GUARDAR EN PIVOTES Y MANTENER ORDEN DEL PROCEDIMIENTO
            if 'G' in indicador_code:  # Indicadores graficables
                if nombre_descriptivo not in indicadores_pivot:
                    indicadores_pivot[nombre_descriptivo] = {}
                    indicadores_order.append(nombre_descriptivo)
                indicadores_pivot[nombre_descriptivo][month_key] = valor
            else:  # Límites
                if nombre_descriptivo not in limites_pivot:
                    limites_pivot[nombre_descriptivo] = {}
                    limites_order.append(nombre_descriptivo)
                limites_pivot[nombre_descriptivo][month_key] = valor

        # ORDENAR MESES CRONOLÓGICAMENTE
        sorted_months = sorted(unique_months.items(), key=lambda x: x[1])
        months_columns = [{'key': month_key, 'display': month_key} for month_key, _ in sorted_months]

        # CONVERTIR A FORMATO DE PLANTILLA MANTENIENDO EL ORDEN
        context['limites_table_data'] = self.format_pivot_for_template_ordered(
            limites_pivot, months_columns, limites_order
        )
        context['indicadores_table_data'] = self.format_pivot_for_template_ordered(
            indicadores_pivot, months_columns, indicadores_order
        )
        context['months_columns'] = months_columns
        context['fecha_corte'] = fecha_corte

        # Añadimos la tabla de riesgo al contexto para que la plantilla la reciba.
        context['tabla'] = tabla_riesgo
        
        # DEBUG
        logger.info(f"[SARC] Procesados {len(limites_pivot)} límites y {len(indicadores_pivot)} indicadores")
        logger.info(f"[SARC] Meses únicos: {len(unique_months)} - {[m['key'] for m in months_columns]}")

        return context

    def format_pivot_for_template_ordered(self, pivot_data, months_columns, order_list):
        """
        Convierte los datos pivoteados manteniendo el orden del procedimiento
        """
        table_data = []
        
        for nombre in order_list:
            if nombre in pivot_data:
                monthly_values = pivot_data[nombre]
                row_data = {
                    'nombre': nombre,
                    'monthly_values': {}
                }
                
                # ASEGURAR QUE TODOS LOS MESES ESTÉN REPRESENTADOS
                for mc in months_columns:
                    month_key = mc['key']
                    valor = monthly_values.get(month_key, '-')
                    
                    # Formatear valores numéricos
                    if isinstance(valor, (int, float)) and valor != 0:
                        if isinstance(valor, float) and valor != int(valor):
                            row_data['monthly_values'][month_key] = f"{valor:.2f}"
                        else:
                            row_data['monthly_values'][month_key] = f"{int(valor)}"
                    else:
                        row_data['monthly_values'][month_key] = valor if valor != 0 else '-'
                
                table_data.append(row_data)
        
        return table_data


class DashboardSarcDataJsonView(TemplateView):
    """Vista para datos JSON de gráficas - Solo para INDICADOR_GRAFICABLE"""
    def get(self, request, *args, **kwargs):
        fecha_corte = get_fecha_corte()
        raw_data = obtener_datos_sarc_sp(fecha_corte)
        
        indicators_data = {}
        unique_dates = {}
        
        # PROCESAR DATOS SIN DUPLICADOS
        for row in raw_data:
            indicador_code = str(row.get('INDICADOR', '')).strip()
            valor = row.get('VALOR')
            fecha_valor = row.get('MES')
            
            # SOLO PROCESAR INDICADORES GRAFICABLES
            if 'G' not in indicador_code or not all([indicador_code, valor is not None, fecha_valor]):
                continue
            
            nombre_descriptivo = INDICADOR_MAP.get(indicador_code, f"Desconocido ({indicador_code})")
            
            # USAR FUNCIÓN UNIFICADA PARA PARSEAR FECHA
            fecha_obj, month_key = parse_fecha_mes(fecha_valor)
            
            if not fecha_obj or not month_key:
                continue
            
            # Convertir valor a número
            try:
                if isinstance(valor, str):
                    valor = valor.replace(',', '.')
                    valor = float(valor)
                elif valor is None:
                    valor = 0
            except (ValueError, TypeError):
                valor = 0
            
            # EVITAR DUPLICADOS AUTOMÁTICAMENTE
            unique_dates[month_key] = fecha_obj
            
            if nombre_descriptivo not in indicators_data:
                indicators_data[nombre_descriptivo] = {}
            
            # SOBRESCRIBIR SI EXISTE (evita duplicados por fecha)
            indicators_data[nombre_descriptivo][month_key] = {
                'fecha': fecha_obj,
                'fecha_display': month_key,
                'valor': valor
            }
        
        # ORDENAR FECHAS CRONOLÓGICAMENTE
        sorted_dates = sorted(unique_dates.items(), key=lambda x: x[1])
        chart_x_labels = [fecha_str for fecha_str, _ in sorted_dates]
        
        trend_data = []
        scatter_points = []
        
        # CONSTRUIR DATOS PARA GRÁFICAS SIN DUPLICADOS
        for nombre_descriptivo, monthly_data in indicators_data.items():
            points = []
            
            # USAR ORDEN CRONOLÓGICO ESTABLECIDO
            for fecha_display in chart_x_labels:
                if fecha_display in monthly_data:
                    points.append({
                        "fecha": fecha_display,
                        "valor": monthly_data[fecha_display]['valor'],
                    })
            
            if points:  # Solo agregar si tiene datos
                trend_data.append({
                    "nombre_limite": nombre_descriptivo,
                    "metodologia": "",
                    "data_points": points,
                })
                
                # Para scatter plot (comparar últimos dos valores)
                if len(points) >= 2:
                    scatter_points.append({
                        "x": points[-2]["valor"],
                        "y": points[-1]["valor"],
                        "label": nombre_descriptivo
                    })
        
        result = {
            "trend_data": trend_data,
            "chart_labels": chart_x_labels, 
            "scatter_data": {
                "points": scatter_points,
                "xAxisLabel": "Valor Anterior",
                "yAxisLabel": "Valor Actual"
            }
        }
        
        logger.info(f"[SARC JSON] Enviando {len(trend_data)} indicadores con {len(chart_x_labels)} meses únicos")
        
        return JsonResponse(result, safe=False, json_dumps_params={'indent': 2})


# ------------------------------------------------------------------------#
# -- DASHBOARD SARL -- (Indicadores de Riesgo SARL)
# @method_decorator(login_required, name='dispatch')
# @method_decorator(role_required(allowed_roles=['Administradores', 'Analistas SARL']), name='dispatch')
# class DashboardSarlView(TemplateView):
#     template_name = "dashboard/dashboardSarL.html"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         # -- TABLA DE INDICADORES SARL --
#         # OBTENER TODOS LOS INDICADORES SARL
#         all_sarl_indicartor_ids = SarLIndicator.objects.values_list('id', flat=True)

#         unique_dates_with_data_sarl = DatosMensualesSarL.objects.filter(
#             indicator_id__in=all_sarl_indicartor_ids
#         ).values_list('fecha', flat=True).distinct()

#         # -- ORDENAR LAS FECHAS Y GENERAR LA LISTA DE COLUMNAS DE MESES
#         sorted_unique_dates_sarl = sorted(list(unique_dates_with_data_sarl))
#         # -- GENERAR LA LISTA DE MESES EN EL FORMATO 'ene-25', 'feb-25', etc.
#         months_columns_dict_sarl = OrderedDict()
#         for date in sorted_unique_dates_sarl:
#             month_key = self.date_to_month_key(date)
#             if month_key not in months_columns_dict_sarl:
#                 # Usamos la primera fecha encontrada para cada mes como referencia
#                 months_columns_dict_sarl[month_key] = {'key': month_key, 'date': date, 'display': month_key}

#         months_columns_list_sarl = list(months_columns_dict_sarl.values())  # Convertir a lista y guardar en variable local
#         context["months_columns_sarl"] = months_columns_list_sarl

#         limites_sarl_data = self.prepare_limites_sarl_table_data(months_columns_list_sarl)
#         context["limites_sarl_table_data"] = limites_sarl_data

#         return context
    
#     def prepare_limites_sarl_table_data(self, months_columns):
#         """Prepara datos para la tabla de Límites (SARL)"""

#         limites_indicators = SarLIndicator.objects.all().prefetch_related('monthly_data').order_by('id')
        
#         table_data = []
        
#         for indicator in limites_indicators:
#             # -- OBTENER TODOS LOS DATOS MENSUALES DEL INDICADOR --
#             monthly_data_dict = {}
#             for data in indicator.monthly_data.all():
#                 month_key = self.date_to_month_key(data.fecha)
#                 monthly_data_dict[month_key] = data.valor
            
#             # -- PREPARAR FILA DE DATOS --
#             row_data = {
#                 'nombre': indicator.nombre_indicador,
#                 'tipo': indicator.tipo, # Añadir el tipo del indicador SARL
#                 'metodologia': indicator.metodologia,
#                 'limite_apetito': indicator.limite_apetito,
#                 'limite_tolerancia': indicator.limite_tolerancia,
#                 'monthly_values': {},
#                 'variacion_porcentaje': self.calculate_variation(monthly_data_dict, months_columns), # indicator.tipo no se usa actualmente en la función de SARL
#                 'indicador_riesgo': self.calculate_risk_indicator(monthly_data_dict, indicator, months_columns) # Pasar months_columns
#             }
            
#             # -- LLENAR VALORES MENSUALES --
#             for month in months_columns:
#                 month_key = month['key']
#                 row_data['monthly_values'][month_key] = monthly_data_dict.get(month_key, '-')
            
#             table_data.append(row_data)
            
#         return table_data
    
#     def date_to_month_key(self, date):
#         """Convierte fecha a formato 'ene-25'"""
#         month_names = {
#             1: 'ene', 2: 'feb', 3: 'mar', 4: 'abr', 5: 'may', 6: 'jun',
#             7: 'jul', 8: 'ago', 9: 'sep', 10: 'oct', 11: 'nov', 12: 'dic'
#         }
#         return f"{month_names[date.month]}-{str(date.year)[2:]}"
    
#     def calculate_variation(self, monthly_data_dict, months_columns):
#         """Calcula la variación como la resta entre los dos últimos meses con datos para SARL."""
#         values = [] # TIPO DE LISTA [FLOAT]
#         # Iterar sobre months_columns (que está ordenado cronológicamente) en reversa
#         for month_spec in reversed(months_columns):
#             month_key = month_spec['key']
#             value = monthly_data_dict.get(month_key)
#             if value is not None and value != '-':
#                 try:
#                     values.append(float(value))
#                     if len(values) == 2: # Tenemos actual y anterior
#                         break
#                 except ValueError:
#                     continue # Ignorar si no es un número

#         if len(values) == 2:
#             current_value, previous_value = values[0], values[1] # values[0] es el más reciente
#             variation = current_value - previous_value # Resta simple
#             return f"{variation:.1f}" # Formato a un decimal, sin %
#         return "-"

#     def calculate_risk_indicator(self, monthly_data_dict, indicator, months_columns):
#         """Calcula indicador de riesgo basado en el último valor disponible"""
#         # OBTENER EL ÚLTIMO VALOR DISPONIBLE
#         last_value = None
#         # Iterar sobre months_columns (que está ordenado cronológicamente) en reversa
#         # para encontrar el último valor con datos.
#         for month_spec in reversed(months_columns):
#             month_key = month_spec['key']
#             value = monthly_data_dict.get(month_key)
#             if value is not None and value != '-':
#                 try:
#                     last_value = float(value)
#                     break 
#                 except ValueError:
#                     continue # Saltar si no es un número válido
        
#         if last_value is None:
#             return "Sin datos"
        
#         # COMPARAR CON LOS LÍMITES DE RIESGO
#         try:
#             apetito = float(indicator.limite_apetito) if indicator.limite_apetito is not None else float('-inf')
#             tolerancia = float(indicator.limite_tolerancia) if indicator.limite_tolerancia is not None else float('-inf')
            
#             if indicator.limite_apetito is None and indicator.limite_tolerancia is None:
#                  return "N/A"
            
#             if last_value <= apetito:
#                 return "Bajo"
#             elif last_value <= tolerancia:
#                 return "Medio"
#             else:
#                 return "Alto"
#         except (ValueError, TypeError):
#             return "Medio"  # MEDIO POR DEFECTO SI HAY ERROR EN LOS LÍMITES

# class DashboardSarlDataJsonView(TemplateView):
#     def get(self, request, *args, **kwargs):
#         indicators = SarLIndicator.objects.all()
#         trend_data = []

#         latest_date = None
#         all_monthly_dates = DatosMensualesSarL.objects.values_list('fecha', flat=True).distinct().order_by('-fecha')
#         if all_monthly_dates:
#             latest_date = all_monthly_dates.first()

#         for ind in indicators:
#             monthly = ind.monthly_data.order_by('fecha')
#             points = []
#             for m in monthly:
#                 points.append({
#                     "fecha": m.fecha.strftime("%Y-%m"), # Formato consistente para Chart.js
#                     "valor": float(m.valor) if m.valor is not None else None, # Manejar valor None
#                 })
#             trend_data.append({
#                 "nombre_indicador": ind.nombre_indicador,
#                 "tipo": ind.tipo,
#                 "data_points": points,
#             })
        
#         niveles = []
#         categorias_nivel = []
#         valores_ultimo_mes_para_promedio = []

#         if latest_date: # Solo calcular niveles si tenemos una latest_date
#             for ind in indicators:
#                 last = ind.monthly_data.filter(fecha=latest_date).first()
#                 if last and last.valor is not None: # Asegurarse que hay un valor
#                     val = last.valor
#                     valores_ultimo_mes_para_promedio.append(float(val))
#                     val_float = float(val)
                    
#                     # Usar -inf / +inf para límites no definidos puede ser más robusto
#                     # dependiendo de si un valor más alto o más bajo es "mejor"
#                     # Aquí asumimos que valores más bajos son mejores.
#                     apetito_float = float(ind.limite_apetito) if ind.limite_apetito is not None else float('inf') 
#                     tolerancia_float = float(ind.limite_tolerancia) if ind.limite_tolerancia is not None else float('inf')

#                     if ind.limite_apetito is None and ind.limite_tolerancia is None:
#                         nivel = "no_aplica" # O algún otro identificador para "sin límites"
#                     elif val_float <= apetito_float:
#                         nivel = "apetito"
#                     elif val_float <= tolerancia_float:
#                         nivel = "tolerancia"
#                     else:
#                         nivel = "fuera_limite"
                        
#                     niveles.append({
#                         "nombre_indicador": ind.nombre_indicador,
#                         "valor": val_float,
#                         "nivel": nivel,
#                         "limite_apetito": ind.limite_apetito, # Enviar el valor original para info
#                         "limite_tolerancia": ind.limite_tolerancia, # Enviar el valor original para info
#                     })
#                     if nivel != "no_aplica":
#                         categorias_nivel.append(nivel)
                
#         # promedio_riesgo es el promedio de los VALORES numéricos de los indicadores.
#         # Lo mantenemos por si se usa, pero para el velocímetro usaremos un índice basado en niveles.
#         indice_riesgo_general_sarl = None
#         if categorias_nivel: # Solo si hay categorías con límites definidos
#             score_map = {"apetito": 1, "tolerancia": 2, "fuera_limite": 3}
#             total_score = sum(score_map.get(nivel, 2) for nivel in categorias_nivel)
#             avg_score = total_score / len(categorias_nivel)
#             indice_riesgo_general_sarl = min(max(((avg_score - 1) / (3 - 1)) * 100, 0), 100)
            
#         frecuencia = Counter(categorias_nivel)
#         total_categorias = len(categorias_nivel) # Usar el total de categorías con límites
#         distribucion = {k: (v / total_categorias * 100) if total_categorias > 0 else 0 for k, v in frecuencia.items()}

#         result = {
#             "trend_data": trend_data,
#             "niveles_ultimo_mes": niveles,
#             # "promedio_riesgo_valores": promedio_riesgo_valores,
#             "indice_riesgo_general_sarl": indice_riesgo_general_sarl,
#             "distribucion_porcentual": distribucion,
#             "frecuencia_niveles": dict(frecuencia),
#             "latest_month": latest_date.strftime("%Y-%m") if latest_date else None,
#         }
#         return JsonResponse(result, safe=False, json_dumps_params={'indent': 2})
    

# # ------------------------------------------------------------------------#

# # Ejemplo conceptual en tu vista (por ejemplo, views.py)
# # from django.db import connection

# # def obtener_datos_desde_oracle_sp(nombre_sp, parametros_sp):
# #     datos_procesados = []
# #     with connection.cursor() as cursor:
# #         # La forma de llamar y obtener resultados puede variar ligeramente
# #         # dependiendo de si el SP devuelve un ref cursor o tiene params de salida.
# #         # Este es un ejemplo general.
# #         cursor.callproc(nombre_sp, parametros_sp)

# #         # Si el SP devuelve un conjunto de resultados directamente o a través de un ref cursor
# #         for row in cursor:
# #             # Aquí transformarías cada 'row' del SP
# #             # a la estructura que tu plantilla espera.
# #             # Por ejemplo, si el SP devuelve (nombre, metodologia, fecha_valor, valor_mes):
# #             dato_transformado = {
# #                 'nombre_indicador': row[0],
# #                 'metodologia_indicador': row[1],
# #                 'fecha': row[2], # Asegúrate que sea un objeto date/datetime
# #                 'valor': row[3]
# #                 # ... y otros campos que devuelva el SP
# #             }
# #             datos_procesados.append(dato_transformado)
# #     return datos_procesados

# # # Luego, en tu método prepare_X_table_data:
# # # raw_data_from_sp = obtener_datos_desde_oracle_sp('MI_PROCEDIMIENTO_SARC', [param1, param2])
# # # Y luego procesarías raw_data_from_sp para construir la estructura final
# # # que va al contexto de la plantilla (similar a como lo haces ahora
# # # pero partiendo de los datos del SP en lugar de objetos del ORM).
