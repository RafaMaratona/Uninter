# ==================== CALCULADORA ====================
import json
import re
import math
import os
import sys
from fractions import Fraction
from sympy import (
    symbols, Eq, solve, SympifyError,
    sin as sym_sin, cos as sym_cos, tan as sym_tan,
    asin as sym_asin, acos as sym_acos, atan as sym_atan,
    sqrt as sym_sqrt, log as sym_log, log10 as sym_log10, exp as sym_exp,
    pi as sym_pi, E as sym_e, Abs as sym_abs,
    floor as sym_floor, ceiling as sym_ceil # SymPy usa ceiling para ceil
)
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    convert_xor,
)

# Transformações do parse_expr para o modo Solve
# standard_transformations — base do parser do sympy
# convert_xor              — converte ^ para potência automaticamente
# implicit_multiplication_application foi removida para evitar conflitos
TRANSFORMACOES_SYMPY = standard_transformations + (convert_xor,)

# Dicionário de funções e constantes do SymPy para o parse_expr
# Mapeia strings para os objetos SymPy correspondentes
SYMPY_LOCAL_DICT = {
    "sin": sym_sin, "cos": sym_cos, "tan": sym_tan,
    "sen": sym_sin, "tg": sym_tan, # Aliases em PT-BR
    "asin": sym_asin, "acos": sym_acos, "atan": sym_atan,
    "sqrt": sym_sqrt, "raiz": sym_sqrt,
    "log": sym_log, "log10": sym_log10, "exp": sym_exp,
    "pi": sym_pi, "e": sym_e,
    "abs": sym_abs, "floor": sym_floor, "ceil": sym_ceil,
    # rad e graus serão tratados por regex, não como funções diretas do sympy
}

# ==================== VARIÁVEIS GLOBAIS ====================
Titulo1 = "Calculadora"
NumCaracRafa1 = 200
NumCaracRafa2 = NumCaracRafa1 // 2
Subtitulo1 = "Explicação"
M1 = None
M2 = None
memorias_definidas = {}

configuracoes = {
    "modo_resultado": "auto",
    "casas_decimais": 4,
}

# ==================== FORMATAÇÃO VISUAL ====================

def formatrafa1():
    print("=" * NumCaracRafa1)
    print(f"{Titulo1:^{NumCaracRafa1}}")
    print("=" * NumCaracRafa1)

def formatrafa2(subtitulo):
    nb = abs(len(subtitulo) - NumCaracRafa1)
    print(f"{subtitulo}{'-' * nb}")
    print("=" * NumCaracRafa1)

# ==================== FORMATAÇÃO DE RESULTADO ====================

def formatar_resultado(valor):
    if isinstance(valor, bool):
        return str(valor)

    modo  = configuracoes["modo_resultado"]
    casas = configuracoes["casas_decimais"]

    try:
        valor_float = float(valor)
    except Exception:
        return str(valor)

    if modo == "inteiro":
        return str(int(round(valor_float)))
    elif modo == "decimal":
        return f"{valor_float:.{casas}f}"
    elif modo == "cientifico":
        return f"{valor_float:.{casas}e}"
    elif modo == "fracao":
        frac = Fraction(valor_float).limit_denominator(10 ** casas)
        if frac.denominator == 1:
            return str(frac.numerator)
        return f"{frac.numerator}/{frac.denominator}"
    else:
        if valor_float == int(valor_float):
            return str(int(valor_float))
        return f"{valor_float:.{casas}f}"

def formatar_solucao_solve(sol):
    modo  = configuracoes["modo_resultado"]
    casas = configuracoes["casas_decimais"]

    try:
        if not (sol.is_real and sol.is_number):
            return str(sol), None

        valor_float = float(sol)

        if modo == "inteiro":
            return str(int(round(valor_float))), valor_float
        elif modo == "decimal":
            return f"{valor_float:.{casas}f}", valor_float
        elif modo == "cientifico":
            return f"{valor_float:.{casas}e}", valor_float
        elif modo == "fracao":
            frac = Fraction(valor_float).limit_denominator(10 ** casas)
            if frac.denominator == 1:
                return str(frac.numerator), valor_float
            return f"{frac.numerator}/{frac.denominator}", valor_float
        else:
            if valor_float == int(valor_float):
                return str(int(valor_float)), valor_float
            return f"{valor_float:.{casas}f}", valor_float

    except Exception:
        return str(sol), None

# ==================== VALIDAÇÃO DE ENTRADA ====================

def entrada_parece_valida(texto):
    caracteres_invalidos = [".exe", "Scripts\\python", "venv\\Scripts"]
    for invalido in caracteres_invalidos:
        if invalido.lower() in texto.lower():
            return False
    return True

# ==================== LIMPEZA DE BUFFER ====================

def limpar_buffer():
    if os.name == 'nt':
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()

