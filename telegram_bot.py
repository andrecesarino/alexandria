import os
import json
import threading
import requests
from telegram.ext import Application, CommandHandler
from excel_manager import atualizar_status_evento

CONFIG_CHATS = os.path.join(os.path.dirname(__file__), "config", "telegram_chats.json")

def _get_bot_token():
    config_path = os.path.join(os.path.dirname(__file__), "config")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            for line in f:
                if "Telegram BOT API" in line:
                    return line.split("API:")[1].strip()
    return None

def ler_chats():
    if os.path.exists(CONFIG_CHATS):
        with open(CONFIG_CHATS, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_chats(chats):
    os.makedirs(os.path.dirname(CONFIG_CHATS), exist_ok=True)
    with open(CONFIG_CHATS, "w", encoding="utf-8") as f:
        json.dump(chats, f)

async def registrar_handler(update, context):
    if not context.args:
        await update.message.reply_text("Informe a coordenadoria. Ex: /registrar COPED_ESUMP_GO")
        return
        
    coord = context.args[0]
    chat_id = update.message.chat_id
    
    chats = ler_chats()
    chats[coord] = chat_id
    salvar_chats(chats)
    
    await update.message.reply_text(f"✅ Coordenadoria {coord} vinculada a este chat! (ID: {chat_id})")

async def concluir_handler(update, context):
    if not context.args:
        await update.message.reply_text("Informe o nome exato do evento. Ex: /concluir Seminário de Saúde Local")
        return
        
    nome_evento = " ".join(context.args)
    chat_id = update.message.chat_id
    chats = ler_chats()
    
    encontrada = None
    for c, cid in chats.items():
        if cid == chat_id:
            encontrada = c
            break
            
    if not encontrada:
        await update.message.reply_text("⚠️ Você não está registrado como nenhuma Coordenadoria. Use /registrar")
        return
        
    sucesso = atualizar_status_evento(nome_evento, encontrada, "Concluído")
    if sucesso:
        await update.message.reply_text(f"☑️ Status atualizado! Tarefa de {encontrada} no evento '{nome_evento}' foi marcada como Concluída.")
    else:
        await update.message.reply_text(f"❌ Não foi possível encontrar o evento '{nome_evento}' em andamento ou a sua coordenadoria não está listada para ele.")

def start_bot_blocking():
    token = _get_bot_token()
    if not token:
        print("Telegram API Token não encontrado no arquivo config. Bot não iniciado.")
        return
        
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("registrar", registrar_handler))
    app.add_handler(CommandHandler("concluir", concluir_handler))
    
    print("🤖 Iniciando Bot Telegram (Polling em background)...")
    try:
        # async loop is handled cleanly handled by python-telegram-bot
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f"Erro ao rodar Telegram Polling: {e}")

def iniciar_bot_threads():
    """Inicia o Bot do Telegram numa Thread rodando em background (Daemon)."""
    t = threading.Thread(target=start_bot_blocking, daemon=True)
    t.start()
    return t

def enviar_mensagem_sync(coordenadoria: str, mensagem: str):
    """Envia mensagem síncrona diretamente pela API sem necessitar da instância async rodando."""
    chats = ler_chats()
    chat_id = chats.get(coordenadoria)
    
    if not chat_id:
        print(f"⚠️ Chat ID de '{coordenadoria}' desconhecido. A pessoa não enviou /registrar.")
        return False
        
    token = _get_bot_token()
    if not token:
        return False
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": mensagem,
        "parse_mode": "Markdown"
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        # return whether it was successful
        return resp.status_code == 200
    except Exception as e:
        print(f"Erro efetuando post no Telegram API: {e}")
        return False
