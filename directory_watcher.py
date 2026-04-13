import os
import time
import shutil
import threading
from pypdf import PdfReader
from ai_manager import gerar_resumo_evento
from task_delegator import executar_delegacao

ENTRADA_DIR = os.path.join(os.path.dirname(__file__), "entrada")
PROCESSADOS_DIR = os.path.join(ENTRADA_DIR, "processados")
RESUMOS_DIR = os.path.join(os.path.dirname(__file__), "resumos")

def extrair_texto_pdf(filepath):
    """Lê todas as páginas do PDF e junta como texto puro."""
    try:
        reader = PdfReader(filepath)
        text = ""
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"--- PÁGINA {i+1} ---\n{page_text}\n\n"
        return text
    except Exception as e:
        print(f"Erro ao ler pacote PDF {filepath}: {e}")
        return ""

def watcher_loop():
    """Função do observador rodando infinitamente e processando .pdf."""
    os.makedirs(ENTRADA_DIR, exist_ok=True)
    os.makedirs(PROCESSADOS_DIR, exist_ok=True)
    os.makedirs(RESUMOS_DIR, exist_ok=True)
    
    print("👀 Watcher ativado: Vigiando a pasta 'entrada/' a cada 10 segundos...")
    while True:
        try:
            for f in os.listdir(ENTRADA_DIR):
                if f.lower().endswith(".pdf"):
                    filepath = os.path.join(ENTRADA_DIR, f)
                    
                    if not os.path.isfile(filepath):
                        continue
                        
                    print(f"\n[Watcher] 📄 Novo PDF detectado: {f}")
                    # Extrai texto
                    texto = extrair_texto_pdf(filepath)
                    if not texto:
                        print(f"[Watcher] ⚠️ Arquivo {f} ignorado, texto vazio ou falha na leitura.")
                        try: shutil.move(filepath, os.path.join(PROCESSADOS_DIR, f))
                        except: pass
                        continue
                        
                    print(f"[Watcher] 🤖 Gerando resumo inteligente para {f} (isso pode levar alguns segundos)...")
                    resumo = gerar_resumo_evento(texto)
                    
                    # Salva resumo substituindo extensão por txt
                    base_name = os.path.splitext(f)[0]
                    nome_resumo = f"{base_name}_resumo.txt"
                    caminho_resumo = os.path.join(RESUMOS_DIR, nome_resumo)
                    with open(caminho_resumo, "w", encoding="utf-8") as res_file:
                        res_file.write(resumo)
                    
                    print(f"[Watcher] 💾 Resumo oficial escrito em resumos/{nome_resumo}")
                    
                    # Delega tarefas de forma orgânica e local
                    print("[Watcher] 🚀 Iniciando automatização de delegação / envio Telegram...")
                    resultado = executar_delegacao(nome_resumo)
                    print(f"[Watcher] ✅ Processamento de delegações Concluído!\n{resultado}")
                    
                    # Ao final absoluto e de sucesso, move o arquivo
                    print(f"[Watcher] 🧹 Movendo {f} para pasta de histórico processados...")
                    try:
                        shutil.move(filepath, os.path.join(PROCESSADOS_DIR, f))
                    except Exception as me:
                        print(f"[Watcher] Erro ao mover arquivo original: {me}")
                        
        except Exception as e:
            print(f"[Watcher] Erro no loop global: {e}")
            
        time.sleep(10)

def iniciar_observador_threads():
    """Inicia o observador autonômo que rodará vigiando os pdfs em background."""
    t = threading.Thread(target=watcher_loop, daemon=True)
    t.start()
    return t
