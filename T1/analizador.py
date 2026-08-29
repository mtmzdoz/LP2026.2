import re

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
minuto = rf"\[({digito}+)['’]\]"
tiempo_agregado = rf"\[MINUTOS EXTRA\] \+({digito}+)['’]"

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
inicio_partido = rf"\[0['’]\]{frase_variable}{jugador}"

# == Estructura Principal == #
relato_partido = rf"^{presentacion_equipo}{presentacion_equipo}{inicio_partido}(?:{evento_valido}|{minuto} {frase_variable})*$"

"""
***
Parametro 1 : nombre_archivo (String)
***
Tipo de retorno: Tupla (equipoJugadores: Diccionario, relato: Lista de strings)
***
Lee el archivo de texto, extrae las alineaciones iniciales para guardarlas en un diccionario y almacena el resto de las líneas en una lista, retornando ambas
"""
def leerArchivo(nombre_archivo):
    with open(nombre_archivo, "r", encoding="utf-8") as archivo:
        contenido = archivo.read().strip()
    lineas = contenido.split("\n")

    #Siempre en primera y segunda linea estaran las alineaciones
    alineaciones = lineas[0:2]
    equipoJugadores = {}
    
    #resto del relato
    relato = lineas[2:]

    for linea in alineaciones:
        matchAlineacion = re.match(rf"^{presentacion_equipo}$", linea)
        if matchAlineacion:
            equipo = matchAlineacion.group(1) 
            jugadores = matchAlineacion.group(2) #Se extraen todos los nombres de los jugadores (Messi, DePaul y Fernandez)
            nombreJugadores = re.findall(rf"{jugador}", jugadores) #Extraemos los nombres de los jugadores individual
            equipoJugadores[equipo] = nombreJugadores  #Diccionario x pais con los jugadores
    return equipoJugadores, relato

