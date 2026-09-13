Nombre: Matilde Vásquez
Rol: 202473652-3
WSL: Ubuntu-24.04

Las 3 consideraciones obligatorias para tu README:

    La advertencia de la carpeta img/ (¡La más importante!): En C, la función fopen puede crear archivos, pero no puede crear carpetas. Si el ayudante ejecuta tu programa y no existe una carpeta llamada img en el mismo directorio, el comando SAVE fallará silenciosamente. Debes advertirle que cree la carpeta antes de correr el programa.

    Cómo cambiar el archivo de prueba: Como refactorizaste tu código de forma profesional creando la variable const char *nombreArchivo = "comandos.txt"; al inicio del main, dile al ayudante que si quiere probar su propio archivo del terror, solo debe cambiar ese nombre ahí.

    Tu blindaje contra errores (Saca a relucir tu buen código): Menciona brevemente que tu programa maneja casos bordes. Esto predispone al ayudante a ponerte una buena nota porque sabe que pensaste en los detalles.


================================================================
PROYECTO: PhotoChop - Procesador de Imágenes en C
ALUMNO: [Tu Nombre / Tu RUT o Matrícula]
CURSO: [Nombre del curso]
================================================================

1. DESCRIPCIÓN
Este programa implementa un procesador de imágenes por lotes leyendo instrucciones desde un archivo de texto. Utiliza gestión de memoria dinámica en 3D (tensores) y un motor basado en arreglos de punteros a funciones para aplicar filtros. Valgrind certifica 0 fugas de memoria (0 memory leaks).

2. CÓMO COMPILAR Y EJECUTAR
- Para compilar el proyecto, abre la terminal en este directorio y ejecuta:
  make

- Para ejecutar el programa:
  ./PhotoChop

3. ⚠️ CONSIDERACIÓN CRÍTICA (CARPETA DE SALIDA)
Para que el comando SAVE funcione correctamente, DEBE existir una carpeta llamada "img" en el mismo directorio donde se encuentra el ejecutable. De lo contrario, los archivos .ppm no podrán generarse.

4. CÓMO PROBAR OTROS ARCHIVOS DE TEXTO
Por defecto, el programa lee "comandos.txt". Si el ayudante desea utilizar su propio archivo de pruebas, debe modificar la línea 18 del archivo main.c:
const char *nombreArchivo = "nuevo_archivo.txt"; 
Luego, compilar nuevamente con "make" o "make rebuild".

5. MANEJO DE ERRORES Y CASOS BORDE INCLUIDOS
El programa está protegido contra fallos comunes (Segmentation Faults):
- Ignora comandos si se llaman antes de un "NEW".
- Bloquea intentos de NEW o RESIZE con dimensiones negativas o iguales a cero.
- Ignora intentos de pintar (RED, GREEN, BLUE) o leer (INFO) coordenadas que están fuera de los límites del lienzo o son negativas.
- Previene el desbordamiento de colores mayores a 255 truncándolos automáticamente gracias al tipo unsigned char.