# ============================================================
# JOVI CLI - Interface de Linha de Comando
# Programa interativo que consome a API JOVI para
# produtividade estudantil.
# ============================================================
# Conceitos aplicados:
# - Menu de opções com loop (while)
# - Estruturas de decisão (match-case)
# - Entrada e saída de dados (input / f-string)
# - Validação de dados de entrada
# - Manipulação de variáveis
# - Armazenamento e manipulação de listas
# - Estruturas de repetição (for)
# - Organização do código em funções
# ============================================================

import os
import requests

# [VARIÁVEL] URL base da API (pode ser local ou remota)
API_URL = os.getenv("JOVI_API_URL", "http://localhost:8000")


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def exibir_menu() -> None:
    """Exibe o menu principal do programa."""
    print("\n" + "=" * 50)
    print("       JOVI - Produtividade Estudantil")
    print("=" * 50)
    print("1. Analisar imagem (extrair texto e sugerir matéria)")
    print("2. Confirmar conteúdo (salvar no sistema)")
    print("3. Traduzir texto")
    print("4. Gerar resumo por IA")
    print("5. Listar matérias")
    print("6. Listar pastas do usuário")
    print("7. Ver conteúdos recentes")
    print("0. Sair")
    print("-" * 50)


def exibir_erro(response: requests.Response) -> None:
    """Exibe mensagem de erro da API formatada."""
    try:
        erro = response.json().get("detail", "Erro desconhecido")
    except Exception:
        erro = response.text
    # [F-STRING] Mensagem de erro formatada
    print(f"\nErro ({response.status_code}): {erro}")


# ============================================================
# FUNCIONALIDADES
# ============================================================

def analisar_imagem() -> None:
    """
    Opção 1: Envia uma imagem para a IA extrair texto e sugerir matéria.
    Salva a imagem em cache por 5 minutos para confirmação posterior.
    """
    print("\n--- Analisar Imagem ---")

    # [ENTRADA DE DADOS + VALIDAÇÃO] Solicita caminho do arquivo
    caminho: str = input("Caminho da imagem (ex: ./foto.jpg): ").strip()

    # [VALIDAÇÃO] Verifica se o arquivo existe
    if not caminho:
        print("Caminho não pode ser vazio.")
        return

    if not os.path.isfile(caminho):
        print(f"Arquivo não encontrado: {caminho}")
        return

    # [VALIDAÇÃO] Verifica extensão do arquivo
    extensoes_validas: list[str] = [".jpg", ".jpeg", ".png", ".webp", ".gif"]
    extensao: str = os.path.splitext(caminho)[1].lower()

    if extensao not in extensoes_validas:
        print(f"Extensão '{extensao}' não suportada. Use: {extensoes_validas}")
        return

    # [ENTRADA DE DADOS] Envia imagem para a API
    print("Enviando imagem para análise...")

    try:
        with open(caminho, "rb") as arquivo:
            response = requests.post(
                f"{API_URL}/ia/analisar-imagem",
                files={"imagem": (os.path.basename(caminho), arquivo)},
            )
    except requests.ConnectionError:
        print(f"Não foi possível conectar à API em {API_URL}")
        return

    # [DECISÃO] Verifica se a requisição foi bem-sucedida
    if response.status_code != 200:
        exibir_erro(response)
        return

    # [MANIPULAÇÃO DE VARIÁVEIS] Extrai dados da resposta
    dados: dict = response.json()
    texto_extraido: str = dados.get("texto_extraido", "")
    materia_id: str = dados.get("materia_sugerida_id", "N/A")
    cache_id: str = dados.get("cache_id", "")

    # [SAÍDA DE DADOS - f-string] Exibe resultados
    print(f"\nAnálise concluída!")
    print(f"Texto extraído: {texto_extraido[:200]}...")
    print(f"Matéria sugerida (ID): {materia_id}")
    print(f"Cache ID (use na opção 2): {cache_id}")
    print(f"A imagem ficará em cache por 5 minutos.")


