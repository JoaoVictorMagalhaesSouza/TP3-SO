from __future__ import annotations
from typing import List, Dict
from copy import deepcopy
import os
import memoria

# Estruturas de dados


class Cpu:
    def __init__(self, EstadoBloqueado: List, TabelaDeProcessos: TabelaDeProcessos, EstadoPronto: List, EstadoExecucao: List, Tempo: List, Memoria: Memoria, Disco: List):
        self.pid: int
        self.codigo_processo: List
        self.pc: int
        #self.memoria: List
        self.numeroVariaveis: int
        self.posicaoInicialMem: int
        self.prioridade: int
        self.ppid: int
        self.tempo_inicio: int
        self.tempo_cpu: int
        self.quantum: int
        self.politicaEscalonamento: int = 1
        # estruturas de dados acopladas, necessárias para algumas instruções
        # simuladas
        self.bloqueados = EstadoBloqueado
        self.tabela_de_processos = TabelaDeProcessos
        self.prontos = EstadoPronto
        self.EstadoExecucao = EstadoExecucao
        self.Tempo = Tempo
        self.memoria = Memoria
        self.Disco = Disco
        # atributos de estatistica
        self.requisicao_memoria = 0
        self.requisicao_negada = 0

    def recebe_processo(self, processo: Dict):
        self.pid = processo['pid']
        self.codigo_processo = processo['pscodigo']
        self.pc = processo['pc']
        #self.memoria = deepcopy(processo['memoria'])
        self.ppid = processo['ppid']
        self.prioridade = processo['prioridade']
        self.tempo_inicio = processo['tempo_inicio']
        self.tempo_cpu = processo['tempo_cpu']
        self.quantum = 2**processo['prioridade']
        self.numeroVariaveis = processo['nVariaveis']
        self.posicaoInicialMem = processo['posicaoInicialMem']

    def define_quantum(self):
        self.quantum = 2**self.prioridade

    def retorna_quantum(self):
        return self.quantum

    def atualiza_tabela(self):
        self.tabela_de_processos.atualizar_processo(
            self.pid, self.pc, self.codigo_processo, self.ppid,
            self.prioridade, self.tempo_inicio, self.tempo_cpu,
            self.numeroVariaveis, self.posicaoInicialMem
        )

    def escalonadorFIFO(self):
        pid_first_in = self.prontos[0]
        processo = self.tabela_de_processos.achar_processo_pid(pid_first_in)
        return processo

    def troca_contexto(self, T: bool, B: bool):
        # Dentro do atualiza_tabela() já é considerado caso seja instrução T.
        self.atualiza_tabela()
        print("Lista de prontos: ", self.prontos)
        processo_maior_prioridade: Dict = {}
        maior_prioridade = 5  # prioridade inexistente, só para iniciar.
        # Achar o próximo pronto.
        if(len(self.prontos) >= 1):
            if(self.politicaEscalonamento == 0):
                for i in self.prontos:
                    processo = self.tabela_de_processos.achar_processo_pid(i)
                    if processo['prioridade'] < maior_prioridade:
                        maior_prioridade = processo['prioridade']
                        processo_maior_prioridade = processo
            else:
                # Nesse caso não é o processo de maior prioridade e sim o que chegou primeiro.
                processo_maior_prioridade = self.escalonadorFIFO()

            if (not T) and (not B):
                self.prontos.append(deepcopy(self.EstadoExecucao[0]))

            # atualiza estado em execução
            self.EstadoExecucao[0] = processo_maior_prioridade['pid']
            # remove o estado em execução dos prontos
            self.prontos.remove(processo_maior_prioridade['pid'])
            # atualiza os registradores da cpu
            self.recebe_processo(deepcopy(processo_maior_prioridade))

            print('Novo processo na cpu, PID: ',
                  processo_maior_prioridade['pid'])

    def get_codigo_em_execucao(self):
        # Método usado em testes
        return self.codigo_processo

    def get_memoria(self):
        return self.memoria

    def executa(self):
        # declaracoes
        sem_memoria = False
        # Recebe a instrucao atual
        if len(self.tabela_de_processos.processos) == 0:
            print('Nada a executar')
            return None
        elif len(self.prontos) == 0 and len(self.bloqueados) > 0:
            if self.EstadoExecucao[0] == None:
                print('Nada a executar')
                return None
        print("PC: ", self.pc)
        instrucao: str = self.codigo_processo[self.pc]
        print('\npid na cpu: ', self.pid)
        print('instrucao: ', instrucao)

        novo_pc = self.pc + 1

        if instrucao[0] == 'N':
            sem_memoria = self.instrucao_N(instrucao)
        elif instrucao[0] == 'D':
            self.instrucao_D(instrucao)
        elif instrucao[0] == 'V':
            self.instrucao_V(instrucao)
        elif instrucao[0] == 'A':
            self.instrucao_A(instrucao)
        elif instrucao[0] == 'S':
            self.instrucao_S(instrucao)
        elif instrucao[0] == 'B':
            self.instrucao_B(instrucao)
            if (self.quantum - 1) > 0:
                self.prioridade -= 1  # Aumenta prioridade
        elif instrucao[0] == 'T':
            self.instrucao_T()
        elif instrucao[0] == 'F':
            jump = self.instrucao_F(instrucao)
            novo_pc += jump
        elif instrucao[0] == 'R':
            self.instrucao_R(instrucao)
            novo_pc = 0

        self.pc = novo_pc
        self.quantum -= 1
        self.tempo_cpu += 1

        if instrucao[0] == 'T':
            # Limpando memória?
            pos_ini = self.posicaoInicialMem
            while (pos_ini < self.posicaoInicialMem+self.numeroVariaveis):
                self.memoria.vetorMemoria[pos_ini] = None
                pos_ini += 1
            self.troca_contexto(True, False)

        elif (instrucao[0] == 'B') or sem_memoria:
            if sem_memoria:
                self.pc = 0
            self.troca_contexto(False, True)
        elif self.quantum == 0:
            self.prioridade += 1  # diminui prioridade
            if self.prioridade > 3:
                self.prioridade -= 1
            self.define_quantum()  # Atualiza seu quantum
            self.troca_contexto(False, False)

        print('quantum: ', self.quantum)

    def instrucao_N(self, instrucao: str):
        self.requisicao_memoria += 1
        numero_de_variaveis = int(instrucao[2])
        # for i in range(numero_de_variaveis):
        # ex: 3 variáveis teríamos [None, None, None]
        # self.memoria.append(None)
        print("Numero de variaveis: ", numero_de_variaveis)
        self.numeroVariaveis = numero_de_variaveis
        # posicaoInicial = self.memoria.firstFit(self.numeroVariaveis) Aparentemente OK
        posicaoInicial = self.memoria.firstFit(self.numeroVariaveis)
        print("Posicao inicial: ", posicaoInicial)
        if (posicaoInicial == None):
            print("Não há memoria para esse processo")
            # Podemos escolher como fazer. Acho que a melhor forma seria mover o processo para a fila de bloqueados.
            self.instrucao_B(instrucao)
            self.pc -= 1
            self.requisicao_negada += 1
            return True

        else:
            self.posicaoInicialMem = posicaoInicial

    def instrucao_D(self, instrucao: str):
        # Ex: Se a posicao inicial for daquele processo 0 e houverem 2 variaveis, então essas variaveis irão ocupar as posições 0+0 e 0+1 da memória
        posicao = self.posicaoInicialMem + int(instrucao[2])
        print("Posicao: ", posicao)
        self.memoria.vetorMemoria[posicao] = 0

    def instrucao_V(self, instrucao: str):
        valor = int(instrucao[4:])  # O que queremos armazenar
        # Onde queremos armazenar
        posicao = self.posicaoInicialMem + int(instrucao[2])
        self.memoria.vetorMemoria[posicao] = valor

    def instrucao_A(self, instrucao: str):
        posicao = self.posicaoInicialMem + int(instrucao[2])
        valor = int(instrucao[4:])  # Valor a ser adicionado
        self.memoria.vetorMemoria[posicao] = self.memoria.vetorMemoria[posicao] + valor

    def instrucao_S(self, instrucao: str):
        posicao = self.posicaoInicialMem + int(instrucao[2])
        valor = int(instrucao[4:])  # Valor a ser subtraído
        self.memoria.vetorMemoria[posicao] -= valor

    # Dar uma olhada aqui dps:

    def instrucao_B(self, instrucao: str):
        self.bloqueados.append(self.pid)
        posicao_inicial = len(self.Disco)

        # joga no disco e tira da memória
        for i in range(self.memoria.tamMemoria):
            if (i >= self.posicaoInicialMem and i < self.posicaoInicialMem+self.numeroVariaveis):
                self.Disco.append(self.memoria.vetorMemoria[i])
                self.memoria.vetorMemoria[i] = None
        self.posicaoInicialMem = posicao_inicial

    def instrucao_T(self):
        # Deve excluir da tabela de processos
        print('Processo terminado, Memória: ', self.memoria.vetorMemoria)
        self.EstadoExecucao = [None]
        self.tabela_de_processos.termina_processo(self.pid)
        # Limpar a memória que ele tava usando

    def instrucao_F(self, instrucao: str):
        # Atualiza tabela para pegar valores certos
        self.atualiza_tabela()

        novo_pid = self.tabela_de_processos.get_maior_pid() + 1
        novo_processo = deepcopy(
            self.tabela_de_processos.achar_processo_pid(self.pid)
        )
        novo_processo['pid'] = novo_pid  # maior_pid na tabela é atualizado
        novo_processo['pc'] += 1  # Pula para a proxima instrucao
        novo_processo['ppid'] = self.pid
        novo_processo['tempo_cpu'] = 0
        novo_processo['tempo_inicio'] = self.Tempo[0]
        novo_processo['nVariaveis'] = None
        novo_processo['posicaoInicialMem'] = None
        self.tabela_de_processos.add_processo(novo_processo)
        self.prontos.append(novo_pid)

        return int(instrucao[2:])

    def instrucao_R(self, instrucao: str):
        vetor_novo_codigo = []

        arquivo = open(instrucao[2:], 'r')
        linhas = arquivo.readlines()
        for linha in linhas:
            vetor_novo_codigo.append(linha[:-1])
        arquivo.close()

        self.codigo_processo = vetor_novo_codigo
        #self.memoria = []


