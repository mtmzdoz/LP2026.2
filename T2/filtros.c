
#include "filtros.h"
#include "lienzo.h"

/*
***
Parametro 1: struct Lienzo*
***
None
***
Convierte la imagen a escala de grises truncando la formula de luminancia a entero.
*/
void filtro_gris(struct Lienzo *lienzo) {
    if (!lienzo || !lienzo->matriz) return;

    for (int y = 0; y < lienzo->h; y++) {
        for (int x = 0; x < lienzo->w; x++) {
            Pixel *pixel = lienzo->matriz[y][x];
            int gris = (int)((0.299 * pixel->r) + (0.587 * pixel->g) + (0.114 * pixel->b));
            pixel->r = gris;
            pixel->g = gris;
            pixel->b = gris;
        }
    }
}

/*
***
Parametro 1: struct Lienzo*
***
None
***
Voltea la imagen horizontalmente intercambiando los pixeles de cada fila.
*/
void filtro_espejo(struct Lienzo *l) {
    if (!l || !l->matriz) return;

    for (int y = 0; y < l->h; y++) {
        for (int x = 0; x < l->w / 2; x++) {
            Pixel *temp = l->matriz[y][x];
            l->matriz[y][x] = l->matriz[y][l->w - 1 - x];
            l->matriz[y][l->w - 1 - x] = temp;
        }
    }
}