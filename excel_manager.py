import os
import pandas as pd

DEST_PATH = os.path.join(os.path.dirname(__file__), "destinatarios", "destinatarios.xlsx")
EVENTOS_PATH = os.path.join(os.path.dirname(__file__), "destinatarios", "eventos.xlsx")

def ler_destinatarios():
    """Lê a planilha de destinatários e retorna dict: {'COORD': 'MENSAGEM BASE', ...}"""
    if not os.path.exists(DEST_PATH):
        print("Aviso: destinatarios.xlsx não encontrado.")
        return {}
        
    try:
        df = pd.read_excel(DEST_PATH)
        return dict(zip(df["Destinatários"], df["Mensagem"]))
    except Exception as e:
        print(f"Erro ao ler destinatarios: {e}")
        return {}

def gerar_proximo_id() -> str:
    """Inspeciona a planilha de eventos para encontrar o próximo ID 6-digits válido sequêncialmente."""
    base_inicial = 100001
    if not os.path.exists(EVENTOS_PATH):
        return str(base_inicial)
        
    try:
        df = pd.read_excel(EVENTOS_PATH)
        if df.empty or "ID" not in df.columns:
            return str(base_inicial)
            
        valores = pd.to_numeric(df["ID"], errors='coerce').dropna()
        if len(valores) > 0:
            proximo = int(valores.max()) + 1
            return f"{proximo:06d}"
        else:
            return str(base_inicial)
    except Exception as e:
        print(f"Erro buscando ID sequencial: {e}")
        return str(base_inicial)

def inserir_novo_evento(id_evento: str, nome_evento: str, coordenadorias: list):
    """Insere o evento na eventos.xlsx, zerado como Em Andamento, contendo seu ID."""
    # Carrega ou cria do zero
    if os.path.exists(EVENTOS_PATH):
        df = pd.read_excel(EVENTOS_PATH)
    else:
        colunas = ["ID", "Evento"] + coordenadorias
        df = pd.DataFrame(columns=colunas)
        
    # Garante que as colunas das coodenadorias existem nessa DF
    for c in coordenadorias:
        if c not in df.columns:
            df[c] = "-"
            
    novo_registro = {"ID": id_evento, "Evento": nome_evento}
    for coord in coordenadorias:
        novo_registro[coord] = "Em Andamento"
        
    novo_df = pd.DataFrame([novo_registro])
    df = pd.concat([df, novo_df], ignore_index=True)
    
    try:
        df.to_excel(EVENTOS_PATH, index=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar eventos.xlsx: {e}")
        return False

def atualizar_status_evento(referencia: str, coordenadoria: str, status: str = "Concluído"):
    """
    Atualiza eventos.xlsx para uma coordenadoria específica de um evento via Bot. Aceita NOME ou ID.
    """
    if not os.path.exists(EVENTOS_PATH):
        return False
        
    try:
        df = pd.read_excel(EVENTOS_PATH)
        mask = (df["Evento"].astype(str).str.strip().str.lower() == referencia.strip().lower()) | (df["ID"].astype(str).str.strip() == referencia.strip())
        
        if mask.any():
            if coordenadoria in df.columns:
                df.loc[mask, coordenadoria] = status
                df.to_excel(EVENTOS_PATH, index=False)
                return True
        return False
    except Exception as e:
        print(f"Erro atualizando excel: {e}")
        return False
