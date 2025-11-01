from django.conf import settings
import oracledb
import logging
from datetime import datetime, date, timedelta
import calendar
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_POST


logger = logging.getLogger(__name__)

#? ----------------------------------------------------------------
#?                ABSTRACCION DE LA LÓGICA DE ORACLE
#? -----------------------------------------------------------------
def ejecutar_procedimiento(procedimiento, parametros=[]):
    """
    Función base para ejecutar todos los procedmientos y no repetir código.
    Tengo que validar que todos devuelvan un cursor como último parametro.
    """
    try:
        db= settings.DATABASES['oracle'] # Configurar la base
        dsn = f"{db['HOST']}:{db['PORT']}/{db['NAME']}" # Construir el DSN

        with oracledb.connect(user=db['USER'], password=db['PASSWORD'], dsn=dsn) as conn: # Cerrar automáticamente la conexión.
            with conn.cursor() as cursor:   # Cerrar atumáticamente la conexión.
                ref_cursor_out = cursor.var(oracledb.CURSOR)    # Obtener el resultado del cursor devuelto por el SP.
                parametros_completos = parametros + [ref_cursor_out]    # Agregar el cursor de salida

                cursor.callproc(procedimiento, parametros_completos)    # Ejecutar el procedimiento ('Nombre del procedimiento" , [param1, param2, ..., cursor_out])
                cur = ref_cursor_out.getvalue()  # Obtener el cursor devuelto

                if cur:
                    cols = [c[0] for c in cur.description]
                    return [dict(zip(cols, row)) for row in cur]
                
                return []
            
    except Exception as e:
        logger.error(f"Error en ejecutar_procedimiento {procedimiento}: {e}", exc_info=True)
        raise
#? ----------------------     CONEXION A ORACLE   ------------------------------------

def gestion_diaria(agencia=0):
    """SP_INDICADORES_GERENCIA"""
    return ejecutar_procedimiento('SP_INDICADORES_GERENCIA', [agencia])
