import re
import time  #BORRAR

#yo
signos = r'[¡!,\.\'’\-\?¿"“”]'

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
relato_partido = rf"^{presentacion_equipo}{presentacion_equipo}{inicio_partido}(?:{evento_valido}|{minuto} {frase_variable})*$"


def leerArchivo(nombre_archivo):
    with open(nombre_archivo, "r", encoding="utf-8") as archivo:
        contenido = archivo.read().strip()
    lineas = contenido.split("\n")

    #Siempre en primera y segunda linea estarán las alineaciones
    alineaciones = lineas[0:2]
    equipoJugadores = {}
    print(f"Alineaciones: {alineaciones}") #BORRAR para ver si captura la linea de alineaciones 
    #resto del relato
    relato = lineas[2:]

    for linea in alineaciones:
        matchAlineacion = re.match(rf"^{presentacion_equipo}$", linea)
        if matchAlineacion:
            print(f"Match alineacion: {matchAlineacion}") #BORRAR para ver si efectivamente le hizo match a la linea de alineacion
            equipo = matchAlineacion.group(1) #primero el equipo
            print(f"Equipo: {equipo}") #BORRAR para ver si captura el nombre del equipo
            
            jugadores = matchAlineacion.group(2) #se extraen todos los nombres de los jugadores (Messi, DePaul y Fernández)
            nombreJugadores = re.findall(rf"{jugador}", jugadores) #Extraemos los nombres de los jugadores individual
            equipoJugadores[equipo] = nombreJugadores  # Diccionario x pais con los jugadores
        print(f"EquipoJugadores: {equipoJugadores}") #BORRAR para ver si efectivamente se guardo en el diccionario
    
    return equipoJugadores, relato