"""
***
Parametro 1 : equipoJugadores (Diccionario)
Parametro 2 : relato (Lista de strings)
***
Tipo de retorno: Tupla (inconsistencias: Lista, marcador: Diccionario, contadorFaltas: Diccionario, tarjetasAmarillas: Lista, tarjetasRojas: Lista, 
                tiempoPosesionPelota: Diccionario)
***
Analiza secuencialmente las lineas del relato para calcular el marcador, posesion, faltas, tarjetas y detectar errores, retornando todas las stats generadas
"""
def analizarRelato(equipoJugadores, relato):
    equipoConPelota = None #Para calcular stat de posesion 
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
   
    for linea in relato:

        #Inicio Partido
        matchInicio = re.match(rf"^{inicio_partido}$", linea)
    
        if matchInicio:
            #Se extrae al jugador que hace el saque inicial
            jugadorSaqueInicial = matchInicio.group(1)
            #Se busca a que equipo pertenece ese jugador en nuestro diccionario
            equipoPerteneciente = obtenerEquipo(jugadorSaqueInicial, equipoJugadores)

            #Jugador Fantasma
            jugadorValido = validarJugadoresFantasma([jugadorSaqueInicial], equipoJugadores, linea, inconsistencias)
            if not jugadorValido:
                continue#Saltamos la linea si el evento es invalido
            
            #Se actualiza partido
            ultimoMinuto = 0
            jugadorConPelota = jugadorSaqueInicial
            equipoConPelota = equipoPerteneciente
            continue

        #Pase
        matchPase = re.match(rf"^{evento_pase}$", linea)

        if matchPase:
            minActual = int(matchPase.group(1))
            jugadorPaseOrigen = matchPase.group(2)
            jugadorPaseDestino = matchPase.group(3)

            #tiempo correcto/Saltos temp
            tiempoValido = validarSaltoTemporal(minActual, ultimoMinuto, linea, inconsistencias)
            if not tiempoValido:
                continue

            #Jugador Fantasma
            jugadorValido = validarJugadoresFantasma([jugadorPaseOrigen, jugadorPaseDestino], equipoJugadores, linea, inconsistencias)
            if not jugadorValido:
                continue 
                
            if jugadorPaseOrigen != jugadorConPelota:
                inconsistencias.append(f"ERROR: Jugador Desconocido.\nLínea: \"{linea}\"\nMotivo: '{jugadorPaseOrigen}' no pertenece a ninguna alineación ni ha ingresado.\n")
                continue

            #Actualizamos el tiempo de posesion del equipo que tenia la pelota antes del pase
            tiempoPosesion(equipoConPelota, minActual, ultimoMinuto, tiempoPosesionPelota)

            ultimoMinuto = minActual
            jugadorConPelota = jugadorPaseDestino
            equipoConPelota = obtenerEquipo(jugadorPaseDestino, equipoJugadores)
            continue

        #Tiro
        matchTiro = re.match(rf"^{evento_tiro}$", linea)
        
        if matchTiro:
            minutoActual = int(matchTiro.group(1))
            jugadorTiro = matchTiro.group(2)
        
            tiempoValido = validarSaltoTemporal(minutoActual, ultimoMinuto, linea, inconsistencias)
            if not tiempoValido:
                continue
                        
            jugadorValido = validarJugadoresFantasma([jugadorTiro], equipoJugadores, linea, inconsistencias)
            if not jugadorValido:
                continue
        
            tiempoPosesion(equipoConPelota, minutoActual, ultimoMinuto, tiempoPosesionPelota)
            ultimoMinuto = minutoActual
            continue
        
        # Robo/Recuperacion 
        matchRobo = re.match(rf"^{evento_robo}$", linea)
        
        if matchRobo:
            minutoActual = int(matchRobo.group(1))
            jugadorRobo = matchRobo.group(2)
            
            tiempoValido = validarSaltoTemporal(minutoActual, ultimoMinuto, linea, inconsistencias)
            if not tiempoValido:
                continue
                
            jugadorValido = validarJugadoresFantasma([jugadorRobo], equipoJugadores, linea, inconsistencias)
            if not jugadorValido:
                continue

            tiempoPosesion(equipoConPelota, minutoActual, ultimoMinuto, tiempoPosesionPelota)

            ultimoMinuto = minutoActual
            jugadorConPelota = jugadorRobo 
            equipoConPelota = obtenerEquipo(jugadorRobo, equipoJugadores) 
            continue

        #Falta
        matchFalta = re.match(rf"^{evento_falta}$", linea)
        
        if matchFalta:
            minutoActual = int(matchFalta.group(1))
            jugadorInfractor = matchFalta.group(2)
            jugadorVictima = matchFalta.group(3)
        
            tiempoValido = validarSaltoTemporal(minutoActual, ultimoMinuto, linea, inconsistencias)
            if not tiempoValido:
                continue
                    
            equipoInfractor = obtenerEquipo(jugadorInfractor, equipoJugadores)
        
            jugadorValido = validarJugadoresFantasma([jugadorInfractor, jugadorVictima], equipoJugadores, linea, inconsistencias)
            if not jugadorValido:
                continue
                    
            #Si todo esta bien se suma la falta 
            contadorFaltas[equipoInfractor] += 1
            tiempoPosesion(equipoConPelota, minutoActual, ultimoMinuto, tiempoPosesionPelota)
            ultimoMinuto = minutoActual
            equipoConPelota = obtenerEquipo(jugadorVictima, equipoJugadores)
        
            #El jugador que le hicieron la falta se queda con la pelota
            jugadorConPelota = jugadorVictima
            continue

        #Tarjeta
        matchTarjeta = re.match(rf"^{evento_tarjeta}$", linea)

        if matchTarjeta:
            jugadorTarjeta = None
            equipoDelAmonestado = None 

            jugadorAAmonestar = re.findall(rf"{jugador}", linea)
            
            for palabra in jugadorAAmonestar:
                equipoPerteneciente = obtenerEquipo(palabra, equipoJugadores)
                if equipoPerteneciente is not None:
                        jugadorTarjeta = palabra
                        equipoDelAmonestado = equipoPerteneciente #Se guarda el equipo
                        break
                if equipoPerteneciente:
                    break

            #Si no esta en la alineacion ni ha ingresado
            if jugadorTarjeta is None:
                inconsistencias.append(f"ERROR: Jugador Desconocido.\nLínea: \"{linea}\"\nMotivo: El jugador mencionado no pertenece a ninguna alineación ni ha ingresado.\n")
                continue

            #Si encontramos un jugador
            if "TARJETA AMARILLA" in linea:
                tarjetasAmarillas.append((jugadorTarjeta, equipoDelAmonestado))
            elif "TARJETA ROJA" in linea:
                tarjetasRojas.append((jugadorTarjeta, equipoDelAmonestado))
                equipoJugadores[equipoDelAmonestado].remove(jugadorTarjeta) #expulsado
                continue

        #Cambio
        matchCambio = re.match(rf"^{evento_cambio}$", linea)
                
        if matchCambio:
            jugadorSale = None
            equipoCambio = None
                    
            #Vemos jugadores en cancha para buscar el que sale
            for equipo in equipoJugadores:
                for jugadorEnCancha in equipoJugadores[equipo]:
                    if jugadorEnCancha in linea: 
                        jugadorSale = jugadorEnCancha
                        equipoCambio = equipo
                        break
                if jugadorSale:
                    break #Si lo encontramos dejamos de buscar
                            
            #Si revisamos a todos los de la cancha y ninguno estaba en la linea
            if jugadorSale is None:
                inconsistencias.append(f"ERROR: Jugador Desconocido.\nLínea: \"{linea}\"\nMotivo: No se detectó a ningún jugador en cancha para salir.\n")
                continue
                        
            #Cortamos la linea justo después del jugador que sale
            lineaJugadorAEntrar = linea.split(jugadorSale)[1]
                    
            #El jugador que entra es la primera palabra con mayúscula 
            jugadorEntra = re.search(rf"{jugador}", lineaJugadorAEntrar)
                    
            if jugadorEntra:
                jugadorEntra = jugadorEntra.group(1)
                #Se hce el cambio en el diccionario
                equipoJugadores[equipoCambio].remove(jugadorSale)
                equipoJugadores[equipoCambio].append(jugadorEntra)
            continue
            
        #Gol
        matchGol = re.match(rf"^{evento_gol}$", linea)
        if matchGol:
            minutoActual = int(matchGol.group(1))
            jugadorGol = matchGol.group(2)
            equipoGol = matchGol.group(3)
            
            tiempoValido = validarSaltoTemporal(minutoActual, ultimoMinuto, linea, inconsistencias)
            if not tiempoValido:
                continue
                
            jugadorValido = validarJugadoresFantasma([jugadorGol], equipoJugadores, linea, inconsistencias)
            if not jugadorValido:
                continue
            
            if equipoGol in marcador:
                marcador[equipoGol] += 1
                
            tiempoPosesion(equipoConPelota, minutoActual, ultimoMinuto, tiempoPosesionPelota)
            ultimoMinuto = minutoActual

            #Cuando se hace gol el equipo que recibio el gol saca
            for equipo in equipoJugadores:
                if equipo != equipoGol:
                    #Se pasa la pelota al primer jugador del otro equipo
                    jugadorConPelota = equipoJugadores[equipo][0]
                    equipoConPelota = equipo
                    break
            continue

        #Minutos Extra 
        matchExtra = re.match(rf"^{tiempo_agregado}$", linea)

        if matchExtra:
            minutosExtra = int(matchExtra.group(1))
            continue

    minutosFinal = 90 + minutosExtra
    
    #Se suma los ultimos minutos del partido al jugador que se quedo con la pelota
    if minutosFinal > ultimoMinuto:
        tiempoPosesion(equipoConPelota, minutosFinal, ultimoMinuto, tiempoPosesionPelota)

    return inconsistencias, marcador, contadorFaltas, tarjetasAmarillas, tarjetasRojas, tiempoPosesionPelota

