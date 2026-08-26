import re
import time  #BORRAR

#yo
signos = r'[¡!,\.\'’\-]'


# == Base 
digito = r'[0-9]'
letra_min = r'[a-záéíóúñ]'
letra_may = r'[A-ZÁÉÍÓÚÑ]'
letra = rf"(?:{letra_min}|{letra_may})"
palabra = rf"{letra}(?:{letra}|{digito})*"
frase_variable = rf"(?:{letra}|{digito}| |{signos})*?"

# == Entidades del Juego y Tiempo == #
jugador = rf"({letra_may}{letra}+)"
equipo = rf"({letra_may}{letra}+)"
minuto = rf"\[({digito}+)’\]"
tiempo_agregado = rf"\[MINUTOS EXTRA\] \+({digito}+)’"

#yo
listaJugadores = rf"({jugador}(?:(?:, | y ){jugador})*)"

# == Acciones de Relato == #
accion_pase = rf"{frase_variable}(?:pase|toca){frase_variable}"
accion_tiro = rf"{frase_variable}(?:dispara|remata|patea){frase_variable}"
accion_robo = rf"{frase_variable}(?:roba|recupera|domina){frase_variable}"
accion_falta = rf"{frase_variable}(?:entrada|falta|derriba){frase_variable}"
grito_gol = rf"{frase_variable}(?:G|g)o+l(?:azo)?{frase_variable}"

# == Estructura de Eventos Válidos == #
# Los espacios explícitos (" ") de tu EBNF se colocan tal cual BORRAR
evento_pase = rf"{minuto} {jugador}{accion_pase}{jugador}"
evento_tiro = rf"{minuto} {jugador}{accion_tiro}"
evento_robo = rf"{minuto} {jugador}{accion_robo}"
evento_falta = rf"{minuto} {jugador}{accion_falta}{jugador}"
evento_gol = rf"{minuto}{grito_gol} de {jugador} para {equipo}!"

# == Tarjetas y Cambios == #
evento_tarjeta = rf"\[(?:TARJETA AMARILLA|TARJETA ROJA)\]{frase_variable}{jugador}{frase_variable}"
evento_cambio = rf"\[CAMBIO\]{frase_variable}{jugador}{frase_variable}{jugador}{frase_variable}"
evento_valido = rf"(?:{evento_pase}|{evento_tiro}|{evento_robo}|{evento_falta}|{evento_gol}|{evento_tarjeta}|{evento_cambio}|{tiempo_agregado})"

# == Eventos de Inicio y Cierre == #
presentacion_equipo = rf"\[ALINEACION\] El equipo {equipo} sale a la cancha con: {listaJugadores}"
inicio_partido = rf"\[0’\]{frase_variable}{jugador}"

# == Estructura Principal == #
# Añadimos ^ al principio y $ al final para asegurar que valide TODO el texto desde el inicio hasta el fin. BORRAR
relato_partido = rf"^{presentacion_equipo}{presentacion_equipo}{inicio_partido}(?:{evento_valido}|{minuto} {frase_variable})*$"


def leerArchivo(nombre_archivo):
    with open(nombre_archivo, "r", encoding="utf-8") as archivo:
        contenido = archivo.read().strip()
    lineas = contenido.split("\n")

    #Siempre en primera y segunda linea estarán las alineaciones
    alineaciones = lineas[0:2]
    equipoJugadores = {}
    print(f"Alineaciones: {alineaciones}") #BORRAR
    #resto del relato
    relato = lineas[2:]

    for linea in alineaciones:
        matchAlineacion = re.match(rf"^{presentacion_equipo}$", linea)
        if matchAlineacion:
            print(f"Match alineacion: {matchAlineacion}") #BORRAR
            equipo = matchAlineacion.group(1) #primero el equipo
        
        # Extraemos todos los nombres (ej: "Messi, DePaul y Fernández")
            jugadores = matchAlineacion.group(2) 
            nombreJugadores = re.findall(rf"{jugador}", jugadores) #Extraemos los nombres de los jugadores
        # Metemos la lista limpia al diccionario
            equipoJugadores[equipo] = nombreJugadores
    
    return equipoJugadores, relato

