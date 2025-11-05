# J.A.R.V.I.S Ultra Autoevolutivo - Gerenciador Inteligente de Projetos para Termux

## Visão Geral

O **J.A.R.V.I.S Ultra Autoevolutivo** é um assistente inteligente completo para gerenciamento de projetos no ambiente Termux. Ele combina detecção automática de projetos, configuração de ambientes, engenharia de software assistida por IA, sistema RAG (Retrieval Augmented Generation), reconhecimento e síntese de voz, e capacidade de autoevolução.

## Funcionalidades Principais

### 🤖 Assistente de Voz Inteligente
*   **Reconhecimento de Fala**: Suporta VOSK (offline) via `termux-microphone-record` para capturar comandos de voz
*   **Síntese de Voz (TTS)**: Utiliza `termux-tts-speak` (nativo), `gTTS` (online) ou `pyttsx3` (offline, pode ter limitações no Termux) para feedback por voz
*   **Comandos por Voz**: Execute ações apenas falando, como "Jarvis, escaneie downloads"

### 📁 Gerenciamento Automático de Projetos
*   **Detecção Automática**: Escaneia diretórios configuráveis para identificar projetos Python, Node.js e arquivos ZIP
*   **Extração de ZIPs**: Descompacta automaticamente arquivos ZIP encontrados em downloads
*   **Configuração de Ambientes**: Cria ambientes virtuais (venv para Python, npm install para Node.js)
*   **Atalhos Rápidos**: Gera atalhos executáveis em `~/.shortcuts` para acesso rápido

### 🧠 Auto-Engineer com IA
*   **Análise de Código**: Examina projetos e identifica oportunidades de melhoria
*   **Geração de Patches**: Cria sugestões de código usando IA (Hugging Face API ou mock local)
*   **Sandbox Seguro**: Testa modificações em ambiente isolado antes de aplicar
*   **Controle de Versão**: Integração com Git para rastreamento e reversão de alterações
*   **Níveis de Agressividade**: Configurável (low, medium, high) para controle de auto-aplicação

### 📚 Sistema RAG (Retrieval Augmented Generation)
*   **Indexação de Documentos**: Armazena e indexa código, documentação e logs
*   **Consultas Inteligentes**: Responde perguntas contextuais sobre projetos
*   **Aprendizado Contínuo**: Melhora respostas com base em padrões detectados

### 🎨 Gerador de Templates
*   **Telegram Bot**: Template completo para bots do Telegram em Python
*   **Flask App**: Aplicação web Flask com estrutura básica
*   **React App**: Aplicação React com Vite

### 🧠 Memória Persistente
*   **Preferências do Usuário**: Armazena configurações (agressividade, confirmação por voz, idioma)
*   **Histórico de Eventos**: Registra todas as ações realizadas
*   **Aprendizado de Padrões**: Identifica e armazena padrões recorrentes
*   **Histórico de Projetos**: Mantém registro de todas as ações por projeto

### 📊 Dashboard Interativo
*   **Interface Streamlit**: Visualização completa de projetos, logs e métricas
*   **Controle do Auto-Engineer**: Inicie ciclos de análise e aplicação de patches
*   **Consultas RAG**: Interface para fazer perguntas ao sistema
*   **Visualização de Métricas**: Acompanhe o desempenho e evolução do sistema

### 🔄 Autoevolução
*   **Backups Automáticos**: Cria backups antes de qualquer modificação em `~/.jarvis_backups`
*   **Logs Detalhados**: Registra todas as atividades em `~/.jarvis_activity.log` e `~/.jarvis_memory.json`
*   **Melhoria Contínua**: Aprende com padrões e otimiza suas próprias operações

## Estrutura do Projeto