# ==================== CONTEXTO MATEMÁTICO ====================

def montar_contexto():
    contexto = {
        '__builtins__': {},
        'sin':  math.sin,
        'cos':  math.cos,
        'tan':  math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'sen':    math.sin,
        'tg':     math.tan,
        'cossec': lambda x: 1 / math.sin(x),
        'cotg':   lambda x: math.cos(x) / math.sin(x),
        'sqrt': math.sqrt,
        'raiz': math.sqrt,
        'log':   math.log,
        'log10': math.log10,
        'exp':   math.exp,
        'rad':   math.radians,
        'graus': math.degrees,
        'pi': math.pi,
        'e':  math.e,
        'abs':   abs,
        'round': round,
        'floor': math.floor,
        'ceil':  math.ceil,
    }
    for nome, valor in memorias_definidas.items():
        contexto[f"mv_{nome}"] = valor
    return contexto

# ==================== EXPLICAÇÕES ====================

def ExplicacaoMultiplicacao():
    print("Neste sistema, a multiplicação é representada pelo símbolo:  *")
    print("Exemplo: 3 * 4 significa 3 × 4 = 12")
    print("Use o asterisco (*) sempre que quiser multiplicar dois valores.")

def ExplicacaoDivisao():
    print("Neste sistema, a divisão é representada pelo símbolo:  /")
    print("Exemplo: 12 / 4 significa 12 ÷ 4 = 3")
    print("Use a barra (/) sempre que quiser dividir dois valores.")
    print("Lembre: divisão por zero ( / 0 ) não é permitida.")

def ExplicacaoPotencia():
    print("Neste sistema, a potência é representada por:  ^")
    print("Exemplo: 2 ^ 3  significa 2³ = 8")

def ExplicacaoRaiz():
    print("A raiz é escrita como potência com expoente fracionário:")
    print("  √x   →  x ^ (1/2)")
    print("  ∛x   →  x ^ (1/3)")
    print("Exemplos:")
    print("  9 ^ (1/2)  = 3")
    print("  8 ^ (1/3)  = 2")
    print("Use SEMPRE parênteses ao redor do expoente:  (1/2), (1/3).")
    print("Ou use raiz(x) para raiz quadrada diretamente.")

def ExplicacaoMemoriaTemporaria():
    print("Nesta Calculadora existem 2 memórias temporárias: M1 e M2")
    print("Sempre que obter um resultado, ele é armazenado em M1.")
    print("O resultado anterior passa a ser M2.")
    print("Exemplo: 2+2 → M1=4 | depois 3+3 → M2=4, M1=6")

def ExplicacaoMemoriasDefinidas():
    print("Você pode salvar expressões ou valores em variáveis personalizadas.")
    print("Digite: 2 no menu para acessar o módulo de memória.")
    print("Depois informe o nome da variável (ex: taxa, val1).")
    print("  Atenção: evite nomes como x, y, z pois podem colidir com o Solve.")
    print("Em seguida, informe o valor ou expressão a salvar.")
    print("Para usar a variável em cálculos, basta digitar o nome dela na expressão.")
    print("No modo Solve, variáveis com expressões algébricas (ex: x^2) são expandidas automaticamente.")

def ExplicacaoMenu():
    print("Navegue pelos modos digitando o número correspondente:")
    print("  1 - Ajuda")
    print("  2 - Memória Definida")
    print("  3 - Reset")
    print("  4 - Cálculo")
    print("  5 - Solve")
    print("  6 - Configurações")
    print("  Expressões matemáticas são calculadas diretamente pelo menu.")
    print("  Equações com '=' são enviadas automaticamente para o modo Solve.")

def ExplicacaoFuncoes():
    print("Funções disponíveis no Cálculo e no Solve:")
    print("  Trigonometria : sin(x)  cos(x)  tan(x)  — ou em PT-BR: sen(x)  tg(x)")
    print("  Inversas      : asin(x) acos(x) atan(x)")
    print("  Raiz          : sqrt(x) — ou em PT-BR: raiz(x)")
    print("  Logaritmo     : log(x) = ln(x) | log(x, base)")
    print("  Potência      : x^2")
    print("  Constantes    : pi  e")
    print("  Conversão     : rad(graus) → converte graus para radianos")
    print("                  graus(rad) → converte radianos para graus")
    print("  Exemplo       : sen(rad(45))  →  seno de 45 graus")

# ==================== MODO AJUDA ====================

