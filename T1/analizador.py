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
    equipoConPelota = None # Para calcular stat de posesión 
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
            print(f"Minuto actual: {minActual}") #BORRAR para ver si efectivamente captura el minuto
            print(f"Jugador que pasa: {jugadorPaseOrigen}") #BORRAR para ver si efectivamente captura el nombre del jugador
            print(f"Jugador que recibe: {jugadorPaseDestino}") #BORRAR para
            
            # A. Validación: Salto Temporal BORRAR
            tiempoValido = validarSaltoTemporal(minActual, ultimoMinuto, linea, inconsistencias)
            if not tiempoValido:
                continue

            # B. Validación: Jugador Desconocido
            jugadorValido = validarJugadoresFantasma([jugadorPaseOrigen, jugadorPaseDestino], equipoJugadores, linea, inconsistencias)
            if not jugadorValido:
                continue # Saltamos la línea si algún jugador es fantasma
                
            # C. Validación: ¿El jugador origen tiene el balón?
            if jugadorPaseOrigen != jugadorConPelota:
                inconsistencias.append(f"ERROR: Jugador Desconocido.\nLínea: '{linea}'\nMotivo: '{jugadorPaseOrigen}' no pertenece a ninguna alineación ni ha ingresado.\n")
                continue

            #Actualizamos el tiempo de posesión del equipo que tenía la pelota antes del pase
            tiempoPosesion(equipoConPelota, minActual, ultimoMinuto, tiempoPosesionPelota)

            # Si todo está bien, actualizamos el estado
            ultimoMinuto = minActual
            jugadorConPelota = jugadorPaseDestino
            equipoConPelota = obtenerEquipo(jugadorPaseDestino, equipoJugadores)
            continue

        # Robo/Recuperacion 
        matchRobo = re.match(rf"^{evento_robo}$", linea)
        
        if matchRobo:
            minutoActual = int(matchRobo.group(1))
            jugadorRobo = matchRobo.group(2)
            print(f"Minuto actual: {minutoActual}") #BORRAR para ver si efectivamente captura el minuto
            print(f"Jugador que roba: {jugadorRobo}") #BORRAR para ver
            
            # A. Validación: Salto Temporal BORRAR
            tiempoValido = validarSaltoTemporal(minutoActual, ultimoMinuto, linea, inconsistencias)
            if not tiempoValido:
                continue
                
            # B. Validación: Jugador Desconocido BORRAR
            jugadorValido = validarJugadoresFantasma([jugadorRobo], equipoJugadores, linea, inconsistencias)
            if not jugadorValido:
                continue

            tiempoPosesion(equipoConPelota, minutoActual, ultimoMinuto, tiempoPosesionPelota)

            #Si todo está bien, actualizamos el estado BORRAR
            ultimoMinuto = minutoActual
            jugadorConPelota = jugadorRobo 
            equipoConPelota = obtenerEquipo(jugadorRobo, equipoJugadores) 
            continue

        #Cambio
        matchCambio = re.match(rf"^{evento_cambio}$", linea)
        
        if matchCambio:
            jugadorSale = None
            equipoCambio = None
            print(f"Match cambio: {matchCambio}") #BORRAR para ver si efectivamente le hizo match a la linea de cambio  
            
            #Vemos jugadores en cancha para buscar el que sale
            for equipo in equipoJugadores:
                print(f"Jugadores en cancha del equipo {equipo}: {equipoJugadores[equipo]}") #BORRAR para ver si efectivamente captura los jugadores en cancha
                for jugadorEnCancha in equipoJugadores[equipo]:
                    if jugadorEnCancha in linea: #Vemos si el nombre del jugador está escrito en la línea
                        jugadorSale = jugadorEnCancha
                        equipoCambio = equipo
                        print(f"Equipo que hace cambio de jugador: {equipoCambio}") #BORRAR para ver si efectivamente captura el nombre del equipo
                        print(f"Jugador que sale: {jugadorSale}") #BORRAR para ver si
                        break
                if jugadorSale:
                    break # Si lo encontramos dejamos de buscar
                    
            # Si revisamos a todos los de la cancha y ninguno estaba en la línea:
            if jugadorSale is None:
                inconsistencias.append(f"ERROR: Jugador Desconocido.\nLínea: '{linea}'\nMotivo: No se detectó a ningún jugador en cancha para salir.\n")
                continue
                
            #Cortamos la línea justo después del jugador que sale
            lineaJugadorAEntrar = linea.split(jugadorSale)[1]
            print(f"Línea después del jugador que sale: {lineaJugadorAEntrar}") #BORRAR para ver si efectivamente corta la línea
            
            # 3. El que ENTRA es la primera palabra con mayúscula en esa parte final
            jugadorEntra = re.search(rf"{jugador}", lineaJugadorAEntrar)
            print(f"Jugador que entra: {jugadorEntra}") #BORRAR para ver si efectivamente captura el nombre del jugador que entra
            
            if jugadorEntra:
                jugadorEntra = jugadorEntra.group(1)
                print(f"Jugador que entra (después de group): {jugadorEntra}") #BORRAR para ver si efectivamente captura el nombre del jugador que entra
                #Se hce el cambio en el diccionario
                equipoJugadores[equipoCambio].remove(jugadorSale)
                equipoJugadores[equipoCambio].append(jugadorEntra)
            continue

        #Tarjeta
        matchTarjeta = re.match(rf"^{evento_tarjeta}$", linea)

        if matchTarjeta:
            jugadorTarjeta = None
            equipoDelAmonestado = None 
            # 1. Buscamos TODAS las palabras que parezcan nombres en esta línea BORRAR
            jugadorAAmonestar = re.findall(rf"{jugador}", linea)
            print(f"Jugador en línea de tarjeta: {jugadorAAmonestar}") #BORRAR para ver si efectivamente captura los posibles jugadores
            
            # 2. Revisamos cuál de esas palabras existe en nuestras listas Borrar
            for palabra in jugadorAAmonestar:
                print(f"Jugador en línea de tarjeta: {palabra}") #BORRAR para ver si efectivamente captura los posibles jugadores
                equipoPerteneciente = obtenerEquipo(palabra, equipoJugadores)
                print(f"Equipo al que pertenece el jugador: {equipoPerteneciente}") #BORRAR para ver si efectivamente captura el equipo del posible jugador
                if equipoPerteneciente is not None:
                        jugadorTarjeta = palabra
                        equipoDelAmonestado = equipoPerteneciente # Guardamos el equipo
                        break
                if equipoPerteneciente:
                    break

            #Si no esta en la alineacion ni ha ingresado
            if jugadorTarjeta is None:
                inconsistencias.append(f"ERROR: Jugador Desconocido.\nLínea: '{linea}'\nMotivo: El jugador mencionado no pertenece a ninguna alineación ni ha ingresado.\n")
                continue

            #Si encontramos un jugador
            if "TARJETA AMARILLA" in linea:
                tarjetasAmarillas.append((jugadorTarjeta, equipoDelAmonestado))
            elif "TARJETA ROJA" in linea:
                tarjetasRojas.append((jugadorTarjeta, equipoDelAmonestado))
                equipoJugadores[equipoDelAmonestado].remove(jugadorTarjeta) #expulsado
                continue

        #Tiro
        matchTiro = re.match(rf"^{evento_tiro}$", linea)

        if matchTiro:
            minutoActual = int(matchTiro.group(1))
            jugadorTiro = matchTiro.group(2)

            # A. Validación: Salto Temporal BORRAR
            tiempoValido = validarSaltoTemporal(minutoActual, ultimoMinuto, linea, inconsistencias)
            if not tiempoValido:
                continue
                
            # B. Validación: Jugador Fantasma BORRAR
            jugadorValido = validarJugadoresFantasma([jugadorTiro], equipoJugadores, linea, inconsistencias)
            if not jugadorValido:
                continue

            tiempoPosesion(equipoConPelota, minutoActual, ultimoMinuto, tiempoPosesionPelota)
            ultimoMinuto = minutoActual
            continue

        #Falta
        matchFalta = re.match(rf"^{evento_falta}$", linea)

        if matchFalta:
            minutoActual = int(matchFalta.group(1))
            jugadorInfractor = matchFalta.group(2)
            jugadorVictima = matchFalta.group(3)

            # A. Validación: Salto Temporal
            tiempoValido = validarSaltoTemporal(minutoActual, ultimoMinuto, linea, inconsistencias)
            if not tiempoValido:
                continue
            
            # B. Validación: Jugador Fantasma BORRAR
            equipoInfractor = obtenerEquipo(jugadorInfractor, equipoJugadores)

            jugadorValido = validarJugadoresFantasma([jugadorInfractor, jugadorVictima], equipoJugadores, linea, inconsistencias)
            if not jugadorValido:
                continue
            
            # Si todo está bien, SUMAMOS LA FALTA BORRAR
            contadorFaltas[equipoInfractor] += 1
            tiempoPosesion(equipoConPelota, minutoActual, ultimoMinuto, tiempoPosesionPelota)
            ultimoMinuto = minutoActual
            equipoConPelota = obtenerEquipo(jugadorVictima, equipoJugadores)

            #El jugador que le hicieron la falta se queda con la pelota
            jugadorConPelota = jugadorVictima
            continue
            
        #Gol
        matchGol = re.match(rf"^{evento_gol}$", linea)
        print(f"Match gol: {matchGol}") #BORRAR para ver si efectivamente le hizo match a la linea de gol BOrrar
        if matchGol:
            minutoActual = int(matchGol.group(1))
            jugadorGol = matchGol.group(2)
            equipoGol = matchGol.group(3)
            print(f"Minuto actual: {minutoActual}") #BORRAR para ver si efectivamente captura el minuto
            print(f"Jugador que hace el gol: {jugadorGol}") #BORRAR para ver si efectivamente captura el nombre del jugador
            print(f"Equipo que hace el gol: {equipoGol}") #BORRAR para
            
            # A. Validación: Salto Temporal BORRAR
            tiempoValido = validarSaltoTemporal(minutoActual, ultimoMinuto, linea, inconsistencias)
            if not tiempoValido:
                continue
                
            # B. Validación: Jugador Fantasma BORRAR
            jugadorValido = validarJugadoresFantasma([jugadorGol], equipoJugadores, linea, inconsistencias)
            if not jugadorValido:
                continue
            
            # Si todo está bien, SUMAMOS EL GOL BORRAR
            if equipoGol in marcador:
                marcador[equipoGol] += 1
                
            tiempoPosesion(equipoConPelota, minutoActual, ultimoMinuto, tiempoPosesionPelota)
            ultimoMinuto = minutoActual

            #Cuando se hace gol: El equipo que recibio el gol saca
            for equipo in equipoJugadores:
                if equipo != equipoGol:
                    # Le damos la pelota al primer jugador del otro equipo
                    jugadorConPelota = equipoJugadores[equipo][0]
                    equipoConPelota = equipo
                    break
            continue

        #Minutos Extra 
        matchExtra = re.match(rf"^{tiempo_agregado}$", linea)
        if matchExtra:
            minutosExtra = int(matchExtra.group(1))
            print(f"Minutos extra detectados: {minutosExtra}") #BORRAR para ver si efectivamente captura los minutos extra
            continue

    minutosFinal = 90 + minutosExtra
    
    # Le sumamos los últimos minutos del partido al jugador que se quedó con el balón
    if minutosFinal > ultimoMinuto:
        tiempoPosesion(equipoConPelota, minutosFinal, ultimoMinuto, tiempoPosesionPelota)

    return inconsistencias, marcador, contadorFaltas, tarjetasAmarillas, tarjetasRojas, tiempoPosesionPelota