def analizarRelato(equipoJugadores, relato):
    # Variables de estado
    ultimoMinuto = -1
    jugadorConPelota = None # Vital para calcular la posesión luego
    inconsistencias = []
    tarjetas_amarillas = []
    tarjetas_rojas = []
    minutos_extra = 0 
    
    # 2. Creamos los diccionarios vacíos para los contadores
    marcador = {}
    contador_faltas = {}
    tiempoPosesionPelota = {}
    
    # 3. Llenamos los diccionarios con un 0 inicial usando el ciclo clásico
    for equipo in equipoJugadores:
        marcador[equipo] = 0
        contador_faltas[equipo] = 0
        tiempoPosesionPelota[equipo] = 0

    for linea in relato:
        
        # --- 1. ¿ES EL INICIO DEL PARTIDO? ---
        matchInicio = re.match(rf"^{inicio_partido}$", linea)
        
        if matchInicio:
            # Extraemos al jugador que hace el saque inicial
            jugadorSaqueInicial = matchInicio.group(1)
            
            # Buscamos a qué equipo pertenece ese jugador en nuestro diccionario
            equipoPerteneciente = None
            for equipo, listaJugadores in equipoJugadores.items():
                if jugadorSaqueInicial in listaJugadores:
                    equipoPerteneciente = equipo
                    break # Lo encontramos, dejamos de buscar
            
            # VALIDACIÓN: Jugador Fantasma
            if equipoPerteneciente is None:
                error = f"ERROR: Jugador Desconocido.\nLínea: '{linea}'\nMotivo: '{jugadorSaqueInicial}' no pertenece a ninguna alineación ni ha ingresado."
                inconsistencias.append(error)
                continue # Saltamos la línea, este evento es inválido
            
            # Si todo está bien, actualizamos el estado del partido
            ultimoMinuto = 0
            jugadorConPelota = jugadorSaqueInicial
            continue # Pasamos a leer la siguiente línea del relato

        matchPase = re.match(rf"^{evento_pase}$", linea)
        
        if matchPase:
            min_actual = int(matchPase.group(1))
            jugador_origen = matchPase.group(2)
            jugador_destino = matchPase.group(3)
            
            # A. Validación: Salto Temporal
            if min_actual < ultimoMinuto:
                inconsistencias.append(f"ERROR: Salto Temporal.\nLínea: '{linea}'\nMotivo: El minuto {min_actual}' es inferior al último registrado ({ultimoMinuto}').\n")
                continue
                
            # B. Validación: ¿El jugador origen tiene el balón?
            if jugador_origen != jugadorConPelota:
                inconsistencias.append(f"ERROR: Jugador Desconocido.\nLínea: '{linea}'\nMotivo: '{jugador_origen}' no pertenece a ninguna alineación ni ha ingresado.\n")
                continue

            # C. Validación: ¿Existen los jugadores? (Revisamos ambos)
            jugadores_validos = True
            for jugador_evaluar in [jugador_origen, jugador_destino]:
                encontrado = False
                for listaJugadores in equipoJugadores.values():
                    if jugador_evaluar in listaJugadores:
                        encontrado = True
                        break
                if not encontrado:
                    inconsistencias.append(f"ERROR: Jugador Desconocido.\nLínea: '{linea}'\nMotivo: '{jugador_evaluar}' no pertenece a ninguna alineación ni ha ingresado.\n")
                    jugadores_validos = False
                    break # Salimos del ciclo de validación
            
            if not jugadores_validos:
                continue # Saltamos la línea si algún jugador es fantasma

            tiempoPosesion(jugadorConPelota, equipoJugadores, min_actual, ultimoMinuto, tiempoPosesionPelota)

            # Si todo está bien, actualizamos el estado
            ultimoMinuto = min_actual
            jugadorConPelota = jugador_destino # ¡El balón cambió de dueño!
            continue

        # --- 3. ¿ES UN ROBO/RECUPERACIÓN? ---
        matchRobo = re.match(rf"^{evento_robo}$", linea)
        
        if matchRobo:
            min_actual = int(matchRobo.group(1))
            jugador_robo = matchRobo.group(2)
            
            # A. Validación: Salto Temporal
            if min_actual < ultimoMinuto:
                inconsistencias.append(f"ERROR: Salto Temporal.\nLínea: '{linea}'\nMotivo: El minuto {min_actual}' es inferior al último registrado ({ultimoMinuto}').\n")
                continue
                
            # B. Validación: ¿El jugador existe?
            encontrado = False
            for listaJugadores in equipoJugadores.values():
                if jugador_robo in listaJugadores:
                    encontrado = True
                    break
                    
            if not encontrado:
                inconsistencias.append(f"ERROR: Jugador Desconocido.\nLínea: '{linea}'\nMotivo: '{jugador_robo}' no pertenece a ninguna alineación ni ha ingresado.\n")
                continue

            tiempoPosesion(jugadorConPelota, equipoJugadores, min_actual, ultimoMinuto, tiempoPosesionPelota)
            # Si todo está bien, actualizamos el estado
            ultimoMinuto = min_actual
            jugadorConPelota = jugador_robo # ¡Ahora este jugador tiene el control!
            continue
        # --- 4. ¿ES UN CAMBIO? ---
        matchCambio = re.match(rf"^{evento_cambio}$", linea)
        
        if matchCambio:
            jugador_sale = matchCambio.group(1)
            jugador_entra = matchCambio.group(2)
            
            # Buscamos de qué equipo es el que sale
            equipo_cambio = None
            for equipo, listaJugadores in equipoJugadores.items():
                if jugador_sale in listaJugadores:
                    equipo_cambio = equipo
                    break
            
            # Si el que sale no existe, es un error
            if equipo_cambio is None:
                inconsistencias.append(f"ERROR: Jugador Desconocido.\nLínea: '{linea}'\nMotivo: '{jugador_sale}' no puede salir porque no está en la cancha.\n")
                continue
                
            # Si todo está bien, hacemos la sustitución en tu diccionario
            equipoJugadores[equipo_cambio].remove(jugador_sale)
            equipoJugadores[equipo_cambio].append(jugador_entra)
            continue

        # --- 5. ¿ES UNA TARJETA? ---
        matchTarjeta = re.match(rf"^{evento_tarjeta}$", linea)
        if matchTarjeta:
            # 1. Buscamos TODAS las palabras que parezcan nombres en esta línea
            posibles_jugadores = re.findall(rf"{jugador}", linea)
            
            jugador_tarjeta = None
            equipo_del_amonestado = None # NUEVO: Guardamos de qué equipo es
            
            # 2. Revisamos cuál de esas palabras existe en nuestras listas
            for palabra in posibles_jugadores:
                encontrado = False
                for equipo in equipoJugadores:
                    if palabra in equipoJugadores[equipo]:
                        jugador_tarjeta = palabra
                        equipo_del_amonestado = equipo # Guardamos el equipo
                        encontrado = True
                        break
                if encontrado:
                    break
            
            # 3. Si revisamos todas y ninguna era un jugador:
            if jugador_tarjeta is None:
                inconsistencias.append(f"ERROR: Jugador Desconocido.\nLínea: '{linea}'\nMotivo: No se encontró ningún jugador válido en la línea.\n")
                continue

            # 4. Si encontramos al jugador real, le damos su tarjeta
            if "TARJETA AMARILLA" in linea:
                tarjetas_amarillas.append(jugador_tarjeta)
            elif "TARJETA ROJA" in linea:
                tarjetas_rojas.append(jugador_tarjeta)
                # ¡NUEVO: LO EXPULSAMOS DE LA CANCHA!
                equipoJugadores[equipo_del_amonestado].remove(jugador_tarjeta)
                
            continue

        # --- 6. ¿ES UN TIRO? ---
        matchTiro = re.match(rf"^{evento_tiro}$", linea)
        if matchTiro:
            min_actual = int(matchTiro.group(1))
            jugador_tiro = matchTiro.group(2)
            # A. Validación: Salto Temporal
            if min_actual < ultimoMinuto:
                inconsistencias.append(f"ERROR: Salto Temporal.\nLínea: '{linea}'\nMotivo: El minuto {min_actual}' es inferior al último registrado ({ultimoMinuto}').\n")
                continue
                
            # B. Validación: ¿El jugador existe?
            encontrado = False
            for listaJugadores in equipoJugadores.values():
                if jugador_tiro in listaJugadores:
                    encontrado = True
                    break
            
            if not encontrado:
                inconsistencias.append(f"ERROR: Jugador Desconocido.\nLínea: '{linea}'\nMotivo: '{jugador_tiro}' no pertenece a ninguna alineación ni ha ingresado.\n")
                continue

            tiempoPosesion(jugadorConPelota, equipoJugadores, min_actual, ultimoMinuto, tiempoPosesionPelota)
            ultimoMinuto = min_actual
            continue

        # --- 7. ¿ES UNA FALTA? ---
        matchFalta = re.match(rf"^{evento_falta}$", linea)
        if matchFalta:
            min_actual = int(matchFalta.group(1))
            jugador_infractor = matchFalta.group(2)
            jugador_victima = matchFalta.group(3)

            # A. Validación: Salto Temporal
            if min_actual < ultimoMinuto:
                inconsistencias.append(f"ERROR: Salto Temporal.\nLínea: '{linea}'\nMotivo: El minuto {min_actual}' es inferior al último registrado ({ultimoMinuto}').\n")
                continue
            
            # B. Validación: ¿Existen los jugadores?
            jugadores_validos = True
            equipo_del_infractor = None 
            
            for jugador_evaluar in [jugador_infractor, jugador_victima]:
                encontrado = False
                for equipo, listaJugadores in equipoJugadores.items():
                    if jugador_evaluar in listaJugadores:
                        encontrado = True
                        if jugador_evaluar == jugador_infractor:
                            equipo_del_infractor = equipo
                        break
                if not encontrado:
                    inconsistencias.append(f"ERROR: Jugador Desconocido.\nLínea: '{linea}'\nMotivo: '{jugador_evaluar}' no pertenece a ninguna alineación ni ha ingresado.\n")
                    jugadores_validos = False
                    break
            
            if not jugadores_validos:
                continue
                
            # Si todo está bien, SUMAMOS LA FALTA
            contador_faltas[equipo_del_infractor] += 1
            tiempoPosesion(jugadorConPelota, equipoJugadores, min_actual, ultimoMinuto, tiempoPosesionPelota)
            ultimoMinuto = min_actual

            # REGLA DE FÚTBOL: La víctima cobra la falta y se queda con el balón
            jugadorConPelota = jugador_victima
            continue
            
        # --- 8. ¿ES UN GOL? ---
        matchGol = re.match(rf"^{evento_gol}$", linea)
        if matchGol:
            min_actual = int(matchGol.group(1))
            jugador_gol = matchGol.group(2)
            equipo_gol = matchGol.group(3)
            
            # A. Validación: Salto Temporal
            if min_actual < ultimoMinuto:
                inconsistencias.append(f"ERROR: Salto Temporal.\nLínea: '{linea}'\nMotivo: El minuto {min_actual}' es inferior al último registrado ({ultimoMinuto}').\n")
                continue
                
            # B. Validación: ¿El jugador existe?
            encontrado = False
            for listaJugadores in equipoJugadores.values():
                if jugador_gol in listaJugadores:
                    encontrado = True
                    break
            
            if not encontrado:
                inconsistencias.append(f"ERROR: Jugador Desconocido.\nLínea: '{linea}'\nMotivo: '{jugador_gol}' no pertenece a ninguna alineación ni ha ingresado.\n")
                continue
            
            # Si todo está bien, SUMAMOS EL GOL
            if equipo_gol in marcador:
                marcador[equipo_gol] += 1
                
            tiempoPosesion(jugadorConPelota, equipoJugadores, min_actual, ultimoMinuto, tiempoPosesionPelota)
            ultimoMinuto = min_actual

            # REGLA DE FÚTBOL: El equipo que recibió el gol saca del medio.
            for equipo in equipoJugadores:
                if equipo != equipo_gol:
                    # Le damos la pelota al primer jugador del otro equipo
                    jugadorConPelota = equipoJugadores[equipo][0]
                    break

            continue

        # --- 9. ¿SON MINUTOS EXTRA? ---
        matchExtra = re.match(rf"^{tiempo_agregado}$", linea)
        if matchExtra:
            minutos_extra = int(matchExtra.group(1))
            continue

    minuto_final = 90 + minutos_extra
    
    # Le sumamos los últimos minutos del partido al jugador que se quedó con el balón
    if minuto_final > ultimoMinuto:
        tiempoPosesion(jugadorConPelota, equipoJugadores, minuto_final, ultimoMinuto, tiempoPosesionPelota)

    return inconsistencias, marcador, contador_faltas, tarjetas_amarillas, tarjetas_rojas, tiempoPosesionPelota


