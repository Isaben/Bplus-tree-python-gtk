import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import math
import cairo
from random import randint
import time
import copy

"""
    O código está organizado da seguinte maneira:
    1 - Classe node, que corresponde aos nós da árvore. Contem os atributos:
        father = nó pai, assume valor "null"
        isRoot = booleano que assume True se o nó for raiz, False se não
        isLeaf = booleano que assume True se o nó for folha, False se não
        ordem = ordem do nó
        busca_flag = flag utilizada apenas na função de busca para visualização, basicamente
        sempre será False com exceção na função de busca, quando o nó que contém o elemento
        que foi buscado se encontra.
        list_elementos = lista que contém os elementos do nó, de acordo com o padrão de árvores B+.
        É basicamente exatamente do jeito que é desenhado uma. O padrão dela é
        que, para valores nulos, estes assumem o número 9999. Por exemplo:
        [9999, 1, 9999, 3, <objeto da classe node>]
        Corresponderia muito bem a um nó folha de uma árvore B+ de ordem 3.

        Funções:

        real_len() = função que retorna a quantidade de elementos no nó
        qtd_pointers() = retorna a quantidade de ponteiros (a.k.a elementos da classe node)
        nesse nó
        erase() = apaga o nó, colocando tudo 9999 em seus espaços
        elementos() = retorna os elementos na lista
        ponteiros() = os ponteiros na lista

    2 - Classe BplusTree, é literalmente a classe que corresponde a árvore. Atributos:
        root = objeto da classe node que corresponde à raiz da árvore.
        ordem = ordem da árvore.

        Funções:

        insert() = função que recebe como parâmetro um valor a ser inserido na árvore,
        busca o local adequado a ser inserido e insere. É nela que é feita a maracutaia
        de separar o nó folha quando necessário e chamar as outras funções. Por ser baseada no pseudo-código
        existente no livro do Silberschatz, ela depende da função recursiva insert_in_father
        e da função insert_in_leaf.
        insert_in_leaf() = simplesmente insere o valor parâmetro no nó que supõem-se ser
        folha, e retorna um nó com o valor adicionado.
        insert_in_father() = função recursiva que é chamada sempre que ao inserir
        um valor em um nó qualquer, seja ele folha ou intermediário, verifica se é
        preciso separar o nó atual e subir o para o próximo nível, ou se basta
        inserir o valor no nó atual e ajeitar os ponteiros. É nela também que é possível
        aumentar a altura da árvore quando necessário. Basicamente, ela que faz as coisas
        mais complexas no algoritmo.
        definir_pai() = função recursiva que atualiza o atributo father de todos os nós
        da árvore, para corresponder aos "pais verdadeiros" dos nós.
        delete() = função que verifica qual o nó que possivelmente encontra-se o valor
        a ser deletado, e chama a função delete_recursive, que é onde realmente a mágica acontece.
        delete_recursive() = aqui é o ultimatum da complexidade. É esta função que verifica
        se o nó atual tem o valor a ser deletado (apenas na primeira vez que é chamada que importa),
        verifica também qual situação do nó atual, se ele é raiz, intermediário ou folha,
        e age de acordo com o algoritmo de deleções em árvores B+. Se o nó atual for folha
        e seus irmãos só possuem o valor mínimo de valores de acordo com a ordem, então é chamada
        a função merge_leaf() para fazer o merge entre o nó irmão adequado, o esquerdo ou o direito. Se
        ambos são possíveis, o esquerdo é preferido. Caso algum nó folha irmão tenha elementos
        sobrando, então é chamado a função shift_value(), para fazer a troca de valores entre ambos.
        Se o nó em questão na recursividade for um intermediário, as mesmas verificações são feitas,
        porém chamando as funções merge_intermediate() e shift_value_intermediate(). Diga-se de passagem,
        a função de shift_value_intermediate() só realmente é chamada quando o irmão está cheio,
        em todos os outros casos é preferível usar o merge_intermediate().
        Esta função também é responsável por agir de acordo quando a recursividade acaba
        na raiz, verificando se ela possui ou não 2 ponteiros, caso não ela é deletada e o nó
        sobrando vira raiz, ou simplesmente atualizando a raiz em caso de uma deleção de um elemento.
        merge_leaf() = dá merge em um nó que precisa (node) com um irmão (brother), sendo
        este um irmão esquerda ou direita, de acordo com o parâmetro de (sentido).
        Chama novamente a delete_recursive() para fazer os ajustes necessários no pai.
        shift_value() = realiza a troca de elementos entre um nó que precisa, e um irmão.
        Possui os mesmos parâmetros da merge_leaf(), e também realiza os ajutes no pai
        que são necessários, porém fecha o ciclo de recursividade.
        merge_intermediate() = idêntica a merge_leaf(), porém com algoritmo um pouco diferenciado
        adaptado para nós intermediários. Também chama a delete_recursive para fazer os ajustes
        necessários.
        shift_value_intermediate() = idêntica a shift_value() das folhas, porém com algoritmo
        adaptado para nó intermediário.
        delete_in_node() = realiza a deleção do valor em um nó especificado. Retorna o nó atualizado
        com o valor deletado, ou -1 caso o mesmo não existe no nó.
        search() =  realiza a busca na árvore, retornando False, False caso o valor não existe, ou o próprio
        índice do valor especificado no nó correspondente E o próprio nó que o valor foi encontrado.
        retorna_nos() = função recursiva pra retornar TODOS os filhos dos nós em um nível desejado.
        Contém uma quantidade considerável de parâmetros, descrição mais detalhada na própria função.

    3 - Classe Interface, como o próprio nome diz, é a classe responsável por criar a interface do programa.
    Possui diversos atributos, todos eles correspondendo a algum objeto da interface. Como são muitos,
    e não exatamente importantes, não chega a ser interessante listá-los aqui.
    Todas as funções correspondem ao que foi pedido, e chamam funções correspondentes
    no objeto da classe BplusTree que é criado no construtor da interface.

"""
# Espaços vazios nas listas é SEMPRE 9999
VAZIO = 9999
LEFT = 1
RIGHT = 0