def analizarRelato(equipoJugadores, relato):
    equipoConPelota = None # Para calcular la posesión 
    jugadorConPelota = None 
    inconsistencias = []
    tarjetasAmarillas = []
    tarjetasRojas = []
    minutosExtra = 0 
    ultimoMinuto = -1
    
    #Diccionarios por equipo para los contadores
    marcador = {}
    contadorFaltas = {}
    tiempoPosesionPelota = {}
    
    #Inicializar diccionarios 
    for equipo in equipoJugadores:
        marcador[equipo] = 0
        contadorFaltas[equipo] = 0
        tiempoPosesionPelota[equipo] = 0
    print(f"Marcador inicial: {marcador}") #BORRAR para ver si efectivamente se guardo en el diccionario
    print(f"Contador de faltas inicial: {contadorFaltas}") #BORRAR para ver si efectivamente se guardo en el diccionario
    print(f"Tiempo de posesion inicial: {tiempoPosesionPelota}") #BORRAR para ver si efectivamente se guardo en el diccionario

    for linea in relato:
        #Inicio Partido
        matchInicio = re.match(rf"^{inicio_partido}$", linea)
        #print(f"Match inicio: {matchInicio}") #BORRAR para ver si efectivamente le hizo match a la linea de inicio
        if matchInicio:
            #Extraemos al jugador que hace el saque inicial
            jugadorSaqueInicial = matchInicio.group(1)
            print(f"Jugador que hace el saque inicial: {jugadorSaqueInicial}") #BORRAR para ver si efectivamente captura el nombre del jugador
            #Buscamos a qué equipo pertenece ese jugador en nuestro diccionario
            equipoPerteneciente = obtenerEquipo(jugadorSaqueInicial, equipoJugadores)
            print(f"Equipo al que pertenece el jugador: {equipoPerteneciente}") #BORRAR para ver si efectivamente captura el nombre del equipo
            #Jugador Fantasma
            jugadorValido = validarJugadoresFantasma([jugadorSaqueInicial], equipoJugadores, linea, inconsistencias)
            if not jugadorValido:
                continue#Saltamos la línea si el evento es inválido
            
            #Si todo bien actualizamos el estado del partido
            ultimoMinuto = 0
            jugadorConPelota = jugadorSaqueInicial
            equipoConPelota = equipoPerteneciente
            continue #Siguiente línea del relato


        #Pase
        matchPase = re.match(rf"^{evento_pase}$", linea)

        if matchPase:
            minActual = int(matchPase.group(1))
            jugadorPaseOrigen = matchPase.group(2)
            jugadorPaseDestino = matchPase.group(3)
            
            # A. Validación: Salto Temporal
            if minActual < ultimoMinuto:
                inconsistencias.append(f"ERROR: Salto Temporal.\nLínea: '{linea}'\nMotivo: El minuto {minActual}' es inferior al último registrado ({ultimoMinuto}').\n")
                continue
                
            # B. Validación: ¿El jugador origen tiene el balón?
            if jugadorPaseOrigen != jugadorConPelota:
                inconsistencias.append(f"ERROR: Jugador Desconocido.\nLínea: '{linea}'\nMotivo: '{jugadorPaseOrigen}' no pertenece a ninguna alineación ni ha ingresado.\n")
                continue

            # C. Validación: ¿Existen los jugadores? (Revisamos ambos)
            jugadorValido = validarJugadoresFantasma([jugadorPaseOrigen, jugadorPaseDestino], equipoJugadores, linea, inconsistencias)
            if not jugadorValido:
                continue # Saltamos la línea si algún jugador es fantasma

            tiempoPosesion(equipoConPelota, minActual, ultimoMinuto, tiempoPosesionPelota)

            # Si todo está bien, actualizamos el estado
            ultimoMinuto = minActual
            jugadorConPelota = jugadorPaseDestino # ¡El balón cambió de dueño!
            equipoConPelota = obtenerEquipo(jugadorPaseDestino, equipoJugadores) # NUEVO
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
            jugadorValido = validarJugadoresFantasma([jugador_robo], equipoJugadores, linea, inconsistencias)
            if not jugadorValido:
                continue

            tiempoPosesion(equipoConPelota, min_actual, ultimoMinuto, tiempoPosesionPelota)
            # Si todo está bien, actualizamos el estado
            ultimoMinuto = min_actual
            jugadorConPelota = jugador_robo # ¡Ahora este jugador tiene el control!
            equipoConPelota = obtenerEquipo(jugador_robo, equipoJugadores) # NUEVO
            continue
        # --- 4. ¿ES UN CAMBIO? ---
        matchCambio = re.match(rf"^{evento_cambio}$", linea)
        
        if matchCambio:
            jugador_sale = None
            equipo_cambio = None
            
            # 1. TU IDEA: Usamos a los jugadores en cancha para buscar quién sale
            for equipo in equipoJugadores:
                for j_cancha in equipoJugadores[equipo]:
                    # Verificamos si el nombre del jugador está escrito en la línea
                    if j_cancha in linea:
                        jugador_sale = j_cancha
                        equipo_cambio = equipo
                        break
                if jugador_sale:
                    break # Si ya lo encontramos, dejamos de buscar
                    
            # Si revisamos a todos los de la cancha y ninguno estaba en la línea:
            if jugador_sale is None:
                inconsistencias.append(f"ERROR: Jugador Desconocido.\nLínea: '{linea}'\nMotivo: No se detectó a ningún jugador en cancha para salir.\n")
                continue
                
            # 2. Cortamos la línea justo después del jugador que sale
            # Ej: "[CAMBIO] Sale Bravo y entra Arias" se parte y nos quedamos con " y entra Arias"
            parte_final_linea = linea.split(jugador_sale)[1]
            
            # 3. El que ENTRA es la primera palabra con mayúscula en esa parte final
            match_entra = re.search(rf"{jugador}", parte_final_linea)
            
            if match_entra:
                jugador_entra = match_entra.group(1)
                
                # 4. Hacemos el cambio en el diccionario
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
                equipoPerteneciente = obtenerEquipo(palabra, equipoJugadores)
                if equipoPerteneciente is not None:
                        jugador_tarjeta = palabra
                        equipo_del_amonestado = equipoPerteneciente # Guardamos el equipo
                        break
                if equipoPerteneciente:
                    break
            
            # 3. Si revisamos todas y ninguna era un jugador:
            if jugador_tarjeta is None:
                # Siguiendo el consejo del profesor: tomamos la última mayúscula capturada
                # como el supuesto jugador fantasma.
                if len(posibles_jugadores) > 0:
                    supuesto_fantasma = posibles_jugadores[-1]
                else:
                    supuesto_fantasma = "Desconocido"
                    
                inconsistencias.append(f"ERROR: Jugador Desconocido.\nLínea: '{linea}'\nMotivo: '{supuesto_fantasma}' no pertenece a ninguna alineación ni ha ingresado.\n")
                continue

            # 4. Si encontramos al jugador real, le damos su tarjeta
            if "TARJETA AMARILLA" in linea:
                tarjetasAmarillas.append((jugador_tarjeta, equipo_del_amonestado))
            elif "TARJETA ROJA" in linea:
                tarjetasRojas.append((jugador_tarjeta, equipo_del_amonestado))
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
            jugadorValido = validarJugadoresFantasma([jugador_tiro], equipoJugadores, linea, inconsistencias)
            if not jugadorValido:
                continue

            tiempoPosesion(equipoConPelota, min_actual, ultimoMinuto, tiempoPosesionPelota)
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
            equipo_del_infractor = obtenerEquipo(jugador_infractor, equipoJugadores)

            jugadorValido = validarJugadoresFantasma([jugador_infractor, jugador_victima], equipoJugadores, linea, inconsistencias)
            if not jugadorValido:
                continue
            
            if not jugadores_validos:
                continue
                
            # Si todo está bien, SUMAMOS LA FALTA
            contadorFaltas[equipo_del_infractor] += 1
            tiempoPosesion(equipoConPelota, min_actual, ultimoMinuto, tiempoPosesionPelota)
            ultimoMinuto = min_actual
            equipoConPelota = obtenerEquipo(jugador_victima, equipoJugadores)

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
            jugadorValido = validarJugadoresFantasma([jugador_gol], equipoJugadores, linea, inconsistencias)
            if not jugadorValido:
                continue
            
            # Si todo está bien, SUMAMOS EL GOL
            if equipo_gol in marcador:
                marcador[equipo_gol] += 1
                
            tiempoPosesion(equipoConPelota, min_actual, ultimoMinuto, tiempoPosesionPelota)
            ultimoMinuto = min_actual

            # REGLA DE FÚTBOL: El equipo que recibió el gol saca del medio.
            for equipo in equipoJugadores:
                if equipo != equipo_gol:
                    # Le damos la pelota al primer jugador del otro equipo
                    jugadorConPelota = equipoJugadores[equipo][0]
                    equipoConPelota = equipo
                    break

            continue

        # --- 9. ¿SON MINUTOS EXTRA? ---
        matchExtra = re.match(rf"^{tiempo_agregado}$", linea)
        if matchExtra:
            minutosExtra = int(matchExtra.group(1))
            continue

    minuto_final = 90 + minutosExtra
    
    # Le sumamos los últimos minutos del partido al jugador que se quedó con el balón
    if minuto_final > ultimoMinuto:
        tiempoPosesion(equipoConPelota, minuto_final, ultimoMinuto, tiempoPosesionPelota)

    return inconsistencias, marcador, contadorFaltas, tarjetasAmarillas, tarjetasRojas, tiempoPosesionPelota

