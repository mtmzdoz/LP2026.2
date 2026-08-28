Nombre: Matilde Vásquez
Rol: 202473652-3
Rut: 21.715.078-7
Version Python: 3.10.11


Supuestos y consideraciones 
1. Modificaciones EBNF. Foro "Modificacion de eBNF"
    En el EBNF dado, el patron de <presentacion_equipo> repetía el grupo de captura jugador usando un asterisco *. El problema de esto es que en 
    Python, cuando se repite un grupo de captura, este va sobrescribiendo la memoria cada vez que encuentra uno nuevo. 
    Así que solo guardaba al último jugador de la lista y borraba a los demás. Por lo que agregue <listaJugadores>: que es el patron 
    original de los jugadores y lo hice grupo de captura. Actualice <presentacion_equipo> con este nuevo patron al final de este en 
    lugar de la regla individual.
    Al poner paréntesis exterior, ya no esta la tarea de separar a los jugadores enseguida. En su lugar, quedo que guardara todos
    los jugadores en un grupo(ej: "Messi, DePaul y Fernández") sin que Python borre a nadie. Y al tener los jugadores separados, se puede
    ocupar el re.findall para sacar los nombres limpios de manera segura.

    Además, no se ocuparon los patrones de palabra y relato_partido, palabra debido a que tenia un doble * al estar en <frase_variable> y demoraba
    el tiempo de ejecucion, y relato partido porque law validación en el código se implementó iterando línea por línea

2. Formato de nombres. Foro "Consulta Equipos". 
    Los nombres compuestos de paises o jugadores (ej: Corea del Sur) vendran escritos en formato CamelCase (ej: CoreaDelSur)
    Esto fue confirmado por Bastian para mantener la compatibilidad con el EBNF. Además en la duda "Consulta nombre jugador" se 
    menciona que "no existirán nombres con "-", espacios o símbolos que no se encuentren en el patrón de "letra" que aparece en el EBNF"

3. Deteccion del Jugador que entra en un [CAMBIO]. Foro "Consultas cortas consideraciones Tarea"
    En la linea de [CAMBIO], no habra palabras con mayuscula inicial entre el nombre del jugador que SALE y el nombre del jugador que
    ENTRA (ej: el relator diria "y entra Arias", no "y Entra Arias"). Bastian confirmo que "se evitaran mayuscula para evitar ambiguedades", 
    ya que el jugador que entra aún no esta registrado. Así que esto nos permite usar re.search para capturar con seguridad la primera mayusucla 
    despues del jugador que sale

4. Tarjetas a "Jugadores Fantasma". Foro "Duda evento_tarjeta y jugadores fantasma"
    Para resolver la ambigüedad de palabras en mayúscula en los eventos de tarjeta (como "AMARILLA" o "Terrible"), el programa primero verifica las 
    mayúsculas contra los jugadores en cancha. En el caso de que ningun jugador coincida se supuso que lo que importa es identificar el error. Si en 
    una linea de [TARJETA] no se detecta a ningun jugador valido en cancha (que este en la alineacion o entre como cambio), se registre el error con
    un mensaje generico ("El jugador mencionado no pertenece a ninguna alineación ni ha ingresado") en lugar de intentar adivinar su nombre/apellido. 
    Como <frase_variable> permite que el relator diga palabras como "Area", "Falta" o "Tremenda" con mayusculas, el mensaje generico evita que se "acuse" 
    a una palabra de ser un jugador fantasma. Bastian dijo "Se reporta error de jugador desconocido y sea lo que sea que se encuentre, al final lo que importa }
    es el error, si se hace una línea de tarjeta y no hay jugador al cual darle la tarjeta, corresponde a un error"
    
5. Reglas de Posesión (faltas y goles). Foro "error con contabilizacion de tiempo"
    Cuando ocurre una falta, la victima de la infraccion cobra el tiro libre y se queda con la posesion de la pelota.
    Cuando ocurre un gol, el equipo que recibe el gol se queda con la posesion de la pelota, por lo que su primer jugador 
    en la lista asume la posesion. Se aplican esas reglas reales del futbol para mantener el calculo de la posesion.
    "los únicos dos casos de "posesión indirecta" por así decirlo es el gol y la falta"

6. Tarjetas Rojas = Expulsion Real. Foro "Conteo amarrillas por terminal"
    Bastian dijo "Solo la roja es expulsión, podría pasar el caso de que existan 3 líneas continuas de amarilla, amarilla, 
    roja, pero la doble amarilla no implica roja directa ni expulsión"
