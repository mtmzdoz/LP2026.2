#include "main.h"
#include "lienzo.h"
#include "filtros.h"

/*
***
Parametro 1: None
***
Retorno: int (0 si todo bien, 1 si hubo error)
***
Inicia el ciclo del programa, procesa el archivo de entrada (comandos.txt) y libera la memoria al finalizar
*/
int main() {
    MotorFiltros motor;
    motor.aplicar[0] = filtro_gris;
    motor.aplicar[1] = filtro_invertir; 
    motor.aplicar[2] = filtro_expos;
    motor.aplicar[3] = filtro_espejo;
    motor.aplicar[4] = filtro_rotar;

    struct Lienzo *lienzoActual = NULL;
    int contadorSaves = 1; //Para SAVE

    const char *nombreArchivo = "comandos.txt"; 
    FILE *archivoEntrada;
    archivoEntrada = fopen(nombreArchivo, "r");
    if (archivoEntrada == NULL){
        printf("Error: No se pudo abrir %s\n", nombreArchivo);
        return 1;
    }

    char linea[MAX_LINEA];
    char comando[50];

    //Pág 79
    while (fgets(linea, sizeof(linea), archivoEntrada) != NULL){
        if (sscanf(linea, "%s", comando) != 1){//Extrae el primer string para identificar el comando
            continue; //linea vacia
        }
        //printf("[PhotoChop] Comando: %s\n", comando); // BORRAR Muestra el comando actual

        if (strcmp(comando, "NEW") == 0){ //Pág48
            int ancho, alto;
            sscanf(linea, "%*s %d %d", &ancho, &alto);
            
            if (ancho > 0 && alto > 0){
                if (lienzoActual != NULL){  //Si ya existe un lienzo, se libera el anterior
                    lienzo_liberar(lienzoActual);
                }
                
                lienzoActual = lienzo_crear(ancho, alto);
                printf("[PhotoChop] Lienzo %dx%d creado.\n", ancho, alto);

            }else{
                printf("Error: Dimensiones invalidas para NEW.\n");
            }

        }else if (strcmp(comando, "RED") == 0 || strcmp(comando, "GREEN") == 0 || strcmp(comando, "BLUE") == 0){
            int x, y, valorColor;
            sscanf(linea, "%*s %d %d %d", &x, &y, &valorColor);
            //printf("[PhotoChop] Modificando pixel (%d,%d) con valor %d para canal %s.\n", x, y, valorColor, comando); //BORRAR
            
            if (lienzoActual != NULL && x >= 0 && x < lienzoActual->w && y >= 0 && y < lienzoActual->h){
                if (strcmp(comando, "RED") == 0) {
                    lienzoActual->matriz[y][x]->r = (unsigned char)valorColor;
                    printf("[PhotoChop] Canal rojo actualizado en (%d,%d).\n", x, y);
                }else if (strcmp(comando, "GREEN") == 0){
                    lienzoActual->matriz[y][x]->g = (unsigned char)valorColor;
                    printf("[PhotoChop] Canal verde actualizado en (%d,%d).\n", x, y);
                }else if (strcmp(comando, "BLUE") == 0){
                    lienzoActual->matriz[y][x]->b = (unsigned char)valorColor;
                    printf("[PhotoChop] Canal azul actualizado en (%d,%d).\n", x, y);
                }
            }
        // --- INICIO DE BLOQUE DE FILTROS ---
        }else if (strcmp(comando, "GRIS") == 0){
            if (lienzoActual != NULL){
                motor.aplicar[0](lienzoActual); 
                printf("[PhotoChop] Filtro GRIS aplicado.\n");
            }

        }else if (strcmp(comando, "INVERTIR") == 0){
            if (lienzoActual != NULL){
                motor.aplicar[1](lienzoActual);
                printf("[PhotoChop] Filtro INVERTIR aplicado.\n");
            }

        }else if (strcmp(comando, "EXPOS") == 0){
            int porcentaje;
            sscanf(linea, "%*s %d", &porcentaje);
            
            if (lienzoActual != NULL){
                porcentajeExposicion(porcentaje);
                motor.aplicar[2](lienzoActual);
                printf("[PhotoChop] Exposicion ajustada (%d %%).\n", porcentaje);
            }

        }else if (strcmp(comando, "ESPEJO") == 0){
            if (lienzoActual != NULL){
                motor.aplicar[3](lienzoActual); 
                printf("[PhotoChop] Filtro ESPEJO aplicado.\n");
            }

        }else if (strcmp(comando, "ROTAR") == 0){
            char direccion[10]; //DER o IZQ
            sscanf(linea, "%*s %s", direccion);
            
            if (lienzoActual != NULL){
                //1 si es der o 0 si es izq a la variable de la funcion aux
                if (strcmp(direccion, "DER") == 0){
                    dirRotacion(1); 
                }else{
                    dirRotacion(0); 
                }
                motor.aplicar[4](lienzoActual);
                printf("[PhotoChop] Filtro ROTAR aplicado hacia %s.\n", (strcmp(direccion, "DER") == 0) ? "la derecha" : "la izquierda"); //(pregunta/condición) ? si es verdad : si es falso;
            }
        // --- FIN DE BLOQUE DE FILTROS ---
        }else if (strcmp(comando, "INFO") == 0){
            int x, y;
            sscanf(linea, "%*s %d %d", &x, &y);
            
            if (lienzoActual != NULL && x >= 0 && x < lienzoActual->w && y >= 0 && y < lienzoActual->h){
                Pixel *pixel = lienzoActual->matriz[y][x];
                printf("[INFO] Pixel (%d,%d) -> R: %d | G: %d | B: %d\n", x, y, pixel->r, pixel->g, pixel->b);
            }

        }else if (strcmp(comando, "RESIZE") == 0){
            int nuevoAncho, nuevoAlto;
            sscanf(linea, "%*s %d %d", &nuevoAncho, &nuevoAlto);
            
            if (nuevoAncho > 0 && nuevoAlto > 0){ 
                if (lienzoActual != NULL){
                    lienzoActual = lienzo_redimensionar(lienzoActual, nuevoAncho, nuevoAlto);
                    printf("[PhotoChop] Lienzo redimensionado a %dx%d.\n", nuevoAncho, nuevoAlto);
                }

            }else{
                printf("Error: Dimensiones invalidas para RESIZE.\n");
            }

        }else if (strcmp(comando, "SAVE") == 0){
            if (lienzoActual != NULL){
                exportar_ppm(lienzoActual, contadorSaves);
                contadorSaves++; //001, 002, etc
            }

        }else if (strcmp(comando, "EXIT") == 0){
            printf("[PhotoChop] Memoria liberada. Saliendo...\n");
            break; 
        }
    }

    fclose(archivoEntrada);

    if (lienzoActual != NULL){
        lienzo_liberar(lienzoActual);
    }

    return 0;
}