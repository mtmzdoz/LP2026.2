joder



En el EBNF dado, el patron de jugador repetía el grupo de captura usando un asterisco *. El problema de esto es que, en 
Python cuando se repite un grupo de captura, este va sobrescribiendo la memoria cada vez que encuentra uno nuevo. 
Así que solo guardaba al último jugador de la lista y borraba a los demás. Por lo que agregue listaJugadores: que es el patron 
original de los jugadores y lo hice grupo de captura. Actualice presentacion_equipo con este nuevo patron al final del patrón en 
lugar de la regla individual.
Al poner paréntesis exterior, ya no esta la tarea de separar a los jugadores enseguida. En su lugar, quedo que guardara todos
los jugadores en un grupo(ej: "Messi, DePaul y Fernández") sin que Python borre a nadie. Y al tener los jugadores separados, se puede
ocupar el re.findall para sacar los nombres limpios de manera segura.


Nota sobre Jugadores Fantasmas en Tarjetas:
Para resolver la ambigüedad de palabras en mayúscula en los eventos de tarjeta (como "AMARILLA" o "Terrible"), el programa primero verifica las mayúsculas contra los jugadores en cancha. Si ningún jugador coincide (el infractor es un jugador fantasma), se consideró de forma determinista tomar la última palabra con mayúscula de la línea para generar el reporte de inconsistencia, de acuerdo a lo recomendado en el foro.