```
projeto_final/
├── install_termux.sh           # Script de instalação principal
├── requirements.txt            # Dependências Python
├── README.md                   # Este arquivo
├── core/                       # Módulos centrais
│   ├── project_scan.py         # Detecção de projetos
│   ├── env_manager.py          # Gerenciamento de ambientes
│   ├── sandbox.py              # Ambiente de testes seguro
│   ├── shortcuts_manager.py    # Gerenciamento de atalhos
│   ├── rag_core.py             # Sistema RAG
│   ├── memory_manager.py       # Memória persistente
│   ├── voice_assistant.py      # Assistente de voz
│   ├── action_router.py        # Roteador de ações
│   ├── template_generator.py   # Gerador de templates
│   ├── assistente_main.py      # Loop principal do assistente
│   └── auto_updater.py         # Módulo de autoatualização
├── engineer/                   # Engenharia assistida por IA
│   ├── auto_engineer.py        # Orquestrador principal
│   ├── patch_generator.py      # Geração de patches
│   ├── git_ops.py              # Operações Git
│   ├── logger.py               # Logging estruturado
│   └── metrics.py              # Coleta de métricas
├── interface/                  # Interface do usuário
│   └── streamlit_dashboard.py  # Dashboard web
├── scripts/                    # Scripts auxiliares
│   ├── diagnostic.sh           # Diagnóstico do sistema
│   ├── install_termux.sh       # Instalação de dependências
│   ├── start_assistente.sh     # Iniciar assistente de voz
│   ├── stop_assistente.sh      # Parar assistente de voz
│   ├── jarvis_quickstart.sh    # Início rápido completo
│   ├── scan_and_setup.sh       # Scan e configuração
│   ├── master_launcher.sh      # Lançador principal
│   └── create_termux_widgets.sh# Criação de widgets
├── data/                       # Dados persistentes
│   ├── index.json
│   ├── metrics.json
│   └── docs_store.json
└── history/                    # Logs e snapshots
```

## Instalação no Termux

### Método 1: Instalação Completa (Recomendado)

1.  **Baixe o arquivo ZIP** para seu dispositivo Android
2.  **Abra o Termux** e configure o armazenamento:
    ```bash
    termux-setup-storage
    ```
3.  **Descompacte o projeto**:
    ```bash
    cd ~
    unzip ~/storage/downloads/projeto_final_jarvis_ultra_v2.zip -d ~/projects
    cd ~/projects/projeto_final
    ```
4.  **Execute o Quick Start**:
    ```bash
    bash scripts/jarvis_quickstart.sh
    ```

### Método 2: Instalação Manual

1.  **Descompacte o projeto** (como acima)
2.  **Dê permissões de execução**:
    ```bash
    chmod -R +x scripts
    chmod +x install_termux.sh
    ```
3.  **Execute o diagnóstico**:
    ```bash
    bash scripts/diagnostic.sh
    ```
4.  **Instale as dependências**:
    ```bash
    bash scripts/install_termux.sh
    ```
5.  **Inicie o assistente**:
    ```bash
    bash scripts/start_assistente.sh
    ```

## Como Usar

### Comandos de Voz

Com o assistente rodando, você pode usar comandos de voz:

*   **"Jarvis, escaneie downloads"** - Procura e importa ZIPs da pasta de downloads
*   **"Jarvis, escaneie projetos"** - Detecta todos os projetos nos diretórios configurados
*   **"Jarvis, configure ambientes"** - Configura ambientes virtuais para todos os projetos

### Dashboard Web

Abra o dashboard Streamlit:
```bash
~/.shortcuts/open_dashboard.sh
```

Ou manualmente:
```bash
streamlit run ~/projects/projeto_final/interface/streamlit_dashboard.py
```

### Linha de Comando

**Escanear e importar downloads:**
```bash
python ~/projects/projeto_final/core/action_router.py "scan_downloads"
```

**Analisar um projeto:**
```bash
python ~/projects/projeto_final/engineer/auto_engineer.py --analyze-project ~/projects/meu_projeto --auto-apply
```

