transcricao-e-chamado

Script Python para transcrever áudios em português usando AssemblyAI e gerar automaticamente chamados de suporte técnico em JSON utilizando Google Gemini. Inclui fallback para salvar localmente caso o endpoint não aceite POST.

Funcionalidades

Upload de arquivos de áudio para AssemblyAI.

Transcrição automática do áudio para texto em português.

Geração de chamado de suporte técnico em formato JSON via Google Gemini, com campos:

titulo

descricao

status (criado, atendido, fechado)

Envio do chamado para um endpoint via POST ou fallback local (chamado_fallback.json) caso haja erro.

Pré-requisitos

Python 3.10+

Bibliotecas:

pip install requests google-genai


Chaves de API:

ASSEMBLYAI_API_KEY → para AssemblyAI

GENAI_API_KEY → para Google Gemini

Endpoint de chamado (CHAMADO_URL) configurado.

Uso

Configure o arquivo com suas chaves de API e URL do endpoint:

ASSEMBLYAI_API_KEY = "SUA_CHAVE_AQUI"
GENAI_API_KEY = "SUA_CHAVE_AQUI"
CHAMADO_URL = "SEU_ENDPOINT_AQUI"
filepath = "caminho/para/o/audio.mp3"


Execute o script:

python seu_script.py


O script fará:

Upload do áudio.

Criação da transcrição.

Geração do chamado em JSON.

Envio para a API ou salvamento local em caso de falha.

Estrutura do Chamado JSON
{
  "titulo": "Resumo do problema",
  "descricao": "Texto detalhado do chamado",
  "status": "criado"
}

Observações

Caso o endpoint não aceite POST, o JSON será salvo localmente em chamado_fallback.json.

O script limita o texto exibido da transcrição a 400 caracteres na tela, mas envia o conteúdo completo para a geração do chamado.