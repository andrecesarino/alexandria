import os
from mcp.server.fastmcp import FastMCP
from pypdf import PdfReader

# Inicializa o servidor MCP
mcp = FastMCP("Alexandria_Agent_Skills")

ENTRADA_DIR = os.path.join(os.path.dirname(__file__), "entrada")
RESUMOS_DIR = os.path.join(os.path.dirname(__file__), "resumos")

# Certifica-se de que as pastas existem
os.makedirs(ENTRADA_DIR, exist_ok=True)
os.makedirs(RESUMOS_DIR, exist_ok=True)

@mcp.tool()
def listar_documentos_entrada() -> list[str]:
    """Lista todos os arquivos PDF disponíveis na pasta de entrada para serem processados."""
    arquivos = []
    if os.path.exists(ENTRADA_DIR):
        for f in os.listdir(ENTRADA_DIR):
            if f.lower().endswith(".pdf"):
                arquivos.append(f)
    return arquivos

@mcp.tool()
def ler_evento_pdf(nome_arquivo: str) -> str:
    """Lê o conteúdo de texto do arquivo PDF especificado. 
    Use esta ferramenta para analisar a proposta do evento e encontrar informações como: 
    nome do evento, tipo, modalidade, data/horário, público-alvo, requisitos, distribuição de vagas."""
    
    filepath = os.path.join(ENTRADA_DIR, nome_arquivo)
    if not os.path.exists(filepath):
        return f"Erro: Arquivo '{nome_arquivo}' não encontrado na pasta entrada."
    
    try:
        reader = PdfReader(filepath)
        text = ""
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"--- PÁGINA {i+1} ---\n{page_text}\n\n"
        return text
    except Exception as e:
        return f"Erro ao ler o PDF: {str(e)}"

@mcp.tool()
def salvar_resumo_evento(nome_arquivo: str, resumo: str) -> str:
    """Salva as informações extraídas ou o resumo final do evento em um arquivo txt dentro da pasta resumos.
    O parâmetro 'nome_arquivo' deve ser o nome desejado para o arquivo (ex: 'resumo_evento_xyz.txt')."""
    if not nome_arquivo.lower().endswith(".txt"):
        nome_arquivo += ".txt"
        
    filepath = os.path.join(RESUMOS_DIR, nome_arquivo)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(resumo)
        return f"Resumo salvo com sucesso em: {filepath}"
    except Exception as e:
        return f"Erro ao salvar resumo: {str(e)}"

if __name__ == "__main__":
    mcp.run()