def obtenerEquipo(nombreJugador, equipoJugadores):
    """Busca a un jugador en el diccionario y retorna el nombre de su equipo. Si no existe, retorna None."""
    for equipo in equipoJugadores:
        if nombreJugador in equipoJugadores[equipo]:
            return equipo
    return None

def validarJugadoresFantasma(jugadoresAEvaluar, equipoJugadores, linea, inconsistencias):
    """
    Revisa una lista de jugadores. Si alguno no está en cancha, 
    registra el error y retorna False. Si todos existen, retorna True.
    """
    for jugador in jugadoresAEvaluar:
        if obtenerEquipo(jugador, equipoJugadores) is None:
            error = f"ERROR: Jugador Desconocido.\nLínea: '{linea}'\nMotivo: '{jugador}' no pertenece a ninguna alineación ni ha ingresado.\n"
            inconsistencias.append(error)
            return False # Encontramos un fantasma, la validación falla
            
    return True # Todos los jugadores son reales

def validarSaltoTemporal(minutoActual, ultimoMinuto, linea, inconsistencias):
    """
    Verifica si el minuto actual es menor al último minuto registrado.
    Si es así, registra el error y retorna False. Si el tiempo está bien, retorna True.
    """
    if minutoActual < ultimoMinuto:
        error = f"ERROR: Salto Temporal.\nLínea: '{linea}'\nMotivo: El minuto {minutoActual}' es inferior al último registrado ({ultimoMinuto}').\n"
        inconsistencias.append(error)
        return False # Hay un salto en el tiempo, validación falla
    return True # El tiempo es correcto