def tiempoPosesion(jugadorConPelota, equipoJugadores, min_actual, ultimoMinuto, tiempoPosesionPelota):
    """Suma los minutos transcurridos al equipo que tiene la pelota."""
    if jugadorConPelota is not None:
        equipo_del_poseedor = None
        
        # Buscamos a qué equipo pertenece (usando el for clásico que te gustó)
        for equipo in equipoJugadores:
            if jugadorConPelota in equipoJugadores[equipo]:
                equipo_del_poseedor = equipo
                break
        
        if equipo_del_poseedor is not None:
            minutos_pasados = min_actual - ultimoMinuto
            tiempoPosesionPelota[equipo_del_poseedor] += minutos_pasados
# --- EJEMPLO DE USO COMPLETO ---
if __name__ == "__main__":
    
    tiempo_inicio = time.time()
    
    equipoJugadores, relato = leerArchivo("relator3.txt")
    errores, marcador, faltas, t_amarillas, t_rojas, posesion = analizarRelato(equipoJugadores, relato)
    
    tiempo_fin = time.time()
    
    # --- 1. IMPRIMIR MARCADOR FINAL (Lógica básica) ---
    # Llenamos una lista con los nombres de los equipos usando un for normal
    equipos = []
    for equipo in marcador:
        equipos.append(equipo)
        
    equipo1 = equipos[0]
    equipo2 = equipos[1]
    
    print(f"MARCADOR FINAL: {equipo1} {marcador[equipo1]} - {marcador[equipo2]} {equipo2}")
    
    # --- 2. IMPRIMIR POSESIÓN (Lógica básica) ---
    print("ESTADISTICAS DE POSESION:")
    
    # Sumamos el tiempo manualmente
    tiempo_total_juego = 0
    for equipo in posesion:
        tiempo_total_juego += posesion[equipo]
        
    if tiempo_total_juego > 0:
        for equipo in posesion:
            minutos = posesion[equipo]
            porcentaje = (minutos / tiempo_total_juego) * 100
            print(f"- {equipo}: {porcentaje:.1f}% ({minutos} minutos)")
            
        print(f"*(Cálculo basado en un total de {tiempo_total_juego} minutos)*")
    else:
        print("- No hubo tiempo de posesión válido.")
        
    # --- 3. IMPRIMIR FALTAS Y TARJETAS (Lógica básica) ---
    print("ESTADISTICAS DISCIPLINARIAS:")
    print("- Faltas cometidas:")
    for equipo in faltas:
        cant_faltas = faltas[equipo]
        print(f"* {equipo}: {cant_faltas}")
        
    print("- Tarjetas:")
    
    # Verificamos manualmente si las listas están vacías
    if len(t_amarillas) == 0 and len(t_rojas) == 0:
        print("* Ninguna tarjeta registrada.")
    else:
        # Función auxiliar súper tradicional
        def buscar_equipo_jugador(nombre_jugador):
            for equipo in equipoJugadores:
                jugadores_del_equipo = equipoJugadores[equipo]
                if nombre_jugador in jugadores_del_equipo:
                    return equipo
            return "Desconocido"

        # Imprimimos las amarillas
        for jugador in t_amarillas:
            equipo_jugador = buscar_equipo_jugador(jugador)
            print(f"* {jugador} ({equipo_jugador}): 1 Amarilla")
            
        # Imprimimos las rojas
        for jugador in t_rojas:
            equipo_jugador = buscar_equipo_jugador(jugador)
            print(f"* {jugador} ({equipo_jugador}): 1 Roja")

            
    # --- 4. ERRORES ---
    print(f"ERRORES DE TRANSMISION DETECTADOS: {len(errores)}")

    # --- 5. IMPRIMIR JUGADORES EN CANCHA ---
    print("\nJUGADORES QUE TERMINARON EN LA CANCHA:")
    for equipo in equipoJugadores:
        # Unimos la lista de jugadores separándolos por comas
        jugadores_actuales = ", ".join(equipoJugadores[equipo])
        print(f"* {equipo}: {jugadores_actuales}")

    # Escribimos los errores en el txt
    with open("inconsistencias.txt", "w", encoding="utf-8") as salida:
        for error in errores:
            salida.write(error + "\n")
    print("Archivo 'inconsistencias.txt' generado exitosamente.")