    #include <stdlib.h>
    #include "filtros.h"
    #include "lienzo.h"

    /*
    ***
    Parametro 1: struct Lienzo* (puntero al lienzo)
    ***
    Retorno: None
    ***
    Convierte la imagen a escala de grises truncando la formula de luminancia a entero
    */
    void filtro_gris(struct Lienzo *lienzo){
        if (!lienzo || !lienzo->matriz){
            return;
        }

        for (int y = 0; y < lienzo->h; y++){
            for (int x = 0; x < lienzo->w; x++){
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
    Parametro 1: struct Lienzo* (puntero al lienzo)
    ***
    Retorno: None
    ***
    Aplica efecto negativo calculando 255 menos el valor original
    */
    void filtro_invertir(struct Lienzo *l){
        if (!l || !l->matriz){
            return;
        }

        for (int y = 0; y < l->h; y++){
            for (int x = 0; x < l->w; x++){
                Pixel *pixel = l->matriz[y][x];
                pixel->r = 255 - pixel->r;
                pixel->g = 255 - pixel->g;
                pixel->b = 255 - pixel->b;
            }
        }
    }

    /*
    ***
    Parametro 1: struct Lienzo* (puntero al lienzo)
    ***
    Retorno: None
    ***
    Ajusta la exposicion aplicando clamping en 255
    */
    void filtro_expos(struct Lienzo *l){
        if (!l || !l->matriz){
            return;
        } 

        for (int y = 0; y < l->h; y++){
            for (int x = 0; x < l->w; x++){
                Pixel *pixel = l->matriz[y][x];
                int r = (pixel->r * l->exposicion) / 100;
                int g = (pixel->g * l->exposicion) / 100;
                int b = (pixel->b * l->exposicion) / 100;

                pixel->r = (r > 255) ? 255 : r;
                pixel->g = (g > 255) ? 255 : g;
                pixel->b = (b > 255) ? 255 : b;
            }
        }
    }

    /*
    ***
    Parametro 1: struct Lienzo* (puntero al lienzo)
    ***
    Retorno: None
    ***
    Voltea la imagen horizontalmente intercambiando los pixeles de cada fila
    */
    void filtro_espejo(struct Lienzo *l){
        if (!l || !l->matriz){
            return;
        } 

        for (int y = 0; y < l->h; y++){
            for (int x = 0; x < l->w / 2; x++){
                Pixel *temp = l->matriz[y][x];
                l->matriz[y][x] = l->matriz[y][l->w - 1 - x];
                l->matriz[y][l->w - 1 - x] = temp;
            }
        }
    }

    /*
    ***
    Parametro 1: struct Lienzo* (puntero al lienzo)
    ***
    Retorno: None
    ***
    Rota 90 grados, invierte dimensiones, guarda nuevo lienzo y libera el antiguo
    */
    void filtro_rotar(struct Lienzo *l){
        if (!l || !l->matriz){
            return;
        }

        int nuevoAncho = l->h;
        int nuevoAlto = l->w;

        Pixel ***nuevaMatriz = (Pixel***)malloc(nuevoAlto * sizeof(Pixel**));
        for (int y = 0; y < nuevoAlto; y++){
            nuevaMatriz[y] = (Pixel**)malloc(nuevoAncho * sizeof(Pixel*));
            for (int x = 0; x < nuevoAncho; x++){
                nuevaMatriz[y][x] = (Pixel*)malloc(sizeof(Pixel));

                int xAntiguo;
                int yAntiguo;
                if (l->rotacion){ // si es 1 en el main es derecha
                    yAntiguo = l->h - 1 - x;
                    xAntiguo = y;
                }else{
                    yAntiguo = x; //si es 0 es izquierda
                    xAntiguo = l->w - 1 - y;
                }
                nuevaMatriz[y][x]->r = l->matriz[yAntiguo][xAntiguo]->r;
                nuevaMatriz[y][x]->g = l->matriz[yAntiguo][xAntiguo]->g;
                nuevaMatriz[y][x]->b = l->matriz[yAntiguo][xAntiguo]->b;
            }
        }

        for (int y = 0; y < l->h; y++){
            for (int x = 0; x < l->w; x++){
                free(l->matriz[y][x]);
            }
            free(l->matriz[y]);
        }
        free(l->matriz);

        l->matriz = nuevaMatriz;
        l->w = nuevoAncho;
        l->h = nuevoAlto;
    }