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

def inserir_novo_evento(nome_evento: str, coordenadorias: list):
    """Insere o evento na eventos.xlsx, zerado como Em Andamento."""
    # Carrega ou cria do zero
    if os.path.exists(EVENTOS_PATH):
        df = pd.read_excel(EVENTOS_PATH)
    else:
        colunas = ["Evento"] + coordenadorias
        df = pd.DataFrame(columns=colunas)
        
    # Garante que as colunas das coodenadorias existem nessa DF
    for c in coordenadorias:
        if c not in df.columns:
            df[c] = "-"
            
    novo_registro = {"Evento": nome_evento}
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

def atualizar_status_evento(nome_evento: str, coordenadoria: str, status: str = "Concluído"):
    """
    Atualiza eventos.xlsx para uma coordenadoria específica de um evento via Bot.
    """
    if not os.path.exists(EVENTOS_PATH):
        return False
        
    try:
        df = pd.read_excel(EVENTOS_PATH)
        mask = df["Evento"].astype(str).str.strip().str.lower() == nome_evento.strip().lower()
        
        if mask.any():
            if coordenadoria in df.columns:
                df.loc[mask, coordenadoria] = status
                df.to_excel(EVENTOS_PATH, index=False)
                return True
        return False
    except Exception as e:
        print(f"Erro atualizando excel: {e}")
        return False
