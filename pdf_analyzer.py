import os
from pypdf import PdfReader

ENTRADA_DIR = os.path.join(os.path.dirname(__file__), "entrada")
RESUMOS_DIR = os.path.join(os.path.dirname(__file__), "resumos")

# Certifica-se de que as pastas existem
os.makedirs(ENTRADA_DIR, exist_ok=True)
os.makedirs(RESUMOS_DIR, exist_ok=True)

def listar_documentos_entrada_logic() -> list[str]:
    """Lista todos os arquivos PDF disponíveis na pasta de entrada para serem processados."""
    arquivos = []
    if os.path.exists(ENTRADA_DIR):
        for f in os.listdir(ENTRADA_DIR):
            if f.lower().endswith(".pdf"):
                arquivos.append(f)
    return arquivos

def ler_evento_pdf_logic(nome_arquivo: str) -> str:
    """Lê o conteúdo de texto do arquivo PDF especificado."""
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

def salvar_resumo_evento_logic(nome_arquivo: str, resumo: str) -> str:
    """Salva as informações extraídas ou o resumo final do evento em um arquivo txt."""
    if not nome_arquivo.lower().endswith(".txt"):
        nome_arquivo += ".txt"
        
    filepath = os.path.join(RESUMOS_DIR, nome_arquivo)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(resumo)
        return f"Resumo salvo com sucesso em: {filepath}"
    except Exception as e:
        return f"Erro ao salvar resumo: {str(e)}"