class TabelaDeProcessos:
    def __init__(self):
        self.processos: List[Dict] = []  # Lista de dicionários
        self.maior_pid: int

    def achar_processo_pid(self, pid: int):
        for i in self.processos:
            if i['pid'] == pid:
                return i
        return None

    def add_processo(self, processo: Dict):
        self.processos.append(processo)
        self.maior_pid = processo['pid']

    # Ver a memoria aqui dps

    def atualizar_processo(self, pid: int, pc: int, codigo: List,
                           ppid: int, prioridade: int, tempo_inicio: int, tempo_cpu: int, nVariaveis: int,
                           posicaoInicialMem: int):
        processo = self.achar_processo_pid(pid)
        if processo != None:
            processo['pc'] = pc
            processo['nVariaveis'] = nVariaveis
            processo['posicaoInicialMem'] = posicaoInicialMem
            processo['pscodigo'] = codigo
            processo['ppid'] = ppid
            processo['prioridade'] = prioridade
            processo['tempo_inicio'] = tempo_inicio
            processo['tempo_cpu'] = tempo_cpu

    def termina_processo(self, pid: int):
        self.processos.remove(self.achar_processo_pid(pid))

    def get_maior_pid(self):
        return self.maior_pid

    def get_nVariaveis(self, pid: int):
        # fazer mais protegido a erros depois
        processo = self.achar_processo_pid(pid)
        return processo['nVariaveis']

    def set_posicaoInicialMem(self, pid: int, posicao: int):
        processo = self.achar_processo_pid(pid)
        processo['posicaoInicialMem'] = posicao

    def get_posicaoInicialMem(self, pid):
        processo = self.achar_processo_pid(pid)
        return processo['posicaoInicialMem']

    def diminui_posicao_no_disco(self, id: int, unidades: int):
        # recebe quantas unidades no disco a posição altera
        processo = self.achar_processo_pid(pid)
        process['posicaoInicialMem'] -= unidades