def Modo_Ajuda():
    print("=" * NumCaracRafa1)
    print("[ Ajuda ]".center(NumCaracRafa1))
    print("=" * NumCaracRafa1)
    print("  1 - Multiplicação")
    print("  2 - Divisão")
    print("  3 - Potência")
    print("  4 - Raiz")
    print("  5 - Memória Temporária (M1 e M2)")
    print("  6 - Memória Definida")
    print("  7 - Explicação do Menu")
    print("  8 - Funções disponíveis")
    print("  0 - Voltar ao início")
    print("=" * NumCaracRafa1)

    while True:
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "1":
            ExplicacaoMultiplicacao()
        elif opcao == "2":
            ExplicacaoDivisao()
        elif opcao == "3":
            ExplicacaoPotencia()
        elif opcao == "4":
            ExplicacaoRaiz()
        elif opcao == "5":
            ExplicacaoMemoriaTemporaria()
        elif opcao == "6":
            ExplicacaoMemoriasDefinidas()
        elif opcao == "7":
            ExplicacaoMenu()
        elif opcao == "8":
            ExplicacaoFuncoes()
        elif opcao == "0":
            Exibir_Menu_Inicial()
            break
        else:
            print("Opção inválida. Tente novamente.")
        print()
        print("Digite outro número para continuar no Ajuda ou 0 para voltar.")

# ==================== PREPARAÇÃO DE EXPRESSÕES ====================

def preparar_expressao(expressao):
    expressao = expressao.replace("^", "**")
    expressao = expressao.replace(",", ".")
    for nome in sorted(memorias_definidas.keys(), key=lambda x: -len(x)):
        expressao = re.sub(rf'\b{re.escape(nome)}\b', f"mv_{nome}", expressao)
    if M1 is not None:
        expressao = re.sub(r'\bM1\b', str(M1), expressao)
    if M2 is not None:
        expressao = re.sub(r'\bM2\b', str(M2), expressao)
    return expressao

def preparar_expressao_solve(expressao):
    # NÃO converte ^ para ** — o convert_xor do parse_expr já faz isso
    expressao = expressao.replace(",", ".")
    for nome in sorted(memorias_definidas.keys(), key=lambda x: -len(x)):
        valor = memorias_definidas[nome]
        valor_str = str(valor)
        expressao = re.sub(rf'\b{re.escape(nome)}\b', f"({valor_str})", expressao)
    if M1 is not None:
        expressao = re.sub(r'\bM1\b', str(M1), expressao)
    if M2 is not None:
        expressao = re.sub(r'\bM2\b', str(M2), expressao)
    return expressao

def normalizar_funcoes_solve(expressao):
    # Traduz aliases PT-BR para nomes aceitos pelo sympy
    traducoes = {
        r'\bsen\b':    'sin',
        r'\btg\b':     'tan',
        r'\bcossec\b': 'csc',
        r'\bsec\b':    'sec',
        r'\bcotg\b':   'cot',
        r'\braiz\b':   'sqrt',
        r'\bln\b':     'log',
    }
    for padrao, substituto in traducoes.items():
        expressao = re.sub(padrao, substituto, expressao)

    # rad(x) → ((x)*pi/180) com parênteses explícitos para garantir precedência
    # O regex foi ajustado para ser mais robusto e só atuar em 'rad('
    expressao = re.sub(r'\brad\(([^)]+)\)', r'((\1)*pi/180)', expressao)
    # graus(x) → ((x)*180/pi)
    expressao = re.sub(r'\bgraus\(([^)]+)\)', r'((\1)*180/pi)', expressao)

    return expressao

# ==================== MEMÓRIA TEMPORÁRIA ====================

def atualizar_memoria(resultado):
    global M1, M2
    M2 = M1
    M1 = resultado

# ==================== MODO CÁLCULO ====================

def Modo_Calculo(expressao_direta=None):
    global M1, M2

    modo  = configuracoes["modo_resultado"]
    casas = configuracoes["casas_decimais"]

    print("=" * NumCaracRafa1)
    print("[ Modo Cálculo ]".center(NumCaracRafa1))
    print("=" * NumCaracRafa1)
    print("  Digite uma expressão matemática para calcular.")
    print("  Pode usar M1, M2 e qualquer variável salva na memória.")
    print("  Use ponto ou vírgula como decimal.")
    print("  Funções: sin/sen, cos, tan/tg, sqrt/raiz, log, pi, e")
    print("  Conversão de ângulo: rad(45) converte graus → radianos | sen(rad(45)) = seno de 45°")
    print(f"  Modo de exibição: {modo} | Casas decimais: {casas}")
    print("  Digite 'Menu' para voltar ao início.")
    print("=" * NumCaracRafa1)

    if expressao_direta:
        try:
            expressao_preparada = preparar_expressao(expressao_direta)
            contexto = montar_contexto()
            resultado = eval(expressao_preparada, contexto)
            resultado_formatado = formatar_resultado(resultado)
            print(f"{expressao_direta} = {resultado_formatado}")
            atualizar_memoria(resultado)
            m2_display = formatar_resultado(M2) if M2 is not None else "None"
            print(f"[M1 = {formatar_resultado(M1)} | M2 = {m2_display}]")
        except ZeroDivisionError:
            print("Erro: divisão por zero não é permitida.")
        except Exception as e:
            print(f"Erro na expressão: {type(e).__name__}: {e}")

    while True:
        expressao_str = input("\n> ").strip() # Corrigido: > para >

        if expressao_str.lower() == "menu":
            Exibir_Menu_Inicial()
            break

        if expressao_str == "":
            continue

        try:
            expressao_preparada = preparar_expressao(expressao_str)
            contexto = montar_contexto()
            resultado = eval(expressao_preparada, contexto)
            resultado_formatado = formatar_resultado(resultado)
            print(f"{expressao_str} = {resultado_formatado}")
            atualizar_memoria(resultado)
            m2_display = formatar_resultado(M2) if M2 is not None else "None"
            print(f"[M1 = {formatar_resultado(M1)} | M2 = {m2_display}]")

        except ZeroDivisionError:
            print("Erro: divisão por zero não é permitida.")
        except Exception as e:
            print(f"Erro na expressão: {type(e).__name__}: {e}")

