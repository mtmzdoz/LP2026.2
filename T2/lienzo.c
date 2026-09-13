#include <stdlib.h>
#include "lienzo.h"

/*
***
Parametro 1: int
Parametro 2: int
***
struct Lienzo*
***
Inicializa un nuevo tensor 3D reservando memoria en cascada para la matriz de punteros.
*/
struct Lienzo* lienzo_crear(int ancho, int alto) {
    struct Lienzo *lienzo = (struct Lienzo*)malloc(sizeof(struct Lienzo));
    lienzo->w = ancho;
    lienzo->h = alto;

    lienzo->matriz = (Pixel***)malloc(alto * sizeof(Pixel**));
    for (int y = 0; y < alto; y++) {
        lienzo->matriz[y] = (Pixel**)malloc(ancho * sizeof(Pixel*));
        for (int x = 0; x < ancho; x++) {
            lienzo->matriz[y][x] = (Pixel*)malloc(sizeof(Pixel));
            lienzo->matriz[y][x]->r = 0; // Inicializar en blanco temporalmente
            lienzo->matriz[y][x]->g = 0;
            lienzo->matriz[y][x]->b = 0;
        }
    }
    return lienzo;
}



/*
***
Parametro 1: struct Lienzo*
***
None
***
Libera toda la memoria alojada en cascada para el lienzo y sus pixeles.
*/
void lienzo_liberar(struct Lienzo *lienzo) {
    if (lienzo == NULL) return;

    for (int y = 0; y < lienzo->h; y++) {
        for (int x = 0; x < lienzo->w; x++) {
            free(lienzo->matriz[y][x]); // Libera cada Pixel individual
        }
        free(lienzo->matriz[y]); // Libera la fila (arreglo de punteros a Pixel)
    }
    free(lienzo->matriz); // Libera la matriz principal (arreglo de filas)
    free(lienzo); // Libera la estructura del lienzo
}

#include <stdio.h> // Necesario para FILE, fopen, fprintf, sprintf

/*
***
Parametro 1: struct Lienzo*
Parametro 2: int
***
None
***
Exporta el lienzo actual a un archivo PPM en texto plano (P3) dentro de la carpeta /img.
*/
void exportar_ppm(struct Lienzo *l, int contador_img) {
    if (!l || !l->matriz) return;

    char ruta[64];
    // Formatea la ruta para que sea img/img_00x.ppm
    sprintf(ruta, "img/img_%03d.ppm", contador_img);

    FILE *archivo = fopen(ruta, "w");
    if (archivo == NULL) {
        printf("Error: No se pudo crear el archivo %s. ¿Creaste la carpeta 'img'?\n", ruta);
        return;
    }

    // 1. Escribir la cabecera estricta
    fprintf(archivo, "P3\n");
    fprintf(archivo, "%d %d\n", l->w, l->h);
    fprintf(archivo, "255\n");

    // 2. Recorrer la matriz de izquierda a derecha y de arriba hacia abajo
    for (int y = 0; y < l->h; y++) {
        for (int x = 0; x < l->w; x++) {
            Pixel *p = l->matriz[y][x];
            fprintf(archivo, "%d %d %d ", p->r, p->g, p->b);
        }
        fprintf(archivo, "\n"); // Salto de línea al terminar cada fila del lienzo
    }

    fclose(archivo);
    printf("[PhotoChop] Imagen guardada en /img/img_%03d.ppm.\n", contador_img);
}