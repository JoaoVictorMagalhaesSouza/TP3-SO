import gerenciador
import os
import sys
import time


# file descriptors r, w for reading and writing
r, w = os.pipe()
pid = os.fork()
if pid > 0:  # processo pai
    entrada = ''
    while entrada != 'M'.encode():
        entrada = input().encode()
        os.write(w, entrada)

else: # processo filho
    gerenciador.gerenciador(r)

    