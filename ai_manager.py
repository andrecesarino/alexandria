import os
from google import genai

def _get_gemini_key():
    config_path = os.path.join(os.path.dirname(__file__), "api_config.txt")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            for line in f:
                if "GOOGLE AI Studio API" in line:
                    parts = line.split(":")
                    code = parts[1].split("(")[0].strip()
                    return code
    return None

_KEY = _get_gemini_key()
_client = None
if _KEY:
    _client = genai.Client(api_key=_KEY)

def gerar_resumo_evento(texto_pdf: str) -> str:
    """Extrai informações extensas do PDF e gera um resumo oficial formatado."""
    try:
        if not _client:
            return "Erro: Client AI não inicializado."
            
        prompt = (
            "Faça a extração dos dados relevantes do PDF deste Evento e gere um sumário organizado.\n"
            "Mantenha tópicos práticos e o contexto necessário para que a equipe do evento saiba atuar.\n\n"
            f"TEXTO DO PDF:\n{texto_pdf}"
        )
        response = _client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"Erro ao gerar resumo: {str(e)[:100]}"

def extrair_nome_evento(resumo: str) -> str:
    """Extrai apenas o nome do evento mais adequado a partir do resumo usando Gemini."""
    try:
        if not _client:
            return "Erro-Init-AI"
            
        prompt = (
            "Baseado no resumo abaixo, extraia e retorne APENAS o título/nome "
            "oficial e curto do evento. Não use aspas, quebras de linha ou explicações.\n\n"
            f"RESUMO:\n{resumo}"
        )
        response = _client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.replace('"', '').strip()
    except Exception as e:
        return f"Erro-Extracao-Evento-{str(e)[:5]}"

def gerar_mensagem_coordenadoria(id_evento: str, nome_evento: str, base_mensagem: str, resumo: str) -> str:
    """Gera o texto final a ser preenchido/enviado para o Telegram da Coordenadoria, alertando sobre o ID."""
    # Como fallback seguro, fazemos replace direto
    fallback = base_mensagem.replace("<NOME_EVENTO>", nome_evento) + f"\n\n[ID do Evento para dar baixa: {id_evento}]"
    
    try:
        if not _client:
            return fallback
            
        prompt = (
            f"Você é um assistente encarregado de delegar uma tarefa para a equipe do evento '{nome_evento}'.\n"
            f"A instrução base para a equipe é esta: {base_mensagem.replace('<NOME_EVENTO>', nome_evento)}\n\n"
            f"Aqui estão os detalhes do Evento:\n{resumo}\n\n"
            "Crie UMA mensagem profissional de Telegram passando essa tarefa e algum detalhe relevante "
            "do evento se achar necessário para eles cumprirem seu trabalho. Seja direto.\n"
            f"OBRIGATÓRIO: Mencione explicitamente no fim da mensagem que o ID deste evento é {id_evento} e informe que eles precisarão responder este bot usando o comando /concluir {id_evento} assim que terminarem!"
        )
        response = _client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text.strip()
        if text: return text
    except Exception:
        pass
    
    return fallback