"""
***
Parametro 1 : nombreJugador (String)
Parametro 2 : equipoJugadores (Diccionario)
***
Tipo de retorno: String o None (El nombre del equipo, o none si no se encuentra)
***
Busca a un jugador en el diccionario de alineaciones y retorna el nombre de su equipo. Si el jugador no existe en cancha, retorna none
"""
def obtenerEquipo(nombreJugador, equipoJugadores):
    for equipo in equipoJugadores:
        if nombreJugador in equipoJugadores[equipo]:
            return equipo
    return None #Si no se encuentra el jugador en ninguna alineación

"""
***
Parametro 1 : jugadoresAEvaluar (Lista de strings)
Parametro 2 : equipoJugadores (Diccionario)
Parametro 3 : linea (String)
Parametro 4 : inconsistencias (Lista de strings)
***
Tipo de retorno: Booleano (true si todos existen, false si hay algún jugador desconocido)
***
Verifica si los jugadores se encuentran en cancha. Si alguno no existe, registra el error en la lista de inconsistencias y retorna false
"""
def validarJugadoresFantasma(jugadoresAEvaluar, equipoJugadores, linea, inconsistencias):
    for jugador in jugadoresAEvaluar:
        if obtenerEquipo(jugador, equipoJugadores) is None:
            error = f"ERROR: Jugador Desconocido.\nLínea: \"{linea}\"\nMotivo: '{jugador}' no pertenece a ninguna alineación ni ha ingresado.\n"
            inconsistencias.append(error)
            return False
    return True #Todos los jugadores son validos

