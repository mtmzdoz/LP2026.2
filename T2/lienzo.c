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