# ==================== MODO SOLVE ====================

def resolver_equacao(entrada):
    if "=" not in entrada:
        print("Formato inválido. A equação precisa conter '='. Exemplo: x^2 = 9")
        return

    if entrada.count("=") > 1: # Corrigido: > para >
        print("Formato inválido. Use apenas um '=' separando os dois lados da equação.")
        print("Exemplo correto: x^2 + 2*x = 7")
        return

    try:
        if re.search(r'\bM1\b', entrada) and M1 is None:
            print("Erro: M1 está vazia. Faça um cálculo antes de usar M1 no Solve.")
            return
        if re.search(r'\bM2\b', entrada) and M2 is None:
            print("Erro: M2 está vazia. Faça um cálculo antes de usar M2 no Solve.")
            return

        if re.search(r'\bm1\b', entrada) or re.search(r'\bm2\b', entrada):
            print("Aviso: M1 e M2 são sensíveis a maiúsculas. Use M1 e M2 com letra maiúscula.")

        for nome in memorias_definidas:
            if re.search(rf'\b{re.escape(nome)}\b', entrada):
                valor = memorias_definidas[nome]
                if isinstance(valor, (int, float)):
                    print(f"  Aviso: '{nome}' será substituído pelo valor {valor} na equação.")
                else:
                    print(f"  Aviso: '{nome}' será expandido para '{valor}' na equação.")

        # Passo 1 — traduz PT-BR para sympy e converte rad/graus
        entrada_traduzida = normalizar_funcoes_solve(entrada)

        # Passo 2 — expande memórias e M1/M2 (sem converter ^ para **)
        entrada_preparada = preparar_expressao_solve(entrada_traduzida)

        # Passo 3 — separa os dois lados pelo "="
        partes = entrada_preparada.split("=")
        lado_esquerdo = partes[0].strip()
        lado_direito  = partes[1].strip()

        # Passo 4 — parse com local_dict e transformações
        # local_dict mapeia strings de funções/constantes para objetos SymPy
        expr_esquerda = parse_expr(
            lado_esquerdo,
            local_dict=SYMPY_LOCAL_DICT,
            transformations=TRANSFORMACOES_SYMPY
        )
        expr_direita = parse_expr(
            lado_direito,
            local_dict=SYMPY_LOCAL_DICT,
            transformations=TRANSFORMACOES_SYMPY
        )

        # Passo 5 — substitui M1 e M2 via sympy após o parse
        M1_sym = symbols('M1')
        M2_sym = symbols('M2')
        if M1 is not None:
            expr_esquerda = expr_esquerda.subs(M1_sym, M1)
            expr_direita  = expr_direita.subs(M1_sym, M1)
        if M2 is not None:
            expr_esquerda = expr_esquerda.subs(M2_sym, M2)
            expr_direita  = expr_direita.subs(M2_sym, M2)

        # Passo 6 — detecta variáveis livres
        variaveis = expr_esquerda.free_symbols | expr_direita.free_symbols

        # Mostra equação expandida quando houve substituições
        equacao_expandida = f"{expr_esquerda} = {expr_direita}"
        entrada_normalizada = entrada.replace(" ", "").replace(",", ".")
        if equacao_expandida.replace(" ", "") != entrada_normalizada:
            print(f"  Equação expandida: {equacao_expandida}")

        # Passo 7 — verifica identidade/contradição ANTES de definir variavel
        diferenca = (expr_esquerda - expr_direita).simplify()

        if not variaveis:
            if diferenca == 0:
                print("A equação é sempre verdadeira (identidade). Infinitas soluções.")
            else:
                print("A equação não tem solução (contradição). Os dois lados nunca são iguais.")
            return

        if diferenca == 0:
            print("A equação é sempre verdadeira para qualquer valor das variáveis. Infinitas soluções.")
            return

        # Passo 8 — define a variável a resolver
        if len(variaveis) > 1: # Corrigido: > para >
            nomes = sorted([str(v) for v in variaveis])
            print(f"Variáveis encontradas: {', '.join(nomes)}")
            while True:
                var_escolhida = input("Qual variável deseja resolver? ").strip()
                if var_escolhida in nomes:
                    break
                print(f"'{var_escolhida}' não encontrada. Opções: {', '.join(nomes)}")
            variavel = symbols(var_escolhida)
        else:
            variavel = list(variaveis)[0]

        # Passo 9 — resolve
        equacao  = Eq(expr_esquerda, expr_direita)
        solucoes = solve(equacao, variavel)

        if not solucoes:
            print("Nenhuma solução encontrada para essa equação.")
            return

        print(f"\n  Equação: {entrada}")
        for sol in solucoes:
            resultado_str, valor_float = formatar_solucao_solve(sol)
            if valor_float is not None:
                print(f"  {variavel} = {resultado_str}")
            else:
                print(f"  {variavel} = {resultado_str}  (forma simbólica)")

        try:
            primeira = solucoes[0]
            if primeira.is_real and primeira.is_number:
                atualizar_memoria(float(primeira))
                m2_display = formatar_resultado(M2) if M2 is not None else "None"
                print(f"\n[M1 = {formatar_resultado(M1)} | M2 = {m2_display}]")
            else:
                print(f"\nM1 não atualizada — solução não é um número real.")
                m1_display = formatar_resultado(M1) if M1 is not None else "None"
                m2_display = formatar_resultado(M2) if M2 is not None else "None"
                print(f"[M1 = {m1_display} | M2 = {m2_display}]")
        except Exception:
            pass

    except SympifyError as e:
        print("Erro ao interpretar a equação. Verifique a sintaxe.")
        print("Dicas:")
        print("  - Use * para multiplicação: 2*x, não 2x")
        print("  - Use ^ para potência: x^2")
        print("  - Use ponto ou vírgula decimal: 2.5 ou 2,5")
        print("  - Funções aceitas: sin/sen, cos, tan/tg, sqrt/raiz, log")
        print(f"  Detalhes do erro: {e}") # Adicionado para depuração
    except Exception as e:
        print(f"Erro ao resolver: {type(e).__name__}: {e}")