**Criar um template:**
```bash
python ~/projects/projeto_final/core/template_generator.py telegram_bot ~/projects/meu_bot --name "MeuBot"
```

**Consultar o RAG:**
```bash
python ~/projects/projeto_final/core/rag_core.py --query "Como funciona o sistema de patches?"
```

### Configurar Preferências

```bash
python3 - <<PY
import sys
sys.path.insert(0,
'~/projects/projeto_final')
from core import memory_manager as mm

# Alterar nível de agressividade (low, medium, high)
mm.set_preference('aggressiveness', 'high')

# Ativar/desativar confirmação por voz
mm.set_preference('voice_confirmation', True)

# Idioma
mm.set_preference('language', 'pt-BR')

print('Preferências atualizadas!')
PY
```

## Auto-inicialização (Opcional)

Para que o J.A.R.V.I.S inicie automaticamente ao abrir o Termux:

```bash
echo "bash ~/projects/projeto_final/scripts/start_assistente.sh" >> ~/.bashrc
```

## Arquivos de Log e Memória

*   **`~/.jarvis_activity.log`** - Log de atividades humanamente legível
*   **`~/.jarvis_memory.json`** - Memória persistente (preferências, eventos, padrões)
*   **`~/.jarvis_backups/`** - Backups automáticos de arquivos modificados
*   **`~/projects/projeto_final/history/`** - Logs estruturados do sistema

## Requisitos

### Sistema
*   Termux (Android)
*   Acesso ao armazenamento (`termux-setup-storage`)
*   Conexão com internet (para instalação e alguns recursos)

### Dependências Principais
*   Python 3.x
*   Node.js (para projetos Node)
*   Git
*   FFmpeg (para processamento de áudio)
*   Termux API (para TTS e microfone)
*   `libsndfile` (para áudio)

### Módulos Python
*   `streamlit`, `flask` (interfaces)
*   `gTTS`, `pyttsx3`, `vosk` (voz)
*   `huggingface-hub` (IA)
*   `virtualenv` (ambientes)

## Observações Importantes

*   **Modelos de IA**: O `patch_generator` tenta usar a API Hugging Face se `HF_API_TOKEN` estiver configurado. Caso contrário, usa um gerador mock local.
*   **VOSK**: O script de instalação baixa automaticamente o modelo português pequeno (~40MB). Para reconhecimento offline, certifique-se de que o modelo está em `~/vosk-model-small-pt-0.3`.
*   **Termux TTS**: Para melhor experiência de voz, instale o aplicativo Termux:API da F-Droid e execute `pkg install termux-api`.
*   **Reconhecimento de Voz**: A captura de áudio no Termux pode ser sensível. Certifique-se de que o aplicativo Termux:API está instalado e que as permissões de microfone foram concedidas.
*   **Agressividade**: O padrão é `high` (auto-aplicação). Para mais controle, altere para `medium` ou `low`.

## Solução de Problemas

**Assistente não inicia:**
```bash
bash ~/projects/projeto_final/scripts/diagnostic.sh
```

**Voz não funciona:**
- Verifique se `termux-api` está instalado: `pkg install termux-api`
- Instale o app Termux:API da F-Droid
- Teste: `termux-tts-speak "teste"`

**Reconhecimento de voz não funciona:**
- Verifique se o modelo VOSK foi baixado: `ls ~/vosk-model-small-pt-0.3`
- Reinstale: `bash ~/projects/projeto_final/scripts/install_termux.sh`
- Verifique as permissões do microfone para o Termux:API.

**Erro ao importar módulos Python:**
```bash
cd ~/projects/projeto_final
pip install -r requirements.txt
```

## Contribuição e Suporte

Este é um projeto autoevolutivo. O J.A.R.V.I.S aprende com o uso e melhora continuamente. Verifique os logs em `~/.jarvis_activity.log` para acompanhar a evolução.

---

**Desenvolvido com ❤️ para Termux**

