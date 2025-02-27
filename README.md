# AI Agent + Base
AI Agent para interactuar con Base (AgentKit de Coinbase Development Platform) 

Con AgentKit, los agentes de IA pueden realizar operaciones en Blockchaiin, abriendo nuevas posibilidades para la creación de aplicaciones de blockchain inteligentes. Este agente se puede integrar con cualquier LLM, ahora se está usando Llama3.3 hospedado en Groq, y con cualquier billetera, en este momento el código está usando un smart wallet (y su basename asociado) creado en Base.

## Instrucciones
**Prerequisites**
>* Python 3.10+
>* Poetry (https://python-poetry.org/)
>* CDP API Key Name + CDP API Key Private Key (https://www.coinbase.com/developer-platform)
>* Groq API Key, o bien OPENAI API Key, o cualquier otro modelo con el que se quiera experimentar

**Crear .env a partir de .env.local**
`$ cp .env.local .env`

Los valores de CDP_API_KEY_NAME y CDP_API_KEY_PRIVATE_KEY tiene que copiarse del archivo JSON que se obtiene de la creación del CDP API Key:
CDP_API_KEY_NAME es el valor asociado a *name* (todo lo que está entre comillas)
CDP_API_KEY_PRIVATE_KEY es el valor asociado a *privateKey* (todo lo que está entre comillas)

## Instalar dependencias
`$ poetry install`

## Para correr el AI Agent
`$ poetry run python chatbot.py`

## Wallet
AgentKit usa un wallet temporal, definido en un archivo de texto (wallet_data.txt) si este archivo no se existe entonces se crea uno nuevo.

El contenido del archivo, en formato JSON, tiene los valores de `wallet_id` y `seed`