"""
***
Parametro 1 : minutoActual (Entero)
Parametro 2 : ultimoMinuto (Entero)
Parametro 3 : linea (String)
Parametro 4 : inconsistencias (Lista de strings)
***
Tipo de retorno: Booleano (true si el tiempo avanza correctamente, false si hay un salto temporal)
***
Comprueba que el minuto del evento actual no sea menor al del ultimo evento registrado. Si hay un retroceso en el tiempo, guarda el error y retorna false
"""
def validarSaltoTemporal(minutoActual, ultimoMinuto, linea, inconsistencias):
    if minutoActual < ultimoMinuto:
        error = f"ERROR: Salto Temporal.\nLínea: \"{linea}\"\nMotivo: El minuto {minutoActual}' es inferior al último registrado'\n"
        inconsistencias.append(error)
        return False 
    return True #El tiempo es correcto

"""
***
Parametro 1 : equipoConPelota (String)
Parametro 2 : minutoActual (Entero)
Parametro 3 : ultimoMinuto (Entero)
Parametro 4 : tiempoPosesionPelota (Diccionario)
***
Tipo de retorno: None
***
Calcula la diferencia de minutos transcurridos y se los suma al acumulador de tiempo total de posesion del equipo que actualmente tiene la pelota
"""
def tiempoPosesion(equipoConPelota, minutoActual, ultimoMinuto, tiempoPosesionPelota):
    if equipoConPelota is not None:
        minutosPasados = minutoActual - ultimoMinuto
        tiempoPosesionPelota[equipoConPelota] += minutosPasados

"""
***
Parametro 1 : marcador (Diccionario)
Parametro 2 : posesion (Diccionario)
Parametro 3 : faltas (Diccionario)
Parametro 4 : tarjetasAmarillas (Lista de tuplas)
Parametro 5 : tarjetasRojas (Lista de tuplas)
Parametro 6 : errores (Lista de strings)
Parametro 7 : equipoJugadores (Diccionario)
***
Tipo de retorno: None
***
Imprime por consola el reporte final del partido con las estadisticas de posesion, el detalle de tarjetas y la cantidad de errores de transmision detectados
"""
def imprimirReporte(marcador, posesion, faltas, tarjetasAmarillas, tarjetasRojas, errores, equipoJugadores):
    equipos = []
    for equipo in marcador:
        equipos.append(equipo)
            
    equipo1 = equipos[0]
    equipo2 = equipos[1]
    
    print("\n=== REPORTE DEL PARTIDO ===")
    print(f"MARCADOR FINAL: {equipo1} {marcador[equipo1]} - {marcador[equipo2]} {equipo2}")
        
    print("ESTADISTICAS DE POSESION:")
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
    #Si las listas estan vacias
    if len(tarjetasAmarillas) == 0 and len(tarjetasRojas) == 0:
        print("* Ninguna tarjeta registrada.")
    else:
        for jugadorNombre, equipoJugador in tarjetasAmarillas:
            print(f"* {jugadorNombre} ({equipoJugador}): 1 Amarilla")
                
        for jugadorNombre, equipoJugador in tarjetasRojas:
                print(f"* {jugadorNombre} ({equipoJugador}): 1 Roja")
        
    print(f"\nERRORES DE TRANSMISION DETECTADOS: {len(errores)}")
    
    """
    print("\nJUGADORES QUE TERMINARON EN LA CANCHA:")
    for equipo in equipoJugadores:
        jugadoresActuales = ", ".join(equipoJugadores[equipo])
        print(f"* {equipo}: {jugadoresActuales}")
    """
    
equipoJugadores, relato = leerArchivo("relator.txt")
errores, marcador, faltas, tarjetasAmarillas, tarjetasRojas, posesion = analizarRelato(equipoJugadores, relato)
imprimirReporte(marcador, posesion, faltas, tarjetasAmarillas, tarjetasRojas, errores, equipoJugadores)
 
# Errores en el txt
archivoSalida = "inconsistencias.txt"
with open(archivoSalida, "w", encoding="utf-8") as salida:
    for error in errores:
        salida.write(error + "\n")
print(f"Archivo {archivoSalida} generado exitosamente \n")