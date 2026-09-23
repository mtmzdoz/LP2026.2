#ifndef LIENZO_H
#define LIENZO_H


typedef struct {
    unsigned char r; // Canal Rojo (0-255)
    unsigned char g; // Canal Verde (0-255)
    unsigned char b; // Canal Azul (0-255)
} Pixel;

typedef struct Lienzo {
    int w, h;
    Pixel ***matriz; /* matriz[y][x] apunta a un Pixel* en el heap */
    //yo
    int exposicion;
    int rotacion;
} Lienzo;

/* Es completamente imperativo que la matriz sea un triple puntero */
struct Lienzo* lienzo_crear(int ancho, int alto);
struct Lienzo* lienzo_redimensionar(struct Lienzo *l, int n_ancho, int n_alto);
void lienzo_liberar(struct Lienzo *l); /* debe limpiar toda la cascada del heap */
void exportar_ppm(struct Lienzo *l, int contador_img); /* para el SAVE */

#endif