def gerenciador(r):
    ''' Pre-requisitos - antes de entrar no while que troca informações com
     processo pai (controle)'''

    codigo_primeiro_simulado = ['N 2', 'D 0', 'D 1', 'V 0 1000', 'V 1 500', 'A 0 19',
                                'A 0 20', 'S 1 53', 'A 1 55', 'F 1', 'R file_a2.txt',
                                'F 1', 'R file_b.txt', 'F 1', 'R file_c.txt',
                                'F 1', 'R file_d.txt', 'F 1', 'R file_e.txt', 'A 0 100', 'T']

    tabela_de_processos = TabelaDeProcessos()
    mem = memoria.Memoria()
    mem.iniciaMemoria()
    Disco = []
    EstadoBloqueado = []
    EstadoPronto = []
    EstadoExecucao = [0]  # Colocar em vetor para passar como referência
    Tempo = [0]
    cpu = Cpu(EstadoBloqueado, tabela_de_processos,
              EstadoPronto, EstadoExecucao, Tempo, mem, Disco)

    # Ver a memoria aqui dps -> Guardar a posição de memória que ele começa e a qtde de variaveis
    tabela_de_processos.add_processo(
        {'pid': 0, 'pscodigo': codigo_primeiro_simulado,
            'pc': 0, 'ppid': None, 'prioridade': 0,
            'tempo_inicio': Tempo[0], 'tempo_cpu': 0, 'posicaoInicialMem': None, 'nVariaveis': None}
    )
    cpu.recebe_processo(deepcopy(tabela_de_processos.achar_processo_pid(0)))
    ''' Fim da inicialização das estruturas de dados'''

    while True:
        comando = os.read(r, 32)

        if comando.decode() == 'U':
            # 1) executa próxima instrução do processo em execução;
            # 2) atualiza PC
            # 3) incrementa Tempo ("Global")
            # 4) faz escalonamento: pode ou não envolver troca de contexto!
            cpu.executa()
            print("Bloqueados: ", cpu.bloqueados)
            print("Memoria: ", cpu.memoria.vetorMemoria)
            Tempo[0] = Tempo[0] + 1
        elif comando.decode() == 'L':
            posicao_no_disco: int
            posicaoInicial: int
            numero_de_variaveis: int
            # print(tabela_de_processos.processos) # Descomentar para detalhes

            # 1) move o 1º processo da fila EstadoBloqueado para pronto
            print('EstadoBloqueado antes: ', EstadoBloqueado)
            if (len(EstadoBloqueado) > 0):
                primeiro_da_fila = EstadoBloqueado[0]
                EstadoPronto.append(primeiro_da_fila)
                EstadoBloqueado.remove(primeiro_da_fila)
                # Retirando do disco e passando para memoria
                posicao_no_disco = tabela_de_processos.get_posicaoInicialMem()
                numero_de_variaveis = tabela_de_processos.get_nVariaveis(
                    primeiro_da_fila)
                posicaoInicial = mem.firstFit(numero_de_variaveis)
                tabela_de_processos.set_posicaoInicialMem(
                    primeiro_da_fila, posicaoInicial)

                # Atualizando posições iniciais no disco dos processo
                # que continuam bloqueados, pois vai abir um gap
                # [1,2,3,'4','5',6]
                for pid in EstadoBloqueado:  # cada i é um id
                    posicao = tabela_de_processos.get_posicaoInicialMem(pid)
                    if posicao > posicao_no_disco:
                        tabela_de_processos.diminui_posicao_no_disco(
                            pid, numero_de_variaveis)

            print('EstadoBloqueado depois: ', EstadoBloqueado)
            if (cpu.EstadoExecucao[0] == None):
                cpu.troca_contexto(False, True)
            print("\nComando L")
        elif comando.decode() == 'I' or comando.decode() == 'M':
            # 1) Dispara processo impressão (cria um fork() aqui)
            # 2) faz um wait(), pois precisa esperar o impressão terminar
            pid2 = os.fork()

            if pid2 > 0:
                # processo pai
                print('Acionando processo de impressão...')
            else:
                print('Processo impressão - Imprimindo tabela de processos')
                print('Processos na tabela de processos: ')
                for processo in tabela_de_processos.processos:
                    print('PID: ', processo['pid'])
                    print('    PC: ', processo['pc'])
                    print('    PPID (PID do processo pai): ', processo['ppid'])
                    print('    Prioridade: ', processo['prioridade'])
                    print('    Tempo de início: ', processo['tempo_inicio'])
                    print('    Tempo usado em CPU: ', processo['tempo_cpu'])

                print('\nTempo atual do sistema: ', Tempo[0])
                print('PID do Processo em CPU: ', cpu.pid)
                print('Quantum do processo em CPU: ', cpu.quantum)
                print('Memória:', mem.vetorMemoria)
                print('Numero de fragmentos: ', mem.fragmentos())
                print('Percentual de requisição negada: ',
                      cpu.requisicao_negada/cpu.requisicao_memoria)
                print('Media de alocação: ',
                      mem.numeroNos/cpu.requisicao_memoria)
                print('Disco: ', Disco)
                exit()

        if comando.decode() == 'M':
            print("Fim do sistema previsto!")
            exit()
