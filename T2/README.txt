Nombre: Matilde Vásquez
Rol: 202473652-3
WSL: Ubuntu-24.04

Instrucciones
Antes de ejecutar, revisar  que exista una carpeta llamada "img" en el mismo directorio. En caso de no haber, crear una
Importante: Para que el comando SAVE funcione correctamente, debe existir una carpeta llamada "img" en el mismo directorio donde se encuentra el ejecutable. De lo contrario, los archivos .ppm no podran generarse

Consideraciones
  1. El programa lee "comandos.txt". Si se desea utilizar otro ".txt" solo se debe modificar la linea 18 del archivo main.c

  2. Para que main.h no fuera "inutil" se le agregaron las librerias principales para que funcionen

  3. En el makefile se agrego "rm -f img/*.ppm" que elimina los .ppm generados en la carpeta img, esto para dejar "limpio" cada vez que se hace make clean. En caso de que se ejecute un archivo y luego otro, el archivo .ppm se sobreescribira

  4. Se menciono en el foro que idealmente se trabajara con lo entrgado (no modificar parametros). Por lo que para los filtros EXPOS y ROTAR, se les hicieron funciones auxiliares para poder realizarlas.
  Se crearon porcentajeExposicion(int p) y dirRotacion(int der) dentro de filtros.c. Se hicieron para no modificar la firma obligatoria de los punteros a funcion. No era posible pasarle el porcentaje a filtro_expos, ni la direccion a filtro_rotar como un segundo parametro.
  Por lo que, estas funciones auxiliares actuan como puente. Desde el main.c, se llama a estas funciones auxiliares para guardar el argumento extra (el porcentaje de EXPOS o la dirección DER/IZQ de ROTAR) en variables globales static. Asi, cuando el motor invoca al filtro, este simplemente
  lee la variable estatica y aplica el efecto correcto sin romper lo pedido

  5. Si se ejecuta en la terminal  "make valgrind" se garantiza que el programa finaliza con 0 fugas de memoria (0 bytes in use at exit), liberando el tensor tridimensional en cascada de forma segura al usar EXIT, o al reasignar memoria en RESIZE, ROTAR o un NEW consecutivo

  6. Se decidio dejar todo el ciclo while que lee los comandos dentro de la funcion main, porque, lienzo.c se encarga de la memoria y filtros.c de las mates. Asi el unico trabajo de main.c es coordinar la lectura del archivo y ordenes

Manejo de casos bordes
  1. Ignora los comandos si se llaman antes de un NEW

  2. Si se intenta un NEW/RESIZE con dimensiones negativas o iguales a cero, se lanza un mensaje de dimensiones invalidas

  3. Ignora intentos de pintar (RED, GREEN, BLUE) o leer (INFO) coordenadas que están fuera de los limites del lienzo o son negativas
  
  4. Previene el desbordamiento de colores mayores a 255 truncandolos automaticamente debido al tipo unsigned char