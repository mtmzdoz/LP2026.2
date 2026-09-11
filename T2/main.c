#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "main.h"
#include "lienzo.h"
#include "filtros.h"

/*
***
Parametro 1: None
***
int
***
Inicia el ciclo del programa, procesa comandos.txt y libera memoria al finalizar.
*/
int main() {
    // 1. Inicialización del Motor de Filtros (Requisito para los 10 pts)
    MotorFiltros motor;
    motor.aplicar[0] = filtro_gris;
    // motor.aplicar[1] = filtro_invertir; // Se agregarán después
    // motor.aplicar[2] = filtro_expos;
    // motor.aplicar[3] = filtro_rotar;
    // motor.aplicar[4] = filtro_espejo;

    struct Lienzo *lienzo_actual = NULL;
    int contador_imagenes = 1; // Para el comando SAVE

    // 2. Apertura del archivo
    FILE *archivo = fopen("comandos.txt", "r");
    if (archivo == NULL) {
        printf("Error: No se pudo abrir comandos.txt\n");
        return 1;
    }

    char linea[MAX_LINEA];
    char comando[50];

    // 3. Procesamiento por lotes (Lectura línea por línea)
    while (fgets(linea, sizeof(linea), archivo) != NULL) {
        // Extraemos el primer string para identificar el comando
        if (sscanf(linea, "%s", comando) != 1) {
            continue; // Línea vacía
        }

        if (strcmp(comando, "NEW") == 0) {
            int w, h;
            sscanf(linea, "%*s %d %d", &w, &h);
            
            // Si ya existía un lienzo, debe liberar la memoria anterior
            if (lienzo_actual != NULL) {
                lienzo_liberar(lienzo_actual);
            }
            lienzo_actual = lienzo_crear(w, h);
            printf("[PhotoChop] Lienzo %dx%d creado.\n", w, h);
        }
        else if (strcmp(comando, "RED") == 0 || strcmp(comando, "GREEN") == 0 || strcmp(comando, "BLUE") == 0) {
            int x, y, val;
            sscanf(linea, "%*s %d %d %d", &x, &y, &val);
            
            if (lienzo_actual != NULL && x < lienzo_actual->w && y < lienzo_actual->h) {
                if (strcmp(comando, "RED") == 0) {
                    lienzo_actual->matriz[y][x]->r = (unsigned char)val;
                    printf("[PhotoChop] Canal rojo actualizado en (%d,%d).\n", x, y);
                } else if (strcmp(comando, "GREEN") == 0) {
                    lienzo_actual->matriz[y][x]->g = (unsigned char)val;
                    printf("[PhotoChop] Canal verde actualizado en (%d,%d).\n", x, y);
                } else if (strcmp(comando, "BLUE") == 0) {
                    lienzo_actual->matriz[y][x]->b = (unsigned char)val;
                    printf("[PhotoChop] Canal azul actualizado en (%d,%d).\n", x, y);
                }
            }
        }
        else if (strcmp(comando, "GRIS") == 0) {
            if (lienzo_actual != NULL) {
                motor.aplicar[0](lienzo_actual); // Ejecucion estricta por puntero a funcion
                printf("[PhotoChop] Filtro GRIS aplicado.\n");
            }
        }
        else if (strcmp(comando, "INFO") == 0) {
            int x, y;
            sscanf(linea, "%*s %d %d", &x, &y);
            
            if (lienzo_actual != NULL && x < lienzo_actual->w && y < lienzo_actual->h) {
                Pixel *p = lienzo_actual->matriz[y][x];
                // Imprime en terminal los valores RGB actuales con el formato solicitado
                printf("[INFO] Pixel (%d,%d) -> R: %d | G: %d | B: %d\n", x, y, p->r, p->g, p->b);
            }
        }
        else if (strcmp(comando, "EXIT") == 0) {
            // Libera absolutamente toda la memoria asignada y termina la ejecución
            printf("[PhotoChop] Memoria liberada. Saliendo...\n");
            break; 
        }
        
        // Aquí puedes ir agregando los demás comandos con else if (INFO, RESIZE, GRIS, etc.)
    }

    // 4. Limpieza final
    fclose(archivo);
    if (lienzo_actual != NULL) {
        lienzo_liberar(lienzo_actual);
    }

    return 0;
}