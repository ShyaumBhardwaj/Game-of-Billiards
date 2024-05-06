CC = clang
CFLAGS = -Wall -pedantic -std=c99 -fPIC
LDFLAGS = -lm
PYTHON_INCLUDE = -I/usr/include/python3.11
PYTHON_LIB = -lpython3.11



all:libphylib.so _phylib.so 

phylib.o: phylib.c phylib.h
	$(CC) $(CFLAGS) -c phylib.c -o phylib.o

libphylib.so: phylib.o
	$(CC) -shared -o libphylib.so phylib.o $(LDFLAGS)

phylib_wrap.o: phylib_wrap.c
	$(CC) $(CFLAGS) -c phylib_wrap.c $(PYTHON_INCLUDE)

_phylib.so: phylib_wrap.o libphylib.so
	$(CC) $(CFLAGS) -shared phylib_wrap.o -L. $(PYTHON_LIB) $(LDFLAGS) -lphylib -o _phylib.so

phylib_wrap.c: phylib.i phylib.h
	swig -python phylib.i

clean:
	rm -f *.o *.so *.svg
