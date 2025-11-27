from pathlib import Path
path = Path('apps/riesgos/views.py')
lines = path.read_text(encoding='utf-8').splitlines()
start = None
end = None
for i,l in enumerate(lines):
    if 'def _generar_tabla_riesgo(self, raw_data, parametros_manuales, is_graphable, latest_month_key):' in l and start is None:
        start = i
    if start is not None and i>start and l.strip().startswith('def _format_pivot_for_template'):
        end = i
        break
if start is None or end is None:
    raise SystemExit('function not found')
new_block = '''    def _generar_tabla_riesgo(self, raw_data, parametros_manuales, is_graphable, latest_month_key):
        resultados = []
        map_name_to_code = {v: k for k, v in SARL_INDICADOR_MAP.items()}
        order_list = SARL_INDICADORES_GRAFICABLES_ORDER if is_graphable else SARL_INDICADORES_NO_GRAFICABLES_ORDER

        for nombre_indicador in order_list:
            ind_code = map_name_to_code.get(nombre_indicador)
            if not ind_code:
                continue

            parametro = parametros_manuales.get(ind_code)

            # Valor mas reciente basado en MES (con override por mes)
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
                try:
                    r0 = (apetito - tolerancia) / 4
                except Exception:
                    r0 = None

                if r0 is not None:
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
'''.splitlines()
lines = lines[:start] + new_block + lines[end:]
path.write_text('\n'.join(lines)+'\n', encoding='utf-8')