def Modo_Solve(equacao_direta=None):
    modo  = configuracoes["modo_resultado"]
    casas = configuracoes["casas_decimais"]

    print("=" * NumCaracRafa1)
    print("[ Modo Solve ]".center(NumCaracRafa1))
    print("=" * NumCaracRafa1)
    print("  Resolva equações algébricas informando a equação.")
    print("  Exemplos:")
    print("    x^2 = 9              →  x = 3 ou x = -3")
    print("    2*x + 4 = 10         →  x = 3")
    print("    x^2 + 5*x + 6 = 0")
    print("  Você pode usar M1 e M2 diretamente (sensível a maiúsculas).")
    print("  Funções: sin/sen, cos, tan/tg, sqrt/raiz, log.")
    print("  Use * para multiplicar e ^ para potência.")
    print(f"  Modo de exibição: {modo} | Casas decimais: {casas}")

    m1_display = formatar_resultado(M1) if M1 is not None else "vazio"
    m2_display = formatar_resultado(M2) if M2 is not None else "vazio"
    print(f"  [M1 = {m1_display} | M2 = {m2_display}]")
    print("  Digite 'Menu' para voltar ao início.")
    print("=" * NumCaracRafa1)

    if equacao_direta:
        resolver_equacao(equacao_direta)

    while True:
        entrada = input("\n> ").strip() # Corrigido: > para >
        if entrada.lower() == "menu":
            Exibir_Menu_Inicial()
            break
        if entrada == "":
            continue
        resolver_equacao(entrada)

# ==================== MODO CONFIGURAÇÕES ====================

def Modo_Configuracoes():
    print("=" * NumCaracRafa1)
    print("[ Configurações ]".center(NumCaracRafa1))
    print("=" * NumCaracRafa1)

    while True:
        modo_atual  = configuracoes["modo_resultado"]
        casas_atual = configuracoes["casas_decimais"]
        print(f"  Modo atual     : {modo_atual}")
        print(f"  Casas decimais : {casas_atual}")
        print()
        print("  1 - Modo de exibição do resultado")
        print("  2 - Alterar número de casas decimais")
        print("  0 - Voltar ao início")
        print("=" * NumCaracRafa1)

        opcao = input("Escolha: ").strip()

        if opcao == "1":
            Modo_Exibicao()
        elif opcao == "2":
            print(f"  Casas decimais atuais: {casas_atual}")
            print("  Informe o número de casas decimais (1 a 15):")
            entrada = input("  > ").strip() # Corrigido: > para >
            if entrada.isdigit() and 1 <= int(entrada) <= 15: # Corrigido: < e > para < e >
                configuracoes["casas_decimais"] = int(entrada)
                print(f"Casas decimais definidas para: {configuracoes['casas_decimais']}")
                print(f"  Exemplo com pi: {formatar_resultado(math.pi)}")
            else:
                print("Valor inválido. Digite um número entre 1 e 15.")
        elif opcao == "0":
            Exibir_Menu_Inicial()
            break
        else:
            print("Opção inválida. Tente novamente.")

        print()
        print("Digite outro número para continuar nas Configurações ou 0 para voltar.")

