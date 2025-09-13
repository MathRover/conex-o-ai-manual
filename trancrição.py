import assemblyai as aai

# ⚠️ Coloque sua chave da AssemblyAI aqui
aai.settings.api_key = "ab9e6f2e2c2341d49f29b2d61b1c6b21"

# 1) Se quiser usar arquivo local:
# audio_file = "./meu_audio.opus"

# 2) Ou arquivo público:
audio_file = "https://assembly.ai/wildfires.mp3"

# Configuração da transcrição (PT-BR)
config = aai.TranscriptionConfig(
    speech_model=aai.SpeechModel.universal,
    language_code="pt"  # força transcrição em português
)

# Fazendo a transcrição
transcriber = aai.Transcriber(config=config)
transcript = transcriber.transcribe(audio_file)

# Checando erros
if transcript.status == "error":
    raise RuntimeError(f"Transcription failed: {transcript.error}")

# Mostrando o resultado
print("=== TRANSCRIÇÃO ===")
print(transcript.text)

# Salvando em arquivo
with open("transcript.txt", "w", encoding="utf-8") as f:
    f.write(transcript.text)

print("\n✅ Transcrição salva em transcript.txt")