def confirmar_conteudo() -> None:
    """
    Opção 2: Confirma o conteúdo analisado, salvando no sistema.
    Usa o cache_id da análise anterior.
    """
    print("\n--- Confirmar Conteúdo ---")

    # [ENTRADA DE DADOS] Solicita dados necessários
    cache_id: str = input("Cache ID (da análise anterior): ").strip()
    if not cache_id:
        print("Cache ID é obrigatório.")
        return

    id_materia: str = input("ID da matéria: ").strip()
    if not id_materia:
        print("ID da matéria é obrigatório.")
        return

    texto_extraido: str = input("Texto extraído (ou cole o da análise): ").strip()
    if not texto_extraido:
        print("Texto extraído é obrigatório.")
        return

    # [ENTRADA DE DADOS] Envia para a API
    print("Confirmando conteúdo...")

    try:
        response = requests.post(
            f"{API_URL}/conteudo/confirmar",
            json={
                "cache_id": cache_id,
                "id_materia": id_materia,
                "texto_extraido": texto_extraido,
            },
        )
    except requests.ConnectionError:
        print(f"Não foi possível conectar à API em {API_URL}")
        return

    # [DECISÃO] Verifica resposta
    if response.status_code != 200:
        exibir_erro(response)
        return

    # [SAÍDA - f-string] Exibe confirmação
    dados: dict = response.json()
    print(f"\n✅ Conteúdo salvo com sucesso!")
    print(f"🆔 ID do conteúdo: {dados.get('id')}")
    print(f"📁 Pasta ID: {dados.get('pasta_id')}")

    # [LISTA + REPETIÇÃO] Exibe imagens vinculadas
    imagens: list[dict] = dados.get("imagens", [])
    if imagens:
        print("Imagens:")
        for img in imagens:
            print(f"   - {img.get('url_storage')}")


def traduzir_texto() -> None:
    """
    Opção 3: Traduz um texto para o idioma desejado.
    """
    print("\n--- Traduzir Texto ---")

    # [ENTRADA DE DADOS] Solicita texto e idioma
    texto: str = input("Texto para traduzir: ").strip()
    if not texto:
        print("Texto não pode ser vazio.")
        return

    idioma: str = input("Idioma destino (padrão: português brasileiro): ").strip()
    if not idioma:
        idioma = "português brasileiro"

    # Envia para a API
    print("⏳ Traduzindo...")

    try:
        response = requests.post(
            f"{API_URL}/ia/traduzir-texto",
            json={"texto": texto, "idioma_destino": idioma},
        )
    except requests.ConnectionError:
        print(f"Não foi possível conectar à API em {API_URL}")
        return

    # [DECISÃO] Verifica resposta
    if response.status_code != 200:
        exibir_erro(response)
        return

    # [SAÍDA - f-string]
    traducao: str = response.json().get("traducao", "")
    print(f"\nTradução ({idioma}):")
    print(f"   {traducao}")


def gerar_resumo() -> None:
    """
    Opção 4: Gera um resumo por IA de um conteúdo salvo.
    """
    print("\n--- Gerar Resumo por IA ---")

    # [ENTRADA DE DADOS]
    conteudo_id: str = input("ID do conteúdo: ").strip()
    if not conteudo_id:
        print("ID do conteúdo é obrigatório.")
        return

    print("⏳ Gerando resumo...")

    try:
        response = requests.post(
            f"{API_URL}/ia/resumo",
            json={"conteudo_id": conteudo_id},
        )
    except requests.ConnectionError:
        print(f"Não foi possível conectar à API em {API_URL}")
        return

    # [DECISÃO]
    if response.status_code != 200:
        exibir_erro(response)
        return

    # [SAÍDA - f-string]
    resumo: str = response.json().get("resumo", "")
    print(f"\nResumo gerado:")
    print(f"   {resumo}")


