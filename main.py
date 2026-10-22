import os
import pandas as pd
from pypdf import PdfReader
from google import genai
from google.genai import types

# Inicializa o cliente da API do Google GenAI
client = genai.Client()

# Instrução de sistema moldando o comportamento para o Cat Café
system_instruction = (
    "Você é o assistente virtual de um Cat Café aconchegante chamado 'Café com Bigodes'. "
    "Sua interface é um prompt de terminal limpo e direto, sem menus engessados ou jogos. "
    "Você é acolhedor, ama gatos e é capaz de ajudar os clientes a tirar dúvidas, "
    "aprender novas informações passadas pelo usuário na conversa, realizar o agendamento de mesas e horários "
    "(coletando nome, número de pessoas e horário de forma natural e conversacional) "
    "e analisar coerentemente o conteúdo de arquivos (PDF, CSV, JSON) quando fornecidos."
)

chat = client.chats.create(
    model="gemini-3.8-flash",
    config=types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.3,
    )
)

def ler_arquivo(caminho):
    caminho = caminho.strip().strip('"').strip("'")
    if not os.path.exists(caminho):
        return f"[Erro: O arquivo '{caminho}' não foi encontrado.]"
    
    extensao = os.path.splitext(caminho)[1].lower()
    conteudo_extraido = ""

    try:
        if extensao == '.pdf':
            reader = PdfReader(caminho)
            for i, pagina in enumerate(reader.pages):
                texto_pag = pagina.extract_text()
                if texto_pag:
                    conteudo_extraido += f"--- Página {i+1} ---\n{texto_pag}\n"
        elif extensao == '.csv':
            df = pd.read_csv(caminho)
            conteudo_extraido = df.to_string(index=False)
        elif extensao == '.json':
            df = pd.read_json(caminho)
            conteudo_extraido = df.to_string(index=False)
        else:
            return f"[Erro: Formato '{extensao}' não suportado. Use PDF, CSV ou JSON.]"
        
        return f"\n[Conteúdo extraído do arquivo {os.path.basename(caminho)}]:\n{conteudo_extraido}\n"
    except Exception as e:
        return f"[Erro ao processar o arquivo: {str(e)}]"

def main():
    print("=" * 65)
    print("  CAT CAFÉ TERMINAL - Café com Bigodes")
    print("  Converse livremente, ensine dados, agende mesas ou informe arquivos (.pdf, .csv, .json)")
    print("  Digite 'sair' para encerrar a sessão.")
    print("=" * 65 + "\n")

    while True:
        try:
            entrada = input("catcafe@system:~$ ").strip()
            
            if not entrada:
                continue
            
            if entrada.lower() in ["sair", "exit", "quit"]:
                print("\nEncerrando terminal do Cat Café... Até logo! ")
                break

            prompt_final = entrada

            for ext in ['.pdf', '.csv', '.json']:
                if ext in entrada.lower():
                    partes = entrada.split()
                    for p in partes:
                        if ext in p.lower():
                            dados_arquivo = ler_arquivo(p)
                            prompt_final = f"{entrada}\n\n{dados_arquivo}"
                            break

            resposta = chat.send_message(prompt_final)
            print(f"\n{resposta.text}\n")
            print("-" * 65)

        except KeyboardInterrupt:
            print("\nSessão interrompida.")
            break
        except Exception as e:
            print(f"\n[Erro na execução: {e}]\n")

if __name__ == "__main__":
    main()
