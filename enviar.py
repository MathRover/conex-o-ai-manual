import time
import requests
from google import genai
from google.genai import types
import json
import os

# ==========================
# CONFIGURAÇÕES
# ==========================
ASSEMBLYAI_API_KEY = "ab9e6f2e2c2341d49f29b2d61b1c6b21"
GENAI_API_KEY = "AIzaSyBYNOepm2WsceHg0rPQ7wIKbcIIE7OEcXk"
CHAMADO_URL = "http://10.0.0.178:5000/chamado/create"

BASE_V2 = "https://api.assemblyai.com/v2"
HEADERS = {"authorization": ASSEMBLYAI_API_KEY}

# ==========================
# FUNÇÕES ASSEMBLYAI
# ==========================
def upload_file(filepath: str) -> str:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
    with open(filepath, "rb") as f:
        headers = HEADERS.copy()
        headers["content-type"] = "application/octet-stream"
        resp = requests.post(f"{BASE_V2}/upload", headers=headers, data=f)
        resp.raise_for_status()
    return resp.json()["upload_url"]

def create_transcript(audio_url: str, speech_model: str = "universal") -> str:
    payload = {"audio_url": audio_url, "speech_model": speech_model, "language_code": "pt"}
    resp = requests.post(f"{BASE_V2}/transcript", json=payload, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()["id"]

def poll_transcript(transcript_id: str, interval: int = 3, timeout: int = 600) -> str:
    endpoint = f"{BASE_V2}/transcript/{transcript_id}"
    start = time.time()
    while True:
        resp = requests.get(endpoint, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status")
        if status == "completed":
            return data.get("text", "")
        if status == "error":
            raise RuntimeError("Transcription failed: " + data.get("error", "unknown"))
        if time.time() - start > timeout:
            raise TimeoutError("Polling timed out")
        time.sleep(interval)

# ==========================
# FUNÇÃO GOOGLE GEMINI
# ==========================
def generate_chamado(texto_transcrito: str) -> str:
    client = genai.Client(api_key=GENAI_API_KEY)

    prompt = f"""
Crie um chamado de suporte técnico em formato JSON com os campos:
titulo, descricao e status (criado, atendido ou fechado). 
Baseie-se neste texto transcrito do áudio: {texto_transcrito}
""".strip()

    # ⚠️ SEM role, apenas parts
    contents = [types.Content(parts=[types.Part(text=prompt)])]

    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(),
        response_mime_type="application/json"
    )

    generated = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=config
    )

    # pega o JSON real
    if hasattr(generated, "candidates") and len(generated.candidates) > 0:
        candidate = generated.candidates[0]
        if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
            json_str = candidate.content.parts[0].text
        else:
            raise RuntimeError("Resposta do modelo não contém 'parts'")
    else:
        raise RuntimeError("Falha ao gerar o chamado: resposta inválida do modelo")

    print("=== JSON GERADO ===")
    print(json_str)
    return json_str

# ==========================
# FUNÇÃO PARA ENVIAR CHAMADO COM FALLBACK
# ==========================
def send_chamado(json_str: str):
    try:
        chamado_data = json.loads(json_str)
        response = requests.post(
            CHAMADO_URL,
            json=chamado_data,
            timeout=10
        )
        print("=== STATUS DO SERVIDOR ===", response.status_code)
        print("=== RESPOSTA DO SERVIDOR ===", response.text)

        if response.status_code == 405:
            with open("chamado_fallback.json", "w", encoding="utf-8") as f:
                f.write(json_str)
            print("⚠️ Endpoint não aceita POST. JSON salvo em chamado_fallback.json")

    except Exception as e:
        print("Erro ao enviar chamado:", e)
        with open("chamado_fallback.json", "w", encoding="utf-8") as f:
            f.write(json_str)
        print("JSON salvo localmente em chamado_fallback.json")

# ==========================
# EXECUÇÃO PRINCIPAL
# ==========================
if __name__ == "__main__":
    filepath = "audio Rover.opus"  # arquivo de áudio na mesma pasta do script

    print("📤 Fazendo upload do áudio...")
    audio_url = upload_file(filepath)

    print("📜 Criando transcrição...")
    transcript_id = create_transcript(audio_url)

    print("⏳ Aguardando transcrição terminar...")
    transcript_text = poll_transcript(transcript_id)

    print("\n=== TRANSCRIÇÃO ===")
    print(transcript_text[:400] + ("..." if len(transcript_text) > 400 else ""))

    print("\n🤖 Gerando chamado com Google Gemini...")
    json_chamado = generate_chamado(transcript_text)

    print("\n📨 Tentando enviar chamado para a API...")
    send_chamado(json_chamado)

    print("\n✅ Processo concluído!")