def Modo_Exibicao():
    print("=" * NumCaracRafa1)
    print("[ Modo de Exibição ]".center(NumCaracRafa1))
    print("=" * NumCaracRafa1)

    while True:
        modo_atual  = configuracoes["modo_resultado"]
        casas_atual = configuracoes["casas_decimais"]
        print(f"  Modo atual: {modo_atual}")
        print()
        print("  1 - Automático        (inteiro se possível, decimal caso contrário)")
        print("  2 - Decimal fixo      (exibe sempre com o número de casas configurado)")
        print("  3 - Notação científica")
        print("  4 - Fração")
        print("  5 - Inteiro           (arredonda para o inteiro mais próximo)")
        print("  0 - Voltar às Configurações")
        print("=" * NumCaracRafa1)

        opcao = input("Escolha: ").strip()

        if opcao == "1":
            configuracoes["modo_resultado"] = "auto"
            print("Modo definido para: Automático")
            print(f"  Exemplo: 1/3 → {formatar_resultado(1/3)} | 4.0 → {formatar_resultado(4.0)}")
        elif opcao == "2":
            configuracoes["modo_resultado"] = "decimal"
            print(f"Modo definido para: Decimal fixo ({casas_atual} casas)")
            print(f"  Exemplo: 1/3 → {formatar_resultado(1/3)} | pi → {formatar_resultado(math.pi)}")
        elif opcao == "3":
            configuracoes["modo_resultado"] = "cientifico"
            print(f"Modo definido para: Notação científica ({casas_atual} casas)")
            print(f"  Exemplo: 1234567 → {formatar_resultado(1234567)} | 0.000123 → {formatar_resultado(0.000123)}")
        elif opcao == "4":
            configuracoes["modo_resultado"] = "fracao"
            print("Modo definido para: Fração")
            print(f"  Exemplo: 0.5 → {formatar_resultado(0.5)} | 0.333 → {formatar_resultado(0.333)}")
        elif opcao == "5":
            configuracoes["modo_resultado"] = "inteiro"
            print("Modo definido para: Inteiro")
            print(f"  Exemplo: 3.7 → {formatar_resultado(3.7)} | 2.1 → {formatar_resultado(2.1)}")
        elif opcao == "0":
            break
        else:
            print("Opção inválida. Tente novamente.")

        print()
        print("Digite outro número para continuar ou 0 para voltar às Configurações.")

# ==================== MODO MEMÓRIA ====================

def Modo_Memoria():
    print("=" * NumCaracRafa1)
    print("[ Módulo de Memória ]".center(NumCaracRafa1))
    print("=" * NumCaracRafa1)
    print("  1 - Definir nova memória")
    print("  2 - Ver memórias salvas")
    print("  3 - Editar uma memória")
    print("  4 - Exportar memórias")
    print("  5 - Importar memórias")
    print("  0 - Voltar ao início")
    print("=" * NumCaracRafa1)

    while True:
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "1":
            Definir_Memoria()
        elif opcao == "2":
            Listar_Memorias()
        elif opcao == "3":
            Editar_Memoria()
        elif opcao == "4":
            Exportar_Memorias()
        elif opcao == "5":
            Importar_Memorias()
        elif opcao == "0":
            Exibir_Menu_Inicial()
            break
        else:
            print("Opção inválida. Tente novamente.")
        print()
        print("Digite outro número para continuar no módulo de Memória ou 0 para voltar.")

