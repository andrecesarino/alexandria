import os
from mcp.server.fastmcp import FastMCP
from pypdf import PdfReader

# Imports adicionados (Fase 2)
from telegram_bot import iniciar_bot_threads
from task_delegator import executar_delegacao
from directory_watcher import iniciar_observador_threads

# Inicializa o servidor MCP
mcp = FastMCP("Alexandria_Agent_Skills")

# Inicia a Thread global do Telegram Bot que ficará escutando comandos (Fase 2)
iniciar_bot_threads()

# Inicia a Thread de automação de diretório (Watcher - Automação Total)
iniciar_observador_threads()

from pdf_analyzer import (
    listar_documentos_entrada_logic,
    ler_evento_pdf_logic,
    salvar_resumo_evento_logic
)

@mcp.tool()
def listar_documentos_entrada() -> list[str]:
    """Lista todos os arquivos PDF disponíveis na pasta de entrada para serem processados."""
    return listar_documentos_entrada_logic()

@mcp.tool()
def ler_evento_pdf(nome_arquivo: str) -> str:
    """Lê o conteúdo de texto do arquivo PDF especificado. 
    Use esta ferramenta para analisar a proposta do evento e encontrar informações como: 
    nome do evento, tipo, modalidade, data/horário, público-alvo, requisitos, distribuição de vagas."""
    return ler_evento_pdf_logic(nome_arquivo)

@mcp.tool()
def salvar_resumo_evento(nome_arquivo: str, resumo: str) -> str:
    """Salva as informações extraídas ou o resumo final do evento em um arquivo txt dentro da pasta resumos.
    O parâmetro 'nome_arquivo' deve ser o nome desejado para o arquivo (ex: 'resumo_evento_xyz.txt')."""
    return salvar_resumo_evento_logic(nome_arquivo, resumo)

@mcp.tool()
def delegar_tarefas_evento(nome_arquivo_resumo: str) -> str:
    """Ferramenta que lê um resumo de evento processado, extrai seu nome (via IA), e dispara as mensagens de delegação de tarefas de acordo com destinatarios.xlsx via Telegram. Também cria/atualiza os registros na planilha de eventos."""
    return executar_delegacao(nome_arquivo_resumo)

if __name__ == "__main__":
    mcp.run()