def tiempoPosesion(equipoConPelota, minutoActual, ultimoMinuto, tiempoPosesionPelota):
    """Suma los minutos transcurridos al equipo que tiene la pelota."""
    if equipoConPelota is not None:
        minutosPasados = minutoActual - ultimoMinuto
        tiempoPosesionPelota[equipoConPelota] += minutosPasados

def imprimirReporte(marcador, posesion, faltas, tarjetasAmarillas, tarjetasRojas, errores, equipoJugadores):
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
    tiempoTotalPartido = 0
    for equipo in posesion:
        tiempoTotalPartido += posesion[equipo]
            
    if tiempoTotalPartido > 0:
        for equipo in posesion:
            minutos = posesion[equipo]
            porcentaje = (minutos / tiempoTotalPartido) * 100
            print(f"- {equipo}: {porcentaje:.1f}% ({minutos} minutos)")
                
        print(f"*(Cálculo basado en un total de {tiempoTotalPartido} minutos)*")
    else:
        print("- No hubo tiempo de posesión válido.")
            
    print("\nESTADISTICAS DISCIPLINARIAS:")
    print("- Faltas cometidas:")
    for equipo in faltas:
        cantidadFaltas = faltas[equipo]
        print(f"* {equipo}: {cantidadFaltas}")
    
         
    print("- Tarjetas:")
    # Verificamos manualmente si las listas están vacías
    if len(tarjetasAmarillas) == 0 and len(tarjetasRojas) == 0:
        print("* Ninguna tarjeta registrada.")
    else:
        for jugadorNombre, equipoJugador in tarjetasAmarillas:
            print(f"* {jugadorNombre} ({equipoJugador}): 1 Amarilla")
                
        for jugadorNombre, equipoJugador in tarjetasRojas:
                print(f"* {jugadorNombre} ({equipoJugador}): 1 Roja")
    
                
    print(f"\nERRORES DE TRANSMISION DETECTADOS: {len(errores)}")
    
    
    print("\nJUGADORES QUE TERMINARON EN LA CANCHA:")
    for equipo in equipoJugadores:
        # Unimos la lista de jugadores separándolos por comas
        jugadoresActuales = ", ".join(equipoJugadores[equipo])
        print(f"* {equipo}: {jugadoresActuales}")
    


tiempo_inicio = time.time() #BORRAR
    
equipoJugadores, relato = leerArchivo("relator5.txt")
errores, marcador, faltas, tarjetasAmarillas, tarjetasRojas, posesion = analizarRelato(equipoJugadores, relato)
imprimirReporte(marcador, posesion, faltas, tarjetasAmarillas, tarjetasRojas, errores, equipoJugadores)
tiempo_fin = time.time() #Borrar
print(f"Tiempo de ejecución: {tiempo_fin - tiempo_inicio:.4f} segundos") #Borrar
    
# Errores en el txt
archivoSalida = "inconsistencias.txt"
with open(archivoSalida, "w", encoding="utf-8") as salida:
    for error in errores:
        salida.write(error + "\n")
print(f"Archivo {archivoSalida} generado exitosamente \n")