def Definir_Memoria():
    print()
    print("  Digite 0 para cancelar.")
    nome = input("Defina letras/conjunto de letras para armazenar: ").strip()

    if not nome or nome == "0":
        print("Operação cancelada.")
        return

    variaveis_comuns = {"x", "y", "z", "t", "n", "k", "a", "b", "c"}
    if nome.lower() in variaveis_comuns:
        print(f"  Aviso: '{nome}' é um nome muito comum para variáveis algébricas.")
        print(f"  No modo Solve, '{nome}' será substituído em vez de ser resolvido.")
        confirmacao = input("  Deseja continuar mesmo assim? (sim/não): ").strip().lower()
        if confirmacao != "sim":
            print("Operação cancelada.")
            return

    if nome in memorias_definidas:
        print(f"'{nome}' já existe com o valor: {memorias_definidas[nome]}")
        confirmacao = input("Deseja sobrescrever? (sim/não): ").strip().lower()
        if confirmacao != "sim":
            print("Operação cancelada.")
            return

    valor_str = input(f"Digite o valor ou expressão para '{nome}': ").strip()

    if not valor_str or valor_str == "0":
        print("Operação cancelada.")
        return

    try:
        expressao_preparada = preparar_expressao(valor_str)
        contexto = montar_contexto()
        resultado = eval(expressao_preparada, contexto)
        memorias_definidas[nome] = resultado
        print(f"'{nome}' salvo com o valor: {resultado}")
    except ZeroDivisionError:
        print("Erro: divisão por zero não é permitida.")
    except Exception:
        memorias_definidas[nome] = valor_str
        print(f"'{nome}' salvo como expressão: {valor_str}")

def Listar_Memorias():
    if not memorias_definidas:
        print("Nenhuma memória definida ainda.")
        return
    print("=" * NumCaracRafa1)
    print("[ Memórias Salvas ]".center(NumCaracRafa1))
    print("=" * NumCaracRafa1)
    for i, (nome, valor) in enumerate(memorias_definidas.items(), start=1):
        print(f"  {i}. {nome} = {valor}")
    print(f"\n[{len(memorias_definidas)} memória(s) salva(s)]")
    print("=" * NumCaracRafa1)

def Editar_Memoria():
    if not memorias_definidas:
        print("Nenhuma memória definida para editar.")
        return

    Listar_Memorias()
    nomes = list(memorias_definidas.keys())
    entrada = input("\nDigite o número ou o nome da memória (0 para cancelar): ").strip()

    if entrada == "0":
        print("Edição cancelada.")
        return

    if entrada.isdigit():
        indice = int(entrada) - 1
        if indice < 0 or indice >= len(nomes): # Corrigido: < e > para < e >
            print("Número inválido.")
            return
        nome = nomes[indice]
    elif entrada in memorias_definidas:
        nome = entrada
    else:
        print(f"'{entrada}' não encontrado nas memórias.")
        return

    print(f"Editando '{nome}' — valor atual: {memorias_definidas[nome]}")
    print("  1 - Alterar valor")
    print("  2 - Remover esta memória")
    print("  0 - Cancelar")
    acao = input("Escolha: ").strip()

    if acao == "1":
        valor_str = input(f"Novo valor ou expressão para '{nome}': ").strip()
        try:
            expressao_preparada = preparar_expressao(valor_str)
            contexto = montar_contexto()
            resultado = eval(expressao_preparada, contexto)
            memorias_definidas[nome] = resultado
            print(f"'{nome}' atualizado para: {resultado}")
        except ZeroDivisionError:
            print("Erro: divisão por zero não é permitida.")
        except Exception:
            memorias_definidas[nome] = valor_str
            print(f"'{nome}' atualizado como expressão: {valor_str}")
    elif acao == "2":
        confirmacao = input(f"Remover '{nome}'? (sim/não): ").strip().lower()
        if confirmacao == "sim":
            del memorias_definidas[nome]
            print(f"'{nome}' removido.")
        else:
            print("Remoção cancelada.")
    elif acao == "0":
        print("Edição cancelada.")
    else:
        print("Opção inválida.")

def Exportar_Memorias():
    if not memorias_definidas:
        print("Nenhuma memória para exportar.")
        return
    nome_arquivo = input("Digite o nome do arquivo (sem extensão, 0 para cancelar): ").strip()
    if not nome_arquivo or nome_arquivo == "0":
        print("Operação cancelada.")
        return
    try:
        with open(nome_arquivo + ".json", "w", encoding="utf-8") as f:
            json.dump(memorias_definidas, f, ensure_ascii=False, indent=4)
        print(f"Memórias exportadas para '{nome_arquivo}.json'.")
    except Exception as e:
        print(f"Erro ao exportar: {e}")