def listar_materias() -> None:
    """
    Opção 5: Lista todas as matérias cadastradas.
    """
    print("\n--- Matérias Cadastradas ---")

    try:
        response = requests.get(f"{API_URL}/materias")
    except requests.ConnectionError:
        print(f"Não foi possível conectar à API em {API_URL}")
        return

    if response.status_code != 200:
        exibir_erro(response)
        return

    # [LISTA] Recebe lista de matérias
    materias: list[dict] = response.json()

    # [DECISÃO] Verifica se há matérias
    if not materias:
        print("Nenhuma matéria cadastrada.")
        return

    # [REPETIÇÃO - for + f-string] Exibe cada matéria
    print(f"\n{'ID':<40} {'Nome'}")
    print("-" * 60)
    for materia in materias:
        print(f"{materia['id']:<40} {materia['nome']}")

    print(f"\nTotal: {len(materias)} matérias")


def listar_pastas() -> None:
    """
    Opção 6: Lista as pastas do usuário com contagem de arquivos.
    """
    print("\n--- Pastas do Usuário ---")

    try:
        response = requests.get(f"{API_URL}/pastas")
    except requests.ConnectionError:
        print(f"Não foi possível conectar à API em {API_URL}")
        return

    if response.status_code != 200:
        exibir_erro(response)
        return

    # [LISTA] Recebe lista de pastas
    pastas: list[dict] = response.json()

    # [DECISÃO]
    if not pastas:
        print("Nenhuma pasta encontrada.")
        return

    # [REPETIÇÃO - for + f-string] Exibe cada pasta
    print(f"\n{'Nome':<25} {'Arquivos':<10} {'ID'}")
    print("-" * 75)
    for pasta in pastas:
        nome: str = pasta.get("nome", "")
        qtd: int = pasta.get("quantidade_arquivos", 0)
        pasta_id: str = pasta.get("id", "")
        print(f"{nome:<25} {qtd:<10} {pasta_id}")

    print(f"\nTotal: {len(pastas)} pastas")


def ver_recentes() -> None:
    """
    Opção 7: Exibe os 4 conteúdos mais recentes do usuário.
    """
    print("\n--- Conteúdos Recentes ---")

    try:
        response = requests.get(f"{API_URL}/dashboard/recentes")
    except requests.ConnectionError:
        print(f"Não foi possível conectar à API em {API_URL}")
        return

    if response.status_code != 200:
        exibir_erro(response)
        return

    # [LISTA] Recebe lista de conteúdos recentes
    recentes: list[dict] = response.json()

    # [DECISÃO]
    if not recentes:
        print("Nenhum conteúdo encontrado.")
        return

    # [REPETIÇÃO - for] Exibe cada conteúdo recente
    for i, conteudo in enumerate(recentes, start=1):
        texto: str = conteudo.get("extracao_original", "")[:80]
        resumo: str = conteudo.get("resumo_ia") or "Sem resumo"
        imagem: str = conteudo.get("imagem_url") or "Sem imagem"
        conteudo_id: str = conteudo.get("id", "")

        print(f"\n[{i}] ID: {conteudo_id}")
        print(f"   Texto: {texto}...")
        print(f"   Resumo: {resumo[:60]}...")
        print(f"   Imagem: {imagem}")

    print(f"\nTotal: {len(recentes)} conteúdos recentes")


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main() -> None:
    """
    Função principal do programa.
    Implementa o loop do menu com estrutura de repetição (while)
    e estrutura de decisão (match-case).
    """
    print("\n Bem-vindo ao JOVI!")
    print(f" Conectando à API em: {API_URL}")

    # [ESTRUTURA DE REPETIÇÃO - while] Loop principal do menu
    while True:
        exibir_menu()

        # [ENTRADA DE DADOS] Lê opção do usuário
        opcao: str = input("Escolha uma opção: ").strip()

        # [ESTRUTURA DE DECISÃO - match-case] Direciona para a funcionalidade
        match opcao:
            case "1":
                analisar_imagem()
            case "2":
                confirmar_conteudo()
            case "3":
                traduzir_texto()
            case "4":
                gerar_resumo()
            case "5":
                listar_materias()
            case "6":
                listar_pastas()
            case "7":
                ver_recentes()
            case "0":
                # [SAÍDA] Encerra o programa
                print("\n Até logo! Bons estudos!")
                break
            case _:
                # [VALIDAÇÃO] Opção inválida
                print(f"\n  Opção '{opcao}' inválida. Escolha de 0 a 7.")


# Ponto de entrada do programa
if __name__ == "__main__":
    main()