"""
    Classe pro Nó
"""
class node:
    def __init__(self, father, isRoot, isLeaf, ordem):
        self.father = father    # nó pai, "null" se for raiz
        self.isRoot = isRoot    # booleano pra dizer se é raiz ou não
        self.isLeaf = isLeaf    # booleano pra dizer se é folha ou não
        self.ordem = ordem
        self.busca_flag = False

        self.list_elementos = [] # lista pros elementos em si do nodo
        for i in range(0, ordem ):
            self.list_elementos.append(VAZIO)
            self.list_elementos.append(VAZIO)

        self.list_elementos.pop()

    # pega o tamanho da lista "verdadeira", sem contar os "ponteiros"
    def real_len(self):
        value = 0
        for i in range (1, len(self.list_elementos), 2):
            if(self.list_elementos[i] != VAZIO):
                value += 1

        return value

    # quantidade de ponteiros na lista
    def qtd_pointers(self):
        valor = 0
        for i in range(0, len(self.list_elementos), 2):
            if(self.list_elementos[i] != VAZIO):
                valor += 1

        return valor

    def erase(self):
        for i in range(0, len(self.list_elementos)):
            self.list_elementos[i] = VAZIO

    ##retona os elementos
    def elementos(self):
        value = []
        for i in range (1, len(self.list_elementos), 2):
            if(self.list_elementos[i] != VAZIO):
                value.append(self.list_elementos[i])
            else:
                value.append(" ")

        return value

    # os ponteiros ponteiros na lista
    def ponteiros(self):
        valor = []
        for i in range(0, len(self.list_elementos), 2):
            if(self.list_elementos[i] != VAZIO):
                valor.append(self.list_elementos[i])
            else:
                valor.append(" ")
        if self.isLeaf == True:
            return valor[0:-1]
        else:
            return valor