def Importar_Memorias():
    nome_arquivo = input("Digite o nome do arquivo (sem extensão, 0 para cancelar): ").strip()
    if not nome_arquivo or nome_arquivo == "0":
        print("Operação cancelada.")
        return
    try:
        with open(nome_arquivo + ".json", "r", encoding="utf-8") as f:
            dados = json.load(f)

        if not isinstance(dados, dict):
            print("Arquivo inválido.")
            return

        dados_validados = {}
        for chave, valor in dados.items():
            if isinstance(valor, (int, float, str)):
                dados_validados[chave] = valor
            else:
                print(f"  Aviso: '{chave}' ignorado (tipo inválido: {type(valor).__name__}).")

        if not dados_validados:
            print("Nenhum valor válido encontrado.")
            return

        if memorias_definidas:
            print(f"Você já tem {len(memorias_definidas)} memória(s) salva(s).")
            print("  1 - Mesclar  |  2 - Substituir tudo  |  0 - Cancelar")
            opcao = input("Escolha: ").strip()

            if opcao == "1":
                conflitos = [n for n in dados_validados if n in memorias_definidas]
                if conflitos:
                    print(f"Conflitos: {', '.join(conflitos)}")
                    print("  1 - Manter atuais  |  2 - Sobrescrever com arquivo")
                    resolucao = input("Escolha: ").strip()
                    if resolucao == "1":
                        for n, v in dados_validados.items():
                            if n not in memorias_definidas:
                                memorias_definidas[n] = v
                    elif resolucao == "2":
                        memorias_definidas.update(dados_validados)
                    else:
                        print("Opção inválida. Importação cancelada.")
                        return
                else:
                    memorias_definidas.update(dados_validados)
            elif opcao == "2":
                memorias_definidas.clear()
                memorias_definidas.update(dados_validados)
            elif opcao == "0":
                print("Importação cancelada.")
                return
            else:
                print("Opção inválida.")
                return
        else:
            memorias_definidas.update(dados_validados)

        print(f"Importação concluída. Total: {len(memorias_definidas)} memória(s).")

    except FileNotFoundError:
        print(f"Arquivo '{nome_arquivo}.json' não encontrado.")
    except json.JSONDecodeError:
        print("Erro ao ler o arquivo. Verifique se é um JSON válido.")
    except Exception as e:
        print(f"Erro ao importar: {e}")

# ==================== MODO RESET ====================

def Modo_Reset():
    global M1, M2, memorias_definidas
    print("=" * NumCaracRafa1)
    print("[ Reset ]".center(NumCaracRafa1))
    print("=" * NumCaracRafa1)
    print("  1 - Resetar memórias temporárias (M1 e M2)")
    print("  2 - Resetar memórias definidas")
    print("  3 - Resetar configurações de exibição")
    print("  4 - Resetar tudo")
    print("  0 - Cancelar")
    print("=" * NumCaracRafa1)

    opcao = input("Escolha: ").strip()

    if opcao == "1":
        if input("Resetar M1 e M2? (sim/não): ").strip().lower() == "sim":
            M1 = None
            M2 = None
            print("Memórias temporárias resetadas.")
        else:
            print("Cancelado.")
    elif opcao == "2":
        if input("Resetar memórias definidas? (sim/não): ").strip().lower() == "sim":
            memorias_definidas.clear()
            print("Memórias definidas apagadas.")
        else:
            print("Cancelado.")
    elif opcao == "3":
        if input("Resetar configurações? (sim/não): ").strip().lower() == "sim":
            configuracoes["modo_resultado"] = "auto"
            configuracoes["casas_decimais"] = 4
            print("Configurações restauradas.")
        else:
            print("Cancelado.")
    elif opcao == "4":
        if input("Resetar tudo? (sim/não): ").strip().lower() == "sim":
            M1 = None
            M2 = None
            memorias_definidas.clear()
            configuracoes["modo_resultado"] = "auto"
            configuracoes["casas_decimais"] = 4
            print("Calculadora resetada.")
        else:
            print("Cancelado.")
    elif opcao == "0":
        print("Reset cancelado.")
    else:
        print("Opção inválida.")

    Exibir_Menu_Inicial()

# ==================== MENU INICIAL ====================

def Exibir_Menu_Inicial():
    formatrafa1()
    modo_atual = configuracoes["modo_resultado"]
    print("  1 - Ajuda  |  2 - Memória  |  3 - Reset  |  4 - Cálculo  |  5 - Solve  |  6 - Configurações  |  sair - Encerrar")
    print(f"  Modo de exibição: {modo_atual} | Casas decimais: {configuracoes['casas_decimais']}")
    print("  Expressões matemáticas são calculadas diretamente. Equações com '=' vão para o Solve.")
    print("=" * NumCaracRafa1)

def Menu_Inicial():
    limpar_buffer()
    print("\n" * 50)
    Exibir_Menu_Inicial()

    while True:
        entrada = input("\n> ").strip() # Corrigido: > para >

        if not entrada_parece_valida(entrada):
            continue

        if entrada.lower() in ["sair", "exit", "quit"]:
            print("Encerrando a calculadora. Até logo!")
            break
        elif entrada == "1":
            Modo_Ajuda()
        elif entrada == "2":
            Modo_Memoria()
        elif entrada == "3":
            Modo_Reset()
        elif entrada == "4":
            Modo_Calculo()
        elif entrada == "5":
            Modo_Solve()
        elif entrada == "6":
            Modo_Configuracoes()
        elif entrada == "":
            continue
        elif "=" in entrada:
            Modo_Solve(equacao_direta=entrada)
        else:
            Modo_Calculo(expressao_direta=entrada)

# ==================== INÍCIO ====================
Menu_Inicial()