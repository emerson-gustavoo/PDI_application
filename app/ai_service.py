"""Servico de IA: gera o Plano de Desenvolvimento Individual (PDI).

Este modulo concentra TODA a integracao com a Inteligencia Artificial.
A funcao publica e generate_pdi(dados) -> dict. Ela monta um prompt,
chama o provider configurado e devolve um dicionario estruturado.

Trocar de provider (Anthropic / OpenAI / Gemini) e isolado aqui dentro:
basta implementar uma funcao _call_<provider> e plugar no dispatch.
"""
import json
import re

from .config import settings


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """Voce e um mentor de carreira senior especializado na area de
Tecnologia da Informacao. Seu trabalho e analisar o perfil de um profissional e
montar um Plano de Desenvolvimento Individual (PDI) realista, acionavel e
personalizado.

Responda SEMPRE e SOMENTE com um objeto JSON valido, sem texto antes ou depois,
sem blocos de markdown. O JSON deve seguir EXATAMENTE este formato:

{
  "diagnostico": "paragrafo analisando a situacao atual do profissional",
  "pontos_fortes": ["ponto 1", "ponto 2", "ponto 3"],
  "gaps": ["competencia/lacuna a desenvolver 1", "lacuna 2", "lacuna 3"],
  "trilha": [
    {
      "etapa": 1,
      "titulo": "nome da etapa",
      "descricao": "o que estudar/praticar nesta etapa",
      "duracao_estimada": "ex: 4 semanas",
      "recursos": ["recurso ou curso sugerido 1", "recurso 2"]
    }
  ],
  "certificacoes": [
    {
      "nome": "nome da certificacao",
      "motivo": "por que faz sentido para este perfil",
      "prioridade": "alta"
    }
  ],
  "cronograma": [
    {"periodo": "Mes 1-2", "foco": "descricao do foco do periodo"}
  ],
  "proximos_passos": ["acao imediata 1", "acao imediata 2"]
}

Regras:
- "prioridade" deve ser exatamente: alta, media ou baixa.
- Inclua de 3 a 5 etapas na trilha, coerentes com as horas semanais informadas.
- Recomende de 2 a 4 certificacoes reais e relevantes para o objetivo.
- Seja concreto: cite tecnologias, ferramentas e nomes reais de cursos/certificacoes.
"""


def _build_user_prompt(d: dict) -> str:
    return f"""Monte o PDI para o seguinte profissional:

- Cargo atual: {d['cargo_atual']}
- Nivel de experiencia: {d['nivel_experiencia']}
- Area de interesse / para onde quer ir: {d['area_interesse']}
- Objetivo principal: {d['objetivo']}
- Tecnologias que ja conhece: {d['tecnologias']}
- Horas disponiveis por semana para estudar: {d['horas_semanais']}

Gere o JSON do PDI."""


# ---------------------------------------------------------------------------
# Utilitario: extrair JSON de forma tolerante
# ---------------------------------------------------------------------------
def _parse_json(text: str) -> dict:
    """Tenta extrair um objeto JSON mesmo que venha com cercas de markdown."""
    text = text.strip()
    # Remove cercas ```json ... ```
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Ultima tentativa: pega do primeiro { ate o ultimo }
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start : end + 1])
        raise


# ---------------------------------------------------------------------------
# Providers
# ---------------------------------------------------------------------------
def _call_anthropic(user_prompt: str) -> str:
    import anthropic

    if not settings.anthropic_api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY nao configurada. Preencha o .env ou use AI_PROVIDER=mock."
        )

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    message = client.messages.create(
        model=settings.ai_model,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    # Concatena os blocos de texto da resposta
    return "".join(block.text for block in message.content if block.type == "text")


def _call_gemini(user_prompt: str) -> str:
    from google import genai
    from google.genai import types

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY nao configurada. Preencha o .env ou use AI_PROVIDER=mock."
        )

    client = genai.Client(api_key=settings.gemini_api_key)
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            # Forca a resposta a sair em JSON puro (sem cercas de markdown)
            response_mime_type="application/json",
        ),
    )
    return response.text


def _call_mock(user_prompt: str) -> str:
    """Resposta falsa para testar a app sem consumir API. NAO usar na entrega."""
    return json.dumps(
        {
            "diagnostico": "[MODO MOCK] Profissional com base solida e bom potencial de evolucao.",
            "pontos_fortes": ["Base tecnica consistente", "Experiencia pratica", "Vontade de evoluir"],
            "gaps": ["Aprofundar em nuvem", "Praticas de automacao", "Soft skills de lideranca"],
            "trilha": [
                {
                    "etapa": 1,
                    "titulo": "Fundamentos de Cloud",
                    "descricao": "Estudar conceitos de computacao em nuvem.",
                    "duracao_estimada": "4 semanas",
                    "recursos": ["Curso introdutorio de AWS", "Documentacao oficial"],
                }
            ],
            "certificacoes": [
                {"nome": "AWS Certified Cloud Practitioner", "motivo": "Porta de entrada em nuvem", "prioridade": "alta"}
            ],
            "cronograma": [{"periodo": "Mes 1-2", "foco": "Fundamentos e primeira certificacao"}],
            "proximos_passos": ["Criar conta gratuita na AWS", "Definir agenda de estudos"],
        },
        ensure_ascii=False,
    )


_PROVIDERS = {
    "anthropic": _call_anthropic,
    "gemini": _call_gemini,
    "mock": _call_mock,
}


# ---------------------------------------------------------------------------
# API publica
# ---------------------------------------------------------------------------
def generate_pdi(dados: dict) -> dict:
    """Recebe os dados do perfil e devolve o PDI estruturado (dict)."""
    provider = _PROVIDERS.get(settings.ai_provider)
    if provider is None:
        raise RuntimeError(f"AI_PROVIDER '{settings.ai_provider}' nao suportado.")

    raw = provider(_build_user_prompt(dados))
    return _parse_json(raw)