"""
    Classe para a Árvore
"""
class BplusTree:
    def __init__(self, root, ordem):
        self.root = root
        self.ordem = ordem
        self.altura = 1

    """
        Função de inserção, ela chama as outras funções auxiliares
        de inserção sempre.
        value é o próprio valor a ser inserido.
    """
    def insert(self, value):
        next_node = self.root

        while(next_node.isLeaf != True):
            for i in range (1, len(next_node.list_elementos), 2):
                if(value < next_node.list_elementos[i]):

                    next_node = next_node.list_elementos[i - 1]
                    flag = False # significa que não é o último
                    break
                elif((i + 2) >= len(next_node.list_elementos)):
                    next_node = next_node.list_elementos[i + 1]
                    break


        # nodo está cheio, precisa ser feito algo
        if(next_node.real_len() == (self.ordem - 1)):

            new_node = node(next_node.father, False, True, self.ordem) # novo
            node_temp = node(next_node.father, False, True, self.ordem) # temporário

            for i in range(0, len(next_node.list_elementos) - 1): # copia tudo pro temporário
                node_temp.list_elementos[i] = next_node.list_elementos[i]

            node_temp = self.insert_in_leaf(node_temp, value)
            node_temp.list_elementos.pop() # pra desconsiderar o VAZIO no final

            new_node.list_elementos[-1] = next_node.list_elementos[-1]
            next_node.list_elementos[-1] = new_node

            next_node.erase()

            cont_elementos = math.ceil(self.ordem/2)   # pra pegar a posição exata até onde ir no vetor

            y = 0 # y assumirá posição exata depois desse laço
            for i in range(0, len(node_temp.list_elementos)):
                if(i % 2 == 1):
                    y += 1    # conta a quantidade de elementos
                    if(y == cont_elementos):
                        y = i # depois assume o valor da posição
                        break

            for i in range(0, y + 1):
                next_node.list_elementos[i] = node_temp.list_elementos[i]

            cont_ponteiro = math.ceil(self.ordem/ 2) + 1

            x = 0
            for i in range(0, len(node_temp.list_elementos)):
                if(i % 2 == 0):
                    x += 1
                    if(x == cont_ponteiro):
                        x = i
                        break

            b = 0
            for i in range(x, len(node_temp.list_elementos)):
                new_node.list_elementos[b] = node_temp.list_elementos[i]
                b += 1


            self.insert_in_father(next_node, new_node.list_elementos[1], new_node)

        else:
            self.insert_in_leaf(next_node, value)

    """
        Insere em nós folha.
        node é o nó folha a receber o valor.
        value é o próprio valor.
        retorna o nó folha atualizado.
    """
    def insert_in_leaf(self, node, value):
        temp = []
        x = 1
        for i in range(0, node.real_len()): # copia tudo pra um vetor auxiliar
            temp.append(node.list_elementos[x])
            x += 2

        temp.append(value) # adiciona o valor novo
        temp.sort() # deixa em ordem

        x = 1

        for i in range(0, len(temp)):
            if(x >= len(node.list_elementos)):
                node.list_elementos.append(temp[-1])
                node.list_elementos.append(VAZIO)
                #print(node.list_elementos)
                break

            node.list_elementos[x] = temp[i] # coloca no vetor do node
            x += 2

        return node

    """
        Inserção no pai, ou em qualquer nó intermediário/raiz pra ser mais específico
        node1 é o nó à esquerda
        value é o valor em si a ser inserido
        node2 é o valor à direita
    """
    def insert_in_father(self, node1, value, node2):
        if(node1.isRoot):
            node1.isRoot = False
            new_root = node("null", True, False, self.ordem)
            new_root.list_elementos[0] = node1
            new_root.list_elementos[1] = value

            new_root.list_elementos[2] = node2
            self.root = new_root
            self.definir_pai(self.root.list_elementos[0], self.root) # atualiza os pais
            self.definir_pai(self.root.list_elementos[2], self.root)
            self.altura += 1
            return

        father = node1.father

        if(father.qtd_pointers() < self.ordem): # basta inserir
            indice = father.list_elementos.index(node1)
            father.list_elementos.insert(indice + 1, node2)
            father.list_elementos.insert(indice + 1, value)
            # tira os VAZIO extra
            father.list_elementos.pop()
            father.list_elementos.pop()


            self.definir_pai(node2, father) # atualiza os pais afinal foi mexido as coisa
            return

        # quebra o pai em dois
        else:
            temp = []
            for i in range(0, len(father.list_elementos)): # copia tudo do pai1 pra um temporário
                temp.append(father.list_elementos[i])

            indice = father.list_elementos.index(node1)
            # adiciona o novo nodo no pai
            temp.insert(indice + 1, node2)
            temp.insert(indice + 1, value)

            father.erase()

            father2 = node("null", False, False, self.ordem)

            ######### SEPARA O PAI ##################
            cont_elementos = math.ceil(self.ordem/2)   # pra pegar a posição exata até onde ir no vetor

            y = 0 # y assumirá posição exata depois desse laço
            for i in range(0, len(temp)):
                if(i % 2 == 0):
                    y += 1    # conta a quantidade de elementos
                    if(y == cont_elementos):
                        y = i # depois assume o valor da posição
                        break

            for i in range(0, y + 1):
                father.list_elementos[i] = temp[i] # coloca até o valor correto no nodo a esquerda

            value = temp[y + 1]
            y += 2
            b = 0
            for i in range(y, len(temp)):
                father2.list_elementos[b] = temp[i] # resto pro nodo a direita
                b += 1
            # recursividade pra saber o que fazer com os novos nodos

            self.insert_in_father(father, value, father2)

    """
        Atualiza os pais dos nodos de forma recursiva
        Não retorna algo após sua recursividade.
    """
    def definir_pai(self, node_atual, node_anterior):
        if(node_atual.isLeaf): # para folha
            node_atual.father = node_anterior
            return
        elif(node_atual.isLeaf == False and node_atual.isRoot == False): # intermediários
            node_atual.father = node_anterior
            for i in range(0, len(node_atual.list_elementos), 2):
                if(node_atual.list_elementos[i] != VAZIO): # faz isso em todos os nós filhos
                    self.definir_pai(node_atual.list_elementos[i], node_atual)

    """
        Delete inicial, basicamente responsável por encontrar
        qual nó possivelmente contém o valor a ser deletado, e chama a recursividade
        value é o próprio valor.
    """
    def delete(self, value):
        indice, node_param = self.search(value)

        if(not indice):

            return False
        else:
            # kuro mahou
            self.delete_recursive(node_param, node_param.list_elementos[indice])
            return True

    """
        Deleção recursiva. Novamente ela faz todos os tratamentos e age de acordo.
        node_param é o nó a ser analisado para deleção.
        value é o valor a ser deletado
    """
    def delete_recursive(self, node_param, value):

        node_param = self.delete_in_node(node_param, value)

        if(node_param.isRoot and node_param.qtd_pointers() == 0 and node_param.real_len() == 0): # árvore vazia
            return

        elif(node_param == -1): # valor não existe na árvore
            return

        elif(node_param.isRoot and node_param.isLeaf):
            return

        # verifica se o nó está em underflow
        elif((node_param.real_len() < math.ceil((self.ordem - 1)/2) and node_param.isLeaf) or (node_param.qtd_pointers() <= 1 and node_param.isLeaf == False)):

            if(node_param.isRoot != True):
                father = node_param.father
                index_node = father.list_elementos.index(node_param)
                # verifica se existe nós irmaõs
                if(index_node - 2 < 0):
                    left_brother = node("null", "null", "null", 15) # padrão retardado pra "não existe"
                else:
                    left_brother = father.list_elementos[index_node - 2]

                if(index_node + 2 > len(father.list_elementos) - 1):
                    right_brother = node("null", "null", "null", 15)
                else:
                    right_brother = father.list_elementos[index_node + 2]
                    if(right_brother == VAZIO):
                        right_brother = node("null", "null", "null", 15)

                minimal_leaf = math.ceil((self.ordem - 1)/2)

                if(node_param.isLeaf):
                    # segue o algoritmo pra verificar se precisa um merge ou um shift
                    if((left_brother.ordem != 15 and left_brother.real_len() == minimal_leaf)):
                        self.merge_leaf(node_param, left_brother, LEFT)

                    elif((right_brother.ordem != 15 and right_brother.real_len() == minimal_leaf)):
                        self.merge_leaf(node_param, right_brother, RIGHT)

                    else:
                        if(left_brother.real_len() > minimal_leaf):
                            self.shift_value(node_param, left_brother, LEFT)

                        else:
                            self.shift_value(node_param, right_brother, RIGHT)

                # nó em questão é intermediário, mesmas funções porém modelo intermediário
                else:
                    if((left_brother.ordem != 15 and left_brother.real_len() < self.ordem - 1)): # executa 99% das vezes
                        self.merge_intermediate(node_param, left_brother, LEFT)

                    elif((right_brother.ordem != 15 and right_brother.real_len() < self.ordem - 1)):
                        self.merge_intermediate(node_param, right_brother, RIGHT)

                    else:
                        if(left_brother.real_len() == self.ordem - 1):
                            self.shift_value_intermediate(node_param, left_brother, LEFT)

                        else:
                            self.shift_value_intermediate(node_param, right_brother, RIGHT)

            # nó é uma árvore então, e está quase vazia
            else:
                for i in range(0, len(node_param.list_elementos), 2):
                    if(node_param.list_elementos[i] != VAZIO):
                        node_sobrou = node_param.list_elementos[i]
                        break
                node_sobrou.isRoot = True
                node_sobrou.father = "null"

                if(node_sobrou.qtd_pointers() == 0):
                    node_sobrou.isLeaf = True

                del node_param # por estar vazia, deletada será
                self.root = node_sobrou
                self.altura -= 1
                return

        # reorganiza referências quando o nó for intermediário ou raiz
        elif((node_param.isRoot == False and node_param.isLeaf != True) or (node_param.isRoot and node_param.isLeaf != True)):
            if(node_param.list_elementos[0] == VAZIO and node_param.list_elementos[1] != VAZIO):
                node_param.list_elementos[0] = node_param.list_elementos[2]
                node_param.list_elementos[2] = VAZIO
            for i in range(2, len(node_param.list_elementos), 2):
                if(node_param.list_elementos[i - 1] != VAZIO  and node_param.list_elementos[i] == VAZIO):
                    node_param.list_elementos[i] = node_param.list_elementos[i + 2]
                    node_param.list_elementos[i + 2] = VAZIO


    """
        Função que dá merge em folhas na hora das deleções, sempre que necessário
        node é o nó que teve o valor deletado
        brother é o irmão escolhido que vai receber o resto dos valores de node
        sentido é só para dizer se o irmão é esquerda ou direita
    """
    def merge_leaf(self, node, brother, sentido):
        father = node.father
        temp = []
        # copia todos os elementos de ambos os nós para um vetor temporário
        for i in range(1, len(brother.list_elementos), 2):
            if(brother.list_elementos[i] != VAZIO):
                temp.append(brother.list_elementos[i])

        for i in range(1, len(node.list_elementos), 2):
            if(node.list_elementos[i] != VAZIO):
                temp.append(node.list_elementos[i])

        temp.sort()

        if(sentido == LEFT):
            # lado direito é privilegiado, ele que vai receber os valores
            brother.erase()


            x = 1
            for i in range(0, len(temp)):
                brother.list_elementos[x] = temp[i]
                x += 2

            index_node = father.list_elementos.index(node)
            father.list_elementos[index_node] = VAZIO # apaga a referência pro nó antigo no pai

            # chama recursão deletando o elemento separador dos nós
            self.delete_recursive(father, father.list_elementos[index_node - 1])

        elif(sentido == RIGHT):
            # lado direito privilegiado novamente
            node.erase()

            x = 1
            for i in range(0, len(temp)):
                node.list_elementos[x] = temp[i]
                x += 2

            index_brother = father.list_elementos.index(brother)
            father.list_elementos[index_brother] = VAZIO

            self.delete_recursive(father, father.list_elementos[index_brother - 1])

    """
        Função que passa o valor a ser emprestado do nó irmão para o que precisa
        node é o nó que vai receber o valor
        brother é o irmão que tá pagando
        sentido é qual dos dois irmãos vai pagar
    """
    def shift_value(self, node, brother, sentido):
        if(sentido == LEFT):
            indice_maior = 0

            # como o da esquerda é o escolhido, o maior é o mais à direita
            for i in range(1, len(brother.list_elementos), 2):
                if(brother.list_elementos[i] == VAZIO):
                    indice_maior = i - 2
                    break
                elif((i + 2) >= len(brother.list_elementos)):
                    indice_maior = i
                    break

            maior_valor = brother.list_elementos[indice_maior]

            brother.list_elementos[indice_maior] = VAZIO # deleta o maior valor

            # insere ambos os valores no nó que tá recebendo
            node.list_elementos.insert(0, maior_valor)
            node.list_elementos.insert(0, VAZIO)
            # guarda a referência ao nó à direita
            temp = node.list_elementos[-1]
            # retira o excesso de dados no nó, para manter a consistência
            node.list_elementos.pop()
            node.list_elementos.pop()
            node.list_elementos[-1] = temp

            # atualiza o valor entre nós no pai
            father = node.father
            print(father)
            father.list_elementos[father.list_elementos.index(node) - 1] = maior_valor
            return

        else:
            # como o à direita o que deve ser emprestado é o menor valor, isso facilita
            menor_valor = brother.list_elementos[1]
            brother.list_elementos[1] = VAZIO # simplesmente deleta

            # coloca o menor valor da direita como maior da esquerda
            for i in range(1, len(node.list_elementos), 2):
                if(node.list_elementos[i] == VAZIO):
                    node.list_elementos[i] = menor_valor
                    node.list_elementos[i + 1] = brother.list_elementos[0]
                    break

            # guarda a referência ao nó à direita
            temp = brother.list_elementos[-1]
            # como a lista fica com dois VAZIO no início após os procedimentos
            # anteriores, ambos são removidos, um VAZIO a mais é colocado e a referência é recolocada
            brother.list_elementos[-1] = VAZIO
            brother.list_elementos[0] = VAZIO
            brother.list_elementos.remove(VAZIO)
            brother.list_elementos.remove(VAZIO)
            brother.list_elementos.append(VAZIO)
            brother.list_elementos.append(temp)

            father = brother.father
            father.list_elementos[father.list_elementos.index(brother) - 1] = brother.list_elementos[1]
            return

    """
        Semelhante a merge_leaf, porém com algoritmo modificado para nós intermediários
        node é o nó que está em underflow
        brother nó irmão a receber o com underflow
        sentido qual dos irmãos foi escolhido
    """
    def merge_intermediate(self, node, brother, sentido):
        father = node.father
        # pega o nó filho que sobrou do que está em underflow
        for i in range(0, len(node.list_elementos)):
            if(node.list_elementos[i] != VAZIO):
                node_sobrou = node.list_elementos[i]
                break

        if(sentido == LEFT):
            # irmão escolhido é o esquerdo, então o elemento separador está à eqsuerda do nó underfull
            indice_elemento = father.list_elementos.index(node) - 1

            # elemento mais à direita do irmão recebe o valor do elemento separador entre os nós no pai
            for i in range(1, len(brother.list_elementos), 2):
                if(brother.list_elementos[i] == VAZIO):
                    brother.list_elementos[i] = father.list_elementos[indice_elemento]
                    brother.list_elementos[i + 1] = node_sobrou # ponteiro à direita é o nó que sobrou do antigo
                    break


            father.list_elementos[indice_elemento + 1] = VAZIO # deleta referência ao nó que sobrou
            # chama recursividade para deletar o elemento que antes era o separador
            self.delete_recursive(father, father.list_elementos[indice_elemento])

        else:
            # irmão escolhido é o direito, logo elemento separador é o à direita do nó underfull
            indice_elemento = father.list_elementos.index(node) + 1
            # insere a referência ao nó que sobrou e o separador dos nós no pai, no irmão
            brother.list_elementos.insert(0, father.list_elementos[indice_elemento])
            brother.list_elementos.insert(0, node_sobrou)
            #retirada dos dois VAZIO ao final do nó, que sobraram após a inserção acima
            brother.list_elementos.pop()
            brother.list_elementos.pop()

            father.list_elementos[indice_elemento - 1] = VAZIO # deleta a referência ao nó antigo

            self.delete_recursive(father, father.list_elementos[indice_elemento])

    """
        Empréstimo de valores, porém entre nós intermediários. Semelhante à shift_value, porém adaptado.
        node nó que receberá o valor
        brother nó que empresta o valor
        sentido qual dos irmãos está emprestando
    """
    def shift_value_intermediate(self, node, brother, sentido):
        father = node.father
        for i in range(0, len(node.list_elementos)): # pega o nó filho sobrando do nó underfull
            if(node.list_elementos[i] != VAZIO):
                node_sobrou = node.list_elementos[i]
                break

        if(sentido == LEFT):
            # irmão à esquerda, separador no pai está a um índice a menos da referência ao nó underfull
            index_node = father.list_elementos.index(node)
            elemento = father.list_elementos[index_node - 1]

            node.list_elementos[2] = node.list_elementos[0]
            # elemento separador no pai desce para o filho underfull
            node.list_elementos[1] = elemento
            node.list_elementos[0] = brother.list_elementos[-1] # referência à direita do irmão
            brother.list_elementos[-1] = VAZIO
            # elemento mais à direita no irmão sobe para o pai
            elemento_brother = brother.list_elementos[-2]
            father.list_elementos[index_node - 1] = elemento_brother
            brother.list_elementos[-2] = VAZIO
            return

        else:
            print(node.list_elementos)
            index_node = father.list_elementos.index(node)
            indice_sobrou = node.list_elementos.index(node_sobrou)
            # passagem para esquerda do nó que sobrou
            node.list_elementos[0] = node_sobrou

            #node.list_elementos[indice_sobrou] = VAZIO # deleção da referência antiga
            # passagem do elemento separador para o nó antes underfull
            elemento = father.list_elementos[index_node + 1]
            node.list_elementos[1] = elemento
            node.list_elementos[2] = brother.list_elementos[0]

            elemento_brother = brother.list_elementos[1]
            father.list_elementos[index_node + 1] = elemento_brother
            # remoção dos dois primeiros valores de brother (que agora são VAZIO mesmo)
            # e appendo de dois VAZIO no final para manter a consistência
            brother.list_elementos.remove(brother.list_elementos[0])
            brother.list_elementos.remove(brother.list_elementos[0])
            brother.list_elementos.append(VAZIO)
            brother.list_elementos.append(VAZIO)
            return

    """
        Deleta o valor no node específico.
        returna -1 caso o valor não exista, ou o nó modificado caso sim
    """
    def delete_in_node(self, node, value):
        try:
            temp = []
            x = 1
            for i in range(0, node.real_len()): # copia tudo pra um vetor auxiliar
                temp.append(node.list_elementos[x])
                x += 2

            temp[temp.index(value)] = VAZIO

            temp.sort()

            x = 1
            for i in range(0, len(temp)):
                node.list_elementos[x] = temp[i] # coloca no vetor do node
                x += 2

            return node

        except ValueError:
            return -1

    """
        Procura o valor value na árvore.
        retorna dois valores:
        Caso encontrado:
        [índice do elemento no nó que foi encontrado, nó folha que possui o elemento]
        Caso não:
        [False, False]

    """
    def search(self, value):
        next_node = self.root

        while(next_node.isLeaf != True):
            for i in range (1, len(next_node.list_elementos), 2):
                if(value < next_node.list_elementos[i]):

                    next_node = next_node.list_elementos[i - 1]
                    break

                elif((i + 2) >= len(next_node.list_elementos)):
                    next_node = next_node.list_elementos[i + 1]
                    break

        for i in range(1, len(next_node.list_elementos), 2):
            if(next_node.list_elementos[i] == value):
                return i, next_node

        return False, False

    """
        Função recursiva que retorna TODOS os filhos da árvore em um
        determinado nível especificado. É utilizada somente como recurso para
        a visualização da árvore nas funções de desenho. Parâmetros:
        lista = lista inicial, quando chamada fora da recursão é SEMPRE uma lista vazia.
        Quando chamada na recursão, é a formação da lista que será retornada.
        node_param = nó que está sendo considerado. Quando chamado fora da recursão, é
        SEMPRE a raiz da árvore, pois é dela que se consegue a referência aos outros nós.
        Na recursão, é o nó que está sendo considerado.
        nivel_desejado = auto explicativo.
        nivel_atual = qual nível que a recursão tá. Quando chamado fora, SEMPRE será 1
        Retorna uma lista contendo os filhos de todos nó, incluindo " " para quando não existir aquele filho.
    """
    def retorna_nos(self, lista, node_param, nivel_desejado, nivel_atual):
        if(nivel_atual == nivel_desejado): # passo não recursivo
            for i in range(0, len(node_param.list_elementos), 2): # verifica todos os filhos daquele nó
                if(node_param.list_elementos[i] == VAZIO):
                    lista.append(" ")
                else:
                    lista.append(node_param.list_elementos[i])

            return lista # e retorna a lista pra cima

        else: # para quando o nível não é o desejado
            for i in range(0, len(node_param.list_elementos), 2): # vai passando por todos os filhos até chegar no nível desejado

                if(node_param.list_elementos[i] == VAZIO):
                    # pequeno truque para quando algum nó no nível não-desejado não possui todos os filhos
                    for b in range(0, self.ordem ** (nivel_desejado - nivel_atual)):
                        lista.append(" ")

                else:
                    # desce mais um nível!
                    lista = (self.retorna_nos(lista, node_param.list_elementos[i], nivel_desejado, nivel_atual + 1))

                if(i == (len(node_param.list_elementos) - 1) ): # acabou de passar nos filhos daquele nó, retorna pra cima
                    return lista



