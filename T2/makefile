CC = gcc
CFLAGS = -Wall -std=c11 -g

# Lista de archivos objeto correspondientes a los modulos obligatorios
OBJS = main.o lienzo.o filtros.o

TARGET = PhotoChop

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJS)

# Reglas de compilacion para cada archivo
main.o: main.c main.h lienzo.h filtros.h
	$(CC) $(CFLAGS) -c main.c

lienzo.o: lienzo.c lienzo.h
	$(CC) $(CFLAGS) -c lienzo.c

filtros.o: filtros.c filtros.h lienzo.h
	$(CC) $(CFLAGS) -c filtros.c

# Limpia los archivos compilados
clean:
	rm -f $(OBJS) $(TARGET)

# Recompilar desde cero
rebuild: clean all

# Ejecutar programa
run: $(TARGET)
	@./$(TARGET)

# Depurar con valgrind
valgrind: $(TARGET)
	valgrind --leak-check=full --show-leak-kinds=all ./$(TARGET)

.PHONY: all clean rebuild run valgrind