def obtenerEquipo(nombre_jugador, equipoJugadores):
    """Busca a un jugador en el diccionario y retorna el nombre de su equipo. Si no existe, retorna None."""
    for equipo in equipoJugadores:
        if nombre_jugador in equipoJugadores[equipo]:
            return equipo
    return None

def validarJugadoresFantasma(jugadores_evaluar, equipoJugadores, linea, inconsistencias):
    """
    Revisa una lista de jugadores. Si alguno no está en cancha, 
    registra el error y retorna False. Si todos existen, retorna True.
    """
    for jugador in jugadores_evaluar:
        if obtenerEquipo(jugador, equipoJugadores) is None:
            error = f"ERROR: Jugador Desconocido.\nLínea: '{linea}'\nMotivo: '{jugador}' no pertenece a ninguna alineación ni ha ingresado.\n"
            inconsistencias.append(error)
            return False # Encontramos un fantasma, la validación falla
            
    return True # Todos los jugadores son reales

def tiempoPosesion(equipoConPelota, min_actual, ultimoMinuto, tiempoPosesionPelota):
    """Suma los minutos transcurridos al equipo que tiene la pelota."""
    if equipoConPelota is not None:
        minutos_pasados = min_actual - ultimoMinuto
        tiempoPosesionPelota[equipoConPelota] += minutos_pasados



# --- EJEMPLO DE USO COMPLETO ---
if __name__ == "__main__":
    
    tiempo_inicio = time.time()
    
    equipoJugadores, relato = leerArchivo("relatorfin.txt")
    errores, marcador, faltas, tarjetasAmarillas, tarjetasRojas, posesion = analizarRelato(equipoJugadores, relato)
    
    tiempo_fin = time.time()
    
    # --- 1. IMPRIMIR MARCADOR FINAL (Lógica básica) ---
    # Llenamos una lista con los nombres de los equipos usando un for normal
    equipos = []
    for equipo in marcador:
        equipos.append(equipo)
        
    equipo1 = equipos[0]
    equipo2 = equipos[1]

    print("\n=== REPORTE DEL PARTIDO ===")
    print(f"MARCADOR FINAL: {equipo1} {marcador[equipo1]} - {marcador[equipo2]} {equipo2}")
    
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
        
    print("ESTADISTICAS DISCIPLINARIAS:")
    print("- Faltas cometidas:")
    for equipo in faltas:
        cant_faltas = faltas[equipo]
        print(f"* {equipo}: {cant_faltas}")

     
    print("- Tarjetas:")
    # Verificamos manualmente si las listas están vacías
    if len(tarjetasAmarillas) == 0 and len(tarjetasRojas) == 0:
        print("* Ninguna tarjeta registrada.")
    else:
        for jugador_nombre, equipo_jugador in tarjetasAmarillas:
            print(f"* {jugador_nombre} ({equipo_jugador}): 1 Amarilla")
            
        for jugador_nombre, equipo_jugador in tarjetasRojas:
            print(f"* {jugador_nombre} ({equipo_jugador}): 1 Roja")

            
    print(f"ERRORES DE TRANSMISION DETECTADOS: {len(errores)}")

    # --- 5. IMPRIMIR JUGADORES EN CANCHA ---
    print("\nJUGADORES QUE TERMINARON EN LA CANCHA:")
    for equipo in equipoJugadores:
        # Unimos la lista de jugadores separándolos por comas
        jugadores_actuales = ", ".join(equipoJugadores[equipo])
        print(f"* {equipo}: {jugadores_actuales}")

    # Errores en el txt
    with open("inconsistencias.txt", "w", encoding="utf-8") as salida:
        for error in errores:
            salida.write(error + "\n")
    print("Archivo 'inconsistencias.txt' generado exitosamente.")