class Interface(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Simulação Árvore B+")

        box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.add(box)
        grid2 = Gtk.Grid()
        box.pack_start(grid2, False, False, 0)

        # Entradas e botões
        self.entrada_insere = Gtk.Entry()
        self.entrada_insere.connect("activate", self.inserir)
        self.entrada_insere.set_max_length(3)

        self.botao_insere = Gtk.Button(label = "Inserir")
        self.botao_insere.connect("clicked", self.inserir)
        grid2.attach(self.entrada_insere, 0,0,  1, 1)
        grid2.attach(self.botao_insere, 0,1,  1, 1)

        self.entrada_deleta = Gtk.Entry()
        self.entrada_deleta.connect("activate", self.deletar)
        self.entrada_deleta.set_max_length(3)
        self.botao_deleta = Gtk.Button(label = "Deletar")
        self.botao_deleta.connect("clicked", self.deletar)
        grid2.attach(self.entrada_deleta, 0,2,  1, 1)
        grid2.attach(self.botao_deleta, 0,3,  1, 1)


        self.entrada_busca = Gtk.Entry()
        self.entrada_busca.connect("activate", self.buscar)
        self.entrada_busca.set_max_length(3)
        self.botao_busca = Gtk.Button(label = "Buscar")
        self.botao_busca.connect("clicked", self.buscar)
        grid2.attach(self.entrada_busca, 0,4,  1, 1)
        grid2.attach(self.botao_busca, 0,5,  1, 1)

        # ComboBox pra ordem
        label_ordem = Gtk.Label("Ordem:")
        grid2.attach(label_ordem, 0,6,  1, 1)

        ordem = ["3", "4", "5", "6", "7", "8", "9", "10"]
        ordem_combo = Gtk.ComboBoxText()
        ordem_combo.set_entry_text_column(0)

        for i in ordem:
            ordem_combo.append_text(i)

        ordem_combo.set_active(0)
        ordem_combo.connect("changed", self.ordem_combo_changed)
        grid2.attach(ordem_combo, 0,7,  1, 1)

        # Números aleatórios
        label_de = Gtk.Label("Mínimo Intervalo:")

        self.entry_min = Gtk.Entry()
        self.entry_min.set_max_length(3)

        label_ate = Gtk.Label("Máximo Intervalo:")

        self.entry_max = Gtk.Entry()
        self.entry_max.set_max_length(3)

        label_qtd = Gtk.Label("Quantidade:")

        self.entry_qtd = Gtk.Entry()
        self.entry_qtd.connect("activate", self.inserir_aleatorios)
        self.entry_qtd.set_max_length(3)
        self.entry_qtd.set_size_request(0, 10)


        insert_random = Gtk.Button(label = "Inserir Aleatórios")
        insert_random.connect("clicked", self.inserir_aleatorios)

        grid2.attach(label_de,0, 8,  1, 1)
        grid2.attach(self.entry_min,0, 9,  1, 1)
        grid2.attach(label_ate, 0,10,  1, 1)
        grid2.attach(self.entry_max, 0,11,  1, 1)
        grid2.attach(label_qtd, 0,12,  1, 1)
        grid2.attach(self.entry_qtd, 0,13,  1, 1)
        grid2.attach(insert_random, 0,14,  1, 1)
        grid2.set_row_spacing(4)

        self.button_step = Gtk.Button(label = "Step")
        self.button_step.connect("clicked", self.step)
        grid2.attach(self.button_step, 0, 15, 1, 1)

        label_canvas = Gtk.Label("Tamanho do Canvas:")
        grid2.attach(label_canvas, 0, 16, 1, 1)
        self.entry_canvas = Gtk.Entry()
        self.entry_canvas.connect("activate", self.set_canvas)
        grid2.attach(self.entry_canvas, 0, 17, 1, 1)

        #canvas
        self.drawing = Gtk.DrawingArea()
        self.drawing.connect("draw", self.ver_arvore)
        self.large=1500
        self.drawing.set_size_request(self.large, 650)
        self.flag_canvas_size = True

        self.scroll = Gtk.ScrolledWindow(hexpand = True, vexpand = True)
        box.pack_start(self.scroll, True, True, 0)
        self.viewport = Gtk.Viewport()
        self.scroll.add(self.viewport)
        self.viewport.add(self.drawing)
        self.viewport.show()
        self.scroll.show()

        self.connect("delete-event", Gtk.main_quit)

        self.numero2 = VAZIO
        self.ordem_combo_changed(ordem_combo)
        self.set_default_size(1200, 450)
        self.show_all()

    def set_canvas(self, entry):
        self.large = int(self.entry_canvas.get_text())
        self.entry_canvas.set_text("")
        print(self.large)
        self.flag_canvas_size = False
        self.drawing.set_size_request(self.large, 650)
        #self.viewport.queue_draw()
        #self.scroll.queue_draw()
        #self.queue_draw()

    def step(self, button):
        print("Feijoada, NAO DA PRA FAZER ISSO MERMAO AAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHH")

    def dialog_insercao(self):
        popup = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Elemento Repetido!")
        popup.format_secondary_text("O elemento que você está tentando adicionar já se encontra na árvore!")
        popup.run()
        popup.destroy()

    def ordem_combo_changed(self, combo):
        self.ordem_tree = int(combo.get_active_text())
        root = node("null", True, True, self.ordem_tree)
        self.tree = BplusTree(root, self.ordem_tree)
        self.flag_canvas_size = True
        self.viewport.queue_draw()

    def inserir(self, button):
        self.numero2 = VAZIO
        add = int(self.entrada_insere.get_text())
        self.entrada_insere.set_text("")
        teste, teste2 = self.tree.search(add)
        if(teste != False): # verifica se o elemento já se encontra na árvore
            self.dialog_insercao()
            return

        self.tree.insert(add)
        self.flag_canvas_size = False
        for i in range(0, len(self.tree.root.list_elementos), 2):
            if(self.tree.root.list_elementos[i] != VAZIO):
                self.tree.definir_pai(self.tree.root.list_elementos[i], self.tree.root)

        self.viewport.queue_draw()

    def inserir_aleatorios(self, button):
        self.numero2 = VAZIO
        minimo = int(self.entry_min.get_text())
        maximo = int(self.entry_max.get_text())
        qtd = int(self.entry_qtd.get_text())

        self.entry_min.set_text("")
        self.entry_max.set_text("")
        self.entry_qtd.set_text("")
        self.flag_canvas_size = False
        for i in range(0, qtd):
            rand = randint(minimo, maximo)
            teste, teste2 = self.tree.search(rand)
            while(teste != False):
                rand = randint(minimo, maximo)
                teste, teste2 = self.tree.search(rand)

            self.tree.insert(rand)
            for i in range(0, len(self.tree.root.list_elementos), 2):
                if(self.tree.root.list_elementos[i] != VAZIO):
                    self.tree.definir_pai(self.tree.root.list_elementos[i], self.tree.root)

            self.viewport.queue_draw()



    def deletar(self, button):
        self.numero2 = VAZIO
        numero = int(self.entrada_deleta.get_text())
        self.entrada_deleta.set_text("")
        self.flag_canvas_size = False
        if(not self.tree.delete(numero)):
            self.chamar_dialog()
            return

        for i in range(0, len(self.tree.root.list_elementos), 2):
            if(self.tree.root.list_elementos[i] != VAZIO):
                self.tree.definir_pai(self.tree.root.list_elementos[i], self.tree.root)
        self.viewport.queue_draw()


    def chamar_dialog(self):
        popup = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Erro de busca!")
        popup.format_secondary_text("Elemento não encontrado na árvore!")
        popup.run()
        popup.destroy()

    def buscar(self, widget):

        self.numero2 = int(self.entrada_busca.get_text())
        self.entrada_busca.set_text("")
        indice, node = self.tree.search(self.numero2)
        self.flag_canvas_size = False
        if(not node):
            self.chamar_dialog()
        else:
            node.busca_flag = True
            self.viewport.queue_draw()
            node.busca_flag = False



    def ver_arvore(self, janela, cr):
        #cr.set_source_rgb(2, 2, 255)
        self.draw_no(cr,self.ordem_tree,self.large/2,10,self.tree.root,1,0)

        cr.stroke()


    def draw_no(self, cr, ordem, ini_x, ini_y, no, nivel,anterior):
        linhas_fim=[]
        if ordem > 7:
            espa=200
            tam=135
            cr.set_font_size(7)
            if(self.flag_canvas_size):
                self.large=6000
                self.drawing.set_size_request(self.large, 650)
        elif ordem > 6:
            espa=200
            tam=135
            cr.set_font_size(7)
            if(self.flag_canvas_size):
                self.large=6000
                self.drawing.set_size_request(self.large, 650)
        elif ordem > 5:
            espa=200
            tam=135
            cr.set_font_size(7)
            if(self.flag_canvas_size):
                self.large=5500
                self.drawing.set_size_request(self.large, 650)
        elif ordem >4:
            espa=150
            tam=92
            cr.set_font_size(9)
            if(self.flag_canvas_size):
                self.large=2500
                self.drawing.set_size_request(self.large, 650)
        elif ordem >0:
            espa=100
            if(self.flag_canvas_size):
                self.large=1500
                self.drawing.set_size_request(self.large, 650)
            tam=70
            cr.set_font_size(10)
        if ordem == 3:
            tam=50
            cr.set_font_size(12)


        num=ordem**nivel+1

        linhas_fim= list(range(0,self.large-10,round(self.large/(num))))
        linhas_fim= linhas_fim[1:]


        pontos_h=[]
        pontos_h= range(round(ini_x-(tam/2)),round(ini_x+(tam/2)+5),round(tam/(ordem-1))) #separa o nó
        cr.set_line_width(2)
        if no.busca_flag == True and no.isLeaf == True:
            cr.set_source_rgb(0, 1, 0)
            print("work?")
        else:
            cr.set_source_rgb(0, 0, 0)

        cr.move_to(pontos_h[0], ini_y)
        cr.line_to(pontos_h[-1],ini_y)
        cr.move_to(pontos_h[0], ini_y+20)
        cr.line_to(pontos_h[-1],ini_y+20)
        cr.stroke()

        #cria divisoes
        for x in pontos_h:
            cr.move_to(x, ini_y)
            cr.set_line_width(2)
            cr.line_to(x,ini_y+20)
        ele=[]
        ele=no.elementos()
        ##cria os text
        for i in range(0,len(pontos_h)-1):
            if ele[i] == self.numero2 and no.isLeaf == True:
                cr.set_source_rgb(0, 0, 1)
            else:
                cr.set_source_rgb(1, 0, 0)
            cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            cr.move_to(pontos_h[i]+((tam/ordem)/4 -1), ini_y+13)
            cr.show_text(str(ele[i]))
            cr.set_source_rgb(0, 0, 0)


        antes=[]
        if nivel > 1:
            for i in anterior:
                a=list(range(round(i-(tam/2)),round(i+(tam/2)+5),round(tam/(ordem-1))))
                for b in a:
                    antes.append(b)
        else:
            antes=pontos_h

        pon=[]

        pon= self.tree.retorna_nos( [], self.tree.root, nivel,1)

        for p in range(len(pon)):
            if pon[p] != " ":
                #recursão
                self.draw_no(cr,ordem,linhas_fim[p],ini_y+espa,pon[p],nivel+1,linhas_fim)
                #cria as setas
                cr.set_line_width(2)
                cr.move_to(linhas_fim[p],ini_y+espa)
                cr.line_to(antes[p],ini_y+20)
        #cr.rectangle(ini_x-50,ini_y, 100, 30)
        #cr.fill()




tela = Interface()
#tela.connect("notify::is-active", tela.focus_in)
Gtk.main()
