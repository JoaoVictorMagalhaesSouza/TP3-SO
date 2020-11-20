class Memoria:
    def __init__(self):
        self.tamMemoria: int = 15
        self.vetorMemoria: int = []
        self.flagParaNext: int = None
        # FILE memoria virtual -> implementar depois

    def iniciaMemoria(self):
        self.vetorMemoria = [None,None,None,None,None,6,7,8,9,10,None,19,36,None,None]
        '''for i in range(self.tamMemoria):  # Iniciando as posições de memória como válidas
            self.vetorMemoria.append(None)'''

    def firstFit(self, numVariaveis: int):
        vetorIdeal = []
        for i in range(numVariaveis):
            # O vetor ideal seria onde todas as posicoes estao livres
            vetorIdeal.append(None)
            # [None,None,None,...,None]

        for i in range(self.tamMemoria):
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

    def bestFit(self, numVariaveis:int):
        menorTamanho = 9999999999
        menorPosicao = 0
        contador = 0
        posicaoInicialJ = 0
        vetorIdeal = []
        primeiroJ = 0
        
        for i in range (numVariaveis):
            vetorIdeal.append(None)

        i = 0
        while (i < self.tamMemoria):
            #print("i:  ",i)
            j = i
            primeiroJ = j
            
            while (j < self.tamMemoria):
                if (self.vetorMemoria[j]==None): #Começando a formar a sequencia de memoria vazia  [None,None,...,None]
                    contador+=1
                    j+=1
                else:         #Ja nao da pra contar mais com essa posicao, entao vamos ver o que temos               
                    break
            #Vendo o que temos:
            if (contador==0): #Significa que nosso ponto de partida foi uma posicao de memoria ocupada
                i+=1 #Entao so bora ver a posicao seguinte
            
            else: #Significa que nosso ponto de partida foi uma posicao vazia
                #Se o numero de elementos da sequencia de memoria obtida é menor que o menor e,
                #se esse numero de elementos cabe as variaveis que queremos armazenar.
                if (contador < menorTamanho and contador >= numVariaveis): #Obtemos uma sequencia de memoria candidata a ser a melhor
                        menorTamanho = contador
                        menorPosicao = primeiroJ #Guardar a posicao de inicio da sequencia candidata
                i += contador #Vamos verificar mais sequencias a partir do fim dessa então.
                contador = 0
        print("Melhor posicao para ser inserido: ",menorPosicao)
        return menorPosicao
