from pathlib import Path
path = Path('apps/riesgos/views.py')
lines = path.read_text(encoding='utf-8').split('\n')

# SARC block
sarc_start, sarc_end = 194, 266
sarc_block = '''    def _generar_tabla_riesgo(self, raw_data, parametros_manuales, is_graphable, latest_month_key):
        resultados = []
        map_code_to_name = {k: v for k, v in INDICADOR_MAP.items()}
        map_name_to_code = {v: k for k, v in map_code_to_name.items()}
        order_list = INDICADORES_GRAFICABLES_ORDER if is_graphable else INDICADORES_LIMITES_ORDER

        for nombre_indicador in order_list:
            ind_code = map_name_to_code.get(nombre_indicador)
            if not ind_code:
                continue

            parametro = parametros_manuales.get(ind_code)

            datos_indicador_historicos = [
                d for d in raw_data
                if INDICADOR_MAP.get(str(d.get('INDICADOR', '')).strip()) == nombre_indicador and d.get('VALOR') is not None and d.get('MES') is not None
            ]

            valor_actual = 0
            if datos_indicador_historicos:
                datos_con_fecha = []
                for d in datos_indicador_historicos:
                    fecha_obj, _ = parse_fecha_mes(d.get('MES'))
                    if fecha_obj:
                        d['parsed_date'] = fecha_obj
                        datos_con_fecha.append(d)

                if datos_con_fecha:
                    datos_con_fecha.sort(key=lambda x: x['parsed_date'], reverse=True)
                    registro_mas_reciente = datos_con_fecha[0]
                    try:
                        valor_actual = float(str(registro_mas_reciente['VALOR']).replace(',', '.'))
                    except (ValueError, TypeError):
                        valor_actual = 0

                    _, month_key = parse_fecha_mes(registro_mas_reciente.get('MES'))
                    if parametro and parametro.valor_override is not None and parametro.valor_override_mes:
                        if month_key == parametro.valor_override_mes.upper():
                            valor_actual = parametro.valor_override

            elif parametro and parametro.valor_override is not None and parametro.valor_override_mes:
                if parametro.valor_override_mes.upper() == latest_month_key:
                    valor_actual = parametro.valor_override

            apetito = parametro.apetito if parametro else None
            tolerancia = parametro.tolerancia if parametro else None
            capacidad = parametro.capacidad if parametro else None

            riesgo = 'N/A'
            if parametro and all(p is not None for p in [parametro.apetito, parametro.tolerancia, parametro.capacidad]):
                apetito, tolerancia, capacidad = parametro.apetito, parametro.tolerancia, parametro.capacidad
                if valor_actual < apetito:
                    riesgo = 'Bajo'
                elif valor_actual < capacidad and valor_actual > apetito:
                    riesgo = 'Medio'
                else:
                    riesgo = 'Alto'

            resultados.append({
                "INDICADOR": nombre_indicador,
                "RIESGO": riesgo,
                "APETITO": apetito,
                "TOLERANCIA": tolerancia,
                "CAPACIDAD": capacidad,
            })
        return resultados
'''.split('\n')

# SARL block
sarl_start = 575
sarl_end = None
for i in range(sarl_start+1, len(lines)):
    if lines[i].startswith('    def _format_pivot_for_template'):
        sarl_end = i
        break
if sarl_end is None:
    sarl_end = len(lines)

sarl_block = '''    def _generar_tabla_riesgo(self, raw_data, parametros_manuales, is_graphable, latest_month_key):
        resultados = []
        map_name_to_code = {v: k for k, v in SARL_INDICADOR_MAP.items()}
        order_list = SARL_INDICADORES_GRAFICABLES_ORDER if is_graphable else SARL_INDICADORES_NO_GRAFICABLES_ORDER

        for nombre_indicador in order_list:
            ind_code = map_name_to_code.get(nombre_indicador)
            if not ind_code:
                continue

            parametro = parametros_manuales.get(ind_code)
            
            datos_indicador_historicos = [
                d for d in raw_data 
                if SARL_INDICADOR_MAP.get(str(d.get('INDICADOR', '')).strip()) == nombre_indicador and d.get('VALOR') is not None and d.get('MES') is not None
            ]

            valor_actual = 0
            if datos_indicador_historicos:
                datos_con_fecha = []
                for d in datos_indicador_historicos:
                    fecha_obj, _ = parse_fecha_mes(d.get('MES'))
                    if fecha_obj:
                        d['parsed_date'] = fecha_obj
                        datos_con_fecha.append(d)

                if datos_con_fecha:
                    datos_con_fecha.sort(key=lambda x: x['parsed_date'], reverse=True)
                    registro_mas_reciente = datos_con_fecha[0]
                    try:
                        valor_actual = float(str(registro_mas_reciente['VALOR']).replace(',', '.'))
                    except (ValueError, TypeError):
                        valor_actual = 0

                    _, month_key = parse_fecha_mes(registro_mas_reciente.get('MES'))
                    if parametro and parametro.valor_override is not None and parametro.valor_override_mes:
                        if month_key == parametro.valor_override_mes.upper():
                            valor_actual = parametro.valor_override
            
            elif parametro and parametro.valor_override is not None and parametro.valor_override_mes:
                if parametro.valor_override_mes.upper() == latest_month_key:
                    valor_actual = parametro.valor_override

            apetito = parametro.apetito if parametro else None
            tolerancia = parametro.tolerancia if parametro else None
            capacidad = parametro.capacidad if parametro else None

            riesgo = 'N/A'
            if parametro and apetito is not None and tolerancia is not None:
                r0 = (apetito - tolerancia) / 4
                r1 = min(tolerancia, valor_actual)
                thresholds = [r1, r1 + r0, r1 + 2 * r0, r1 + 3 * r0, r1 + 4 * r0]
                labels = ['MINIMO', 'BAJO', 'MEDIO', 'ALTO', 'MUY ALTO'] if (parametro.orden == ParametrosRiesgoSarL.DESC) else ['MUY ALTO', 'ALTO', 'MEDIO', 'BAJO', 'MINIMO']
                riesgo = labels[0]
                for t, label in zip(thresholds, labels):
                    if valor_actual >= t:
                        riesgo = label
            
            resultados.append({
                "INDICADOR": nombre_indicador,
                "RIESGO": riesgo,
                "APETITO": apetito,
                "TOLERANCIA": tolerancia,
                "CAPACIDAD": capacidad,
            })
        return resultados
'''.split('\n')

lines = lines[:sarc_start] + sarc_block + lines[sarc_end:]
lines = lines[:sarl_start] + sarl_block + lines[sarl_end:]
path.write_text('\n'.join(lines), encoding='utf-8')
