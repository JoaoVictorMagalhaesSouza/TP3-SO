class Memoria:
    def __init__(self):
        self.tamMemoria: int = 15
        self.vetorMemoria: int = []
        self.flagParaNext: int = None
        self.numeroNos: int = 0
        # FILE memoria virtual -> implementar depois

    def iniciaMemoria(self):
        '''self.vetorMemoria = [None, None, None, None, None,
                             6, 7, 8, 9, 10, None, 19, 36, None, None]'''
        self.vetorMemoria = [None, None, None, 4, 5,
                             6, 7, 8, 9, 10, None, 19, 36, 39, None]
        '''for i in range(self.tamMemoria):  # Iniciando as posições de memória como válidas
            self.vetorMemoria.append(None)'''

    def firstFit(self, numVariaveis: int):
        vetorIdeal = []
        for i in range(numVariaveis):
            # O vetor ideal seria onde todas as posicoes estao livres

            vetorIdeal.append(None)
            # [None,None,None,...,None]

        for i in range(self.tamMemoria):
            self.numeroNos += 1
            if (i+numVariaveis <= self.tamMemoria):
                # o ultimo indice é exclusivo n entra
                if (self.vetorMemoria[i:i+numVariaveis] == vetorIdeal):
                    return i
                else:
                    continue
            else:
                continue

    def nextFit(self, numVariaveis: int):
        vetorIdeal = []
        for i in range(numVariaveis):
            vetorIdeal.append(None)
        if (self.flagParaNext == None):
            for i in range(self.tamMemoria):
                self.numeroNos += 1
                if (i+numVariaveis <= self.tamMemoria):
                    # o ultimo indice é exclusivo n entra
                    if (self.vetorMemoria[i:i+numVariaveis] == vetorIdeal):
                        self.flagParaNext = (
                            i + numVariaveis) % self.tamMemoria
                        return i
                    else:
                        continue
        else:
            contadorMemoria = 0
            pontoDePartida = self.flagParaNext
            print("Ponto de partida: ", pontoDePartida)
            while (contadorMemoria < self.tamMemoria):  # Varrer toda a memoria circular
                self.numeroNos += 1
                if (pontoDePartida+numVariaveis <= self.tamMemoria):
                    if (self.vetorMemoria[pontoDePartida:pontoDePartida+numVariaveis] == vetorIdeal):
                        self.flagParaNext = (
                            pontoDePartida + numVariaveis) % self.tamMemoria  # Lista circular
                        return pontoDePartida
                    else:
                        pontoDePartida = (pontoDePartida+1) % self.tamMemoria
                        contadorMemoria += 1
                else:
                    pontoDePartida = (pontoDePartida+1) % self.tamMemoria
                    contadorMemoria += 1

    def bestFit(self, numVariaveis: int):
        menorTamanho = 9999999999
        menorPosicao = 0
        contador = 0
        posicaoInicialJ = 0
        vetorIdeal = []
        primeiroJ = 0

        for i in range(numVariaveis):
            vetorIdeal.append(None)

        i = 0
        while (i < self.tamMemoria):
            self.numeroNos += 1
            #print("i:  ",i)
            j = i
            primeiroJ = j

            while (j < self.tamMemoria):
                # Começando a formar a sequencia de memoria vazia  [None,None,...,None]
                if (self.vetorMemoria[j] == None):
                    contador += 1
                    j += 1
                else:  # Ja nao da pra contar mais com essa posicao, entao vamos ver o que temos
                    break
            # Vendo o que temos:
            if (contador == 0):  # Significa que nosso ponto de partida foi uma posicao de memoria ocupada
                i += 1  # Entao so bora ver a posicao seguinte

            else:  # Significa que nosso ponto de partida foi uma posicao vazia
                # Se o numero de elementos da sequencia de memoria obtida é menor que o menor e,
                # se esse numero de elementos cabe as variaveis que queremos armazenar.
                # Obtemos uma sequencia de memoria candidata a ser a melhor
                if (contador < menorTamanho and contador >= numVariaveis):
                    menorTamanho = contador
                    menorPosicao = primeiroJ  # Guardar a posicao de inicio da sequencia candidata
                # Vamos verificar mais sequencias a partir do fim dessa então.
                i += contador
                contador = 0
        print("Melhor posicao para ser inserido: ", menorPosicao)
        return menorPosicao

    def worstFit(self, numVariaveis: int):
        maiorTam = -99999999
        menorPosicao = 0
        contador = 0
        posicaoInicialJ = 0
        vetorIdeal = []
        primeiroJ = 0
        for i in range(numVariaveis):
            vetorIdeal.append(None)

        i = 0
        while (i < self.tamMemoria):
            self.numeroNos += 1
            print("i:  ", i)
            print("Maior: ", maiorTam)
            j = i
            primeiroJ = j
            while (j < self.tamMemoria):
                if (self.vetorMemoria[j] == None):
                    contador += 1
                    j += 1
                else:
                    break

            #print("Contador: ",contador)
            if (contador == 0):
                i += 1

            else:
                if (contador > maiorTam and contador >= numVariaveis):
                    maiorTam = contador
                    menorPosicao = primeiroJ
                i += contador
                contador = 0

        print("Melhor posicao para ser inserido: ", menorPosicao)
        return menorPosicao

    def fragmentos(self):
        contador = 0
        tipo_atual = self.vetorMemoria[0]
        for unidade in self.vetorMemoria:  # quantifica as variações
            if type(unidade) != type(tipo_atual):
                contador += 1
                tipo_atual = unidade

        print('Contador', contador)
        if contador % 2 != 0:  # impar
            valor = (contador + 1)/2
        else:
            if self.vetorMemoria[0] == None:
                valor = contador/2 + 1
            else:
                valor = contador/2

        return valor
