from pathlib import Path
path = Path('apps/riesgos/templates/risk/upload_parametros.html')
lines = path.read_text(encoding='utf-8').splitlines()
start = 12  # line 13 zero-based
end = 27    # up to but not including line 28
new_block = [
    "            <h5 class=\"card-title\">Instrucciones</h5>",
    "            <p class=\"card-text\">",
    "                Suba un archivo Excel (.xlsx) o CSV (.csv) con los parametros de riesgo. La primera fila debe contener los encabezados de columna.",
    "            </p>",
    "            <div class=\"alert alert-info mb-3\">",
    "                <small>La plantilla descargable ya incluye el campo <b>valor_override_mes</b> para aplicar valores manuales por mes.</small>",
    "            </div>",
    "            <h6>Columnas Esperadas:</h6>",
    "            <ul class=\"list-group list-group-flush\">",
    "                <li class=\"list-group-item\"><b>indicador_codigo</b>: (Obligatorio) Codigo del indicador (ej: 1, 13, 2G).</li>",
    "                <li class=\"list-group-item\"><b>apetito</b>: (Opcional) Limite de apetito.</li>",
    "                <li class=\"list-group-item\"><b>tolerancia</b>: (Opcional) Limite de tolerancia.</li>",
    "                <li class=\"list-group-item\"><b>capacidad</b>: (Opcional) Limite de capacidad.</li>",
    "                <li class=\"list-group-item\"><b>valor_override</b>: (Opcional) Valor manual para anular el ultimo valor calculado del indicador. <strong>Requiere `valor_override_mes`.</strong></li>",
    "                <li class=\"list-group-item\"><b>valor_override_mes</b>: (Opcional) Mes para aplicar el valor manual (formato MES-AA, ej: OCT-23). Se aplicara `valor_override` solo para ese mes.</li>",
    "            </ul>",
    "            <p class=\"card-text mt-3\">",
    "                El sistema actualizara unicamente los campos presentes para cada <b>indicador_codigo</b>. Las celdas vacias se ignoran y <b>valor_override</b> solo aplica cuando <b>valor_override_mes</b> coincide con el mes de los datos.",
    "            </p>",
]
lines = lines[:start] + new_block + lines[end:]
path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
