import os
import google.generativeai as genai

def _get_gemini_key():
    config_path = os.path.join(os.path.dirname(__file__), "config")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            for line in f:
                if "GOOGLE AI Studio API" in line:
                    parts = line.split(":")
                    code = parts[1].split("(")[0].strip()
                    return code
    return None

_KEY = _get_gemini_key()
if _KEY:
    genai.configure(api_key=_KEY)

def extrair_nome_evento(resumo: str) -> str:
    """Extrai apenas o nome do evento mais adequado a partir do resumo usando Gemini."""
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        prompt = (
            "Baseado no resumo abaixo, extraia e retorne APENAS o título/nome "
            "oficial e curto do evento. Não use aspas, quebras de linha ou explicações.\n\n"
            f"RESUMO:\n{resumo}"
        )
        response = model.generate_content(prompt)
        return response.text.replace('"', '').strip()
    except Exception as e:
        return f"Erro-Extracao-Evento-{str(e)[:5]}"

def gerar_mensagem_coordenadoria(nome_evento: str, base_mensagem: str, resumo: str) -> str:
    """Gera o texto final a ser preenchido/enviado para o Telegram da Coordenadoria."""
    # Como fallback seguro, fazemos replace direto
    fallback = base_mensagem.replace("<NOME_EVENTO>", nome_evento)
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = (
            f"Você é um assistente encarregado de delegar uma tarefa para a equipe do evento '{nome_evento}'.\n"
            f"A instrução base para a equipe é esta: {base_mensagem.replace('<NOME_EVENTO>', nome_evento)}\n\n"
            f"Aqui estão os detalhes do Evento:\n{resumo}\n\n"
            "Crie UMA mensagem profissional de Telegram passando essa tarefa e algum detalhe relevante "
            "do evento se achar necessário para eles cumprirem seu trabalho. Seja direto. Apenas retorne a mensagem a enviar."
        )
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text: return text
    except Exception:
        pass
    
    return fallback
