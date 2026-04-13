import os
from ai_manager import extrair_nome_evento, gerar_mensagem_coordenadoria
from excel_manager import ler_destinatarios, inserir_novo_evento, gerar_proximo_id
from telegram_bot import enviar_mensagem_sync

RESUMOS_DIR = os.path.join(os.path.dirname(__file__), "resumos")

def executar_delegacao(nome_arquivo_resumo: str) -> str:
    """Ferramenta central que lê o resumo, delega tarefas no excel e dispara os avisos no Telegram."""
    filepath = os.path.join(RESUMOS_DIR, nome_arquivo_resumo)
    if not os.path.exists(filepath):
        return f"Erro: Arquivo '{nome_arquivo_resumo}' não encontrado em resumos/."
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            resumo_texto = f.read()
    except Exception as e:
        return f"Erro ao ler resumo: {str(e)}"
        
    print("Processando inteligência para extrair informações do evento...")
    nome_evento = extrair_nome_evento(resumo_texto)
    id_evento = gerar_proximo_id()
    print(f"Nome extraído: {nome_evento} | ID sequencial gerado: {id_evento}")
    
    # Adicionar ID ao final do arquivo físico do Resumo caso as pessoas abram a pasta
    try:
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(f"\n\n--- ID DO EVENTO REFERÊNCIA: {id_evento} ---\n")
    except Exception as e:
        print(f"Aviso ao salvar ID fisicamente: {e}")
    
    # 1. Recuperar destinatarios
    destinatarios = ler_destinatarios()
    if not destinatarios:
        return "Erro: Planilha destinatarios.xlsx não encontrada ou está vazia."
        
    # 2. Inserir em eventos.xlsx
    coordenadorias = list(destinatarios.keys())
    inserir_novo_evento(id_evento, nome_evento, coordenadorias)
    
    # 3. Formatar e disparar mensagens para cada Coordenadoria
    relatorios = []
    for coord, base_msg in destinatarios.items():
        mensagem_final = gerar_mensagem_coordenadoria(id_evento, nome_evento, base_msg, resumo_texto)
        enviado = enviar_mensagem_sync(coord, mensagem_final)
        if enviado:
            relatorios.append(f"✅ {coord} (Enviado com sucesso)")
        else:
            relatorios.append(f"❌ {coord} (Falhou: Chat ID não registrado via bot)")
            
    resultado = (
        f"Delegação Concluída para o evento '{nome_evento}'.\n"
        f"Acompanhamento registrado em eventos.xlsx!\n\nStatus de Envio:\n" +
        "\n".join(relatorios)
    )
    return resultado
