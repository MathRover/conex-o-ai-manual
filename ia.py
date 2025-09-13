import requests
import time

API_KEY = "ab9e6f2e2c2341d49f29b2d61b1c6b21"  
if not API_KEY:
    raise RuntimeError("Defina a variável de ambiente ASSEMBLYAI_API_KEY")

BASE_V2 = "https://api.assemblyai.com/v2"
HEADERS = {"authorization": API_KEY}


def upload_file(filepath: str) -> str:
    """Faz upload de um arquivo local e retorna o upload_url."""
    url = f"{BASE_V2}/upload"
    with open(filepath, "rb") as f:
        upload_headers = HEADERS.copy()
        upload_headers["content-type"] = "application/octet-stream"
        resp = requests.post(url, headers=upload_headers, data=f)
        resp.raise_for_status()
    return resp.json()["upload_url"]


def create_transcript(audio_url: str, speech_model: str = "universal", **options) -> dict:
    """Cria a requisição de transcrição. Retorna o JSON de criação (contém 'id')."""
    payload = {
        "audio_url": audio_url,
        "speech_model": speech_model,  
        "language_code": "pt" 
    }
    payload.update(options)
    resp = requests.post(f"{BASE_V2}/transcript", json=payload, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def poll_transcript(transcript_id: str, interval: int = 3, timeout: int = 600) -> dict:
    """Faz polling até status completed ou error. Timeout em segundos."""
    endpoint = f"{BASE_V2}/transcript/{transcript_id}"
    start = time.time()
    while True:
        resp = requests.get(endpoint, headers=HEADERS)
        resp.raise_for_status()
        j = resp.json()
        status = j.get("status")

        if status == "completed":
            return j
        if status == "error":
            raise RuntimeError("Transcription failed: " + j.get("error", "unknown"))

        if time.time() - start > timeout:
            raise TimeoutError("Polling timed out")

        time.sleep(interval)


if __name__ == "__main__":
    # ⚠️ Nome do seu arquivo (mesma pasta do .py)
    filepath = "Áudio do WhatsApp de 2025-09-13 à(s) 10.37.18_e1956e90.waptt.opus"

    print("📤 Fazendo upload do arquivo...")
    audio_url = upload_file(filepath)

    print("📜 Criando pedido de transcrição (PT-BR)...")
    created = create_transcript(audio_url, speech_model="universal")
    tid = created["id"]

    print("⏳ Aguardando AssemblyAI terminar...")
    result = poll_transcript(tid)

    transcript_text = result.get("text", "")
    print("\n=== TRANSCRIÇÃO (PT-BR) ===")
    print(transcript_text[:400] + ("..." if len(transcript_text) > 400 else ""))

    with open("transcript.txt", "w", encoding="utf-8") as f:
        f.write(transcript_text)

    print("\n✅ Transcrição salva em transcript.txt")

    

    
