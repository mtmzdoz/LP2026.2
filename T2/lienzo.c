#include <stdlib.h>
#include <stdio.h>
#include "lienzo.h"

/*
***
Parametro 1: int (ancho)
Parametro 2: int (alto)
***
Retorno: Un puntero al lienzo creado
***
Se reserva memoria para las filas, luego para las columnas y finalmente para cada pixel individual. Se inicializa en negro
*/
struct Lienzo* lienzo_crear(int ancho, int alto){
    struct Lienzo *lienzo = (struct Lienzo*)malloc(sizeof(struct Lienzo));
    lienzo->w = ancho;
    lienzo->h = alto;
    lienzo->exposicion = 100; // Valor por defecto
    lienzo->rotacion = 1;

    lienzo->matriz = (Pixel***)malloc(alto * sizeof(Pixel**));//Memoria filas
    for (int y = 0; y < alto; y++){
        lienzo->matriz[y] = (Pixel**)malloc(ancho * sizeof(Pixel*));//Memoria col
        for (int x = 0; x < ancho; x++){
            lienzo->matriz[y][x] = (Pixel*)malloc(sizeof(Pixel));
            lienzo->matriz[y][x]->r = 0; //Inicializar en negro 
            lienzo->matriz[y][x]->g = 0;
            lienzo->matriz[y][x]->b = 0;
        }
    }
    return lienzo;
}

/*
***
Parametro 1: struct Lienzo* (puntero al lienzo)
Parametro 2: int (nuevo ancho)
Parametro 3: int (nuevo alto)
***
Retorno: Un puntero al lienzo redimensionado
***
Redimensiona el lienzo. Si se agranda conserva el lienzo original manteniendolo en la esquina superior izquierda y rellena con blanco (255,255,255) el espacio nuevo. En caso
de achicarse solo corta el lienzo original. Y se libera la matriz anterior.
*/
struct Lienzo* lienzo_redimensionar(struct Lienzo *l, int n_ancho, int n_alto){
    if (!l || !l->matriz){
        return l;
    }

    //nueva matriz tridimensional
    Pixel ***nuevaMatriz = (Pixel***)malloc(n_alto * sizeof(Pixel**));
    for (int y = 0; y < n_alto; y++){
        nuevaMatriz[y] = (Pixel**)malloc(n_ancho * sizeof(Pixel*));
        for (int x = 0; x < n_ancho; x++){
            nuevaMatriz[y][x] = (Pixel*)malloc(sizeof(Pixel));
            
            //Si el pixel estaba en el lienzo antiguo se copia 
            if (x < l->w && y < l->h){
                nuevaMatriz[y][x]->r = l->matriz[y][x]->r;
                nuevaMatriz[y][x]->g = l->matriz[y][x]->g;
                nuevaMatriz[y][x]->b = l->matriz[y][x]->b;
            }else{
                nuevaMatriz[y][x]->r = 255; //Si es nuevo inicializa en blanco
                nuevaMatriz[y][x]->g = 255;
                nuevaMatriz[y][x]->b = 255;
            }
        }
    }

    //Se libera el lienzo antiguo
    for (int y = 0; y < l->h; y++){
        for (int x = 0; x < l->w; x++){
            free(l->matriz[y][x]);
        }
        free(l->matriz[y]);
    }
    free(l->matriz);

    //Se actualiza el puntero y las dimensiones en el lienzo original
    l->matriz = nuevaMatriz;
    l->w = n_ancho;
    l->h = n_alto;

    return l;
}

/*
***
Parametro 1: struct Lienzo* (puntero al lienzo)
***
Retorno: None
***
Libera toda la memoria alojada en cascada para el lienzo y sus pixeles
*/
void lienzo_liberar(struct Lienzo *lienzo){
    if (lienzo == NULL){
        return;
    }

    for (int y = 0; y < lienzo->h; y++){ //filas
        for (int x = 0; x < lienzo->w; x++){ //col
            free(lienzo->matriz[y][x]); //free a cada pixel indiviaual
        }
        free(lienzo->matriz[y]); //free la fila
    }
    free(lienzo->matriz); //free la matriz principal 
    free(lienzo);
}

/*
***
Parametro 1: struct Lienzo* (puntero al lienzo)
Parametro 2: int (contador de imagenes)
***
Retorno: None
***
Exporta el lienzo actual a un archivo ppm en texto plano (P3) dentro de la carpeta /img
*/
void exportar_ppm(struct Lienzo *l, int contador_img){
    if (!l || !l->matriz){
        return;
    }

    char ruta[64];
    //Para que la ruta sea img/img_00x.ppm
    sprintf(ruta, "img/img_%03d.ppm", contador_img);

    FILE *archivoSalida;
    archivoSalida = fopen(ruta, "w");
    if (archivoSalida == NULL){
        printf("Error: No se pudo crear el archivo %s. Recordar estar en la carpeta /img \n", ruta);
        return;
    }

    fprintf(archivoSalida, "P3\n");
    fprintf(archivoSalida, "%d %d\n", l->w, l->h);
    fprintf(archivoSalida, "255\n");

    //Recorrer la matriz de izquierda a derecha y de arriba hacia abajo
    for (int y = 0; y < l->h; y++){
        for (int x = 0; x < l->w; x++){
            Pixel *pixel = l->matriz[y][x];
            fprintf(archivoSalida, "%d %d %d ", pixel->r, pixel->g, pixel->b);
        }
        fprintf(archivoSalida, "\n");
    }

    fclose(archivoSalida);
    printf("[PhotoChop] Imagen guardada en /img/img_%03d.ppm.\n", contador_img);
}