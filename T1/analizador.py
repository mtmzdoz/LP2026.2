import re

#yo
signos = r'[¡!,\.\'’\-]'


# == Base 
digito = r'[0-9]'
letra_min = r'[a-záéíóúñ]'
letra_may = r'[A-ZÁÉÍÓÚÑ]'
letra = rf"(?:{letra_min}|{letra_may})"
palabra = rf"{letra}(?:{letra}|{digito})*"
frase_variable = rf"(?:{palabra}| |{signos})*"

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
evento_gol = rf"{minuto}{grito_gol}de {jugador} para {equipo}!"

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


"""
# Compilamos la expresión regular final
# Compilamos las expresiones regulares individuales que evaluaremos línea por línea
regex_alineacion = re.compile(rf"^{presentacion_equipo}$")
regex_inicio = re.compile(rf"^{inicio_partido}$")
regex_evento = re.compile(rf"^{evento_valido}$")

# --- EJEMPLO DE USO ---
lineas_prueba = [
    "[ALINEACION] El equipo LosTigres sale a la cancha con: Juan, Pedro y Luis",
    "[0’] Comienza sacando Juan",
    "[5’] Juan toca largo para Luis",
    "[10’] ¡Goooolazo de Luis para LosTigres!"
]

for linea in lineas_prueba:
    if regex_alineacion.match(linea):
        print(f"✓ ALINEACIÓN válida: {linea}")
    elif regex_inicio.match(linea):
        print(f"✓ INICIO válido: {linea}")
    elif regex_evento.match(linea):
        print(f"✓ EVENTO válido: {linea}")
    else:
        print(f"✗ INCONSISTENCIA detectada en: {linea}")
        """

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

def analizarRelato(relato):
    inconsistencias = []
    for linea in relato:
        if not re.match(rf"^{evento_valido}$", linea):
            inconsistencias.append(linea)
    return inconsistencias

equipoJugadores, relato = leerArchivo("relator.txt")
print(f"Alineaciones: {equipoJugadores}") #BORRAR
inconsistencias = analizarRelato(relato)
with open("inconcistencias.txt", "w", encoding="utf-8") as salida:
    for linea in relato:
        salida.write(linea)

""""
print("=== REPORTE DEL PARTIDO ===")
print("MARCADOR FINAL:")
for equipo, goles in marcador.items():
    print(f"{equipo} {goles}")
"""