def calcular_ctas_tarjetasCredito_rotativos(cupos_tarjetas_rotativos, tasa_cupos_rotativos):
    try:
        cupostarjetas = float(cupos_tarjetas_rotativos) if cupos_tarjetas_rotativos else 0
        print("entrada cupos_tarjetas: ", cupostarjetas)
        tasa = float(tasa_cupos_rotativos) if tasa_cupos_rotativos else 0
        tasa_procentaje = tasa/100
        print("tasa: ", tasa)

        print((cupostarjetas * (tasa_procentaje/12)))
        total = ((cupostarjetas/36) + (cupostarjetas * (tasa_procentaje/12)))
        print("total_cuotas tarjetas credito: ", total)

        return round(total, 2)

    except ValueError:
        print("Error al convertir los valores a nÃºmeros.")
        return 0

print(calcular_ctas_tarjetasCredito_rotativos(26300000, 0.224828))
