struct Lienzo; /* Forward declaration */

typedef void (*FuncFiltro)(struct Lienzo *l); /* Puntero a funcion */

typedef struct MotorFiltros{
    FuncFiltro aplicar[5]; /* Arreglo de punteros a funcion con los 5 filtros */
} MotorFiltros;

void filtro_gris(struct Lienzo *l);
void filtro_invertir(struct Lienzo *l);
void filtro_expos(struct Lienzo *l);
void filtro_espejo(struct Lienzo *l);
void filtro_rotar(struct Lienzo *l);

//Yo Funciones de apoyo para saltar la limitación de parámetros en la firma
void porcentajeExposicion(int p);
void dirRotacion(int der);