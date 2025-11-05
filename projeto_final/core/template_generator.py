#!/usr/bin/env python3
# core/template_generator.py
"""
Gerador de templates de projetos.
Cria estruturas básicas para Telegram bots, Flask apps, React apps, etc.
"""
import os
import json
from typing import Dict, Optional

def create_telegram_bot_template(project_path: str, bot_name: str = "MyBot") -> bool:
    """
    Cria um template de bot do Telegram em Python.
    
    Args:
        project_path: Caminho onde criar o projeto
        bot_name: Nome do bot
        
    Returns:
        True se bem-sucedido
    """
    try:
        os.makedirs(project_path, exist_ok=True)
        
        # bot.py
        bot_code = f'''#!/usr/bin/env python3
# {bot_name} - Telegram Bot
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Token do bot (configure via variável de ambiente)
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    await update.message.reply_text(
        f"Olá! Eu sou o {bot_name}. Como posso ajudar?"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    help_text = """
Comandos disponíveis:
/start - Iniciar o bot
/help - Mostrar esta ajuda
"""
    await update.message.reply_text(help_text)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Eco de mensagens"""
    await update.message.reply_text(f"Você disse: {{update.message.text}}")

def main():
    """Função principal"""
    # Criar aplicação
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Adicionar handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Iniciar bot
    print(f"{{bot_name}} iniciado!")
    application.run_polling()

if __name__ == "__main__":
    main()
'''
        
        with open(os.path.join(project_path, "bot.py"), "w", encoding="utf-8") as f:
            f.write(bot_code)
        
        # requirements.txt
        requirements = """python-telegram-bot>=20.0
"""
        with open(os.path.join(project_path, "requirements.txt"), "w", encoding="utf-8") as f:
            f.write(requirements)
        
        # README.md
        readme = f"""# {bot_name}

Bot do Telegram criado com python-telegram-bot.

## Configuração

1. Crie um bot com o @BotFather no Telegram
2. Copie o token do bot
3. Configure a variável de ambiente:
   ```bash
   export TELEGRAM_BOT_TOKEN="seu_token_aqui"
   ```

## Instalação

```bash
pip install -r requirements.txt
```

## Execução

```bash
python bot.py
```
"""
        with open(os.path.join(project_path, "README.md"), "w", encoding="utf-8") as f:
            f.write(readme)
        
        print(f"[TEMPLATE] Telegram bot criado em: {project_path}")
        return True
        
    except Exception as e:
        print(f"[TEMPLATE] Erro ao criar Telegram bot: {e}")
        return False

def create_flask_app_template(project_path: str, app_name: str = "MyApp") -> bool:
    """
    Cria um template de aplicação Flask.
    
    Args:
        project_path: Caminho onde criar o projeto
        app_name: Nome da aplicação
        
    Returns:
        True se bem-sucedido
    """
    try:
        os.makedirs(project_path, exist_ok=True)
        os.makedirs(os.path.join(project_path, "templates"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "static"), exist_ok=True)
        
        # app.py
        app_code = f'''#!/usr/bin/env python3
# {app_name} - Flask Application
from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    """Página inicial"""
    return render_template('index.html', app_name="{app_name}")

@app.route('/api/status')
def status():
    """Endpoint de status"""
    return jsonify({{"status": "ok", "app": "{app_name}"}})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
'''
        
        with open(os.path.join(project_path, "app.py"), "w", encoding="utf-8") as f:
            f.write(app_code)
        
        # templates/index.html
        index_html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{{{ app_name }}}}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            text-align: center;
        }}
        h1 {{
            color: #333;
        }}
    </style>
</head>
<body>
    <h1>Bem-vindo ao {{{{ app_name }}}}!</h1>
    <p>Aplicação Flask funcionando corretamente.</p>
</body>
</html>
'''
        
        with open(os.path.join(project_path, "templates", "index.html"), "w", encoding="utf-8") as f:
            f.write(index_html)
        
        # requirements.txt
        requirements = """Flask>=2.3.0
"""
        with open(os.path.join(project_path, "requirements.txt"), "w", encoding="utf-8") as f:
            f.write(requirements)
        
        # README.md
        readme = f"""# {app_name}

Aplicação web criada com Flask.

## Instalação

```bash
pip install -r requirements.txt
```

## Execução

```bash
python app.py
```

Acesse: http://localhost:5000
"""
        with open(os.path.join(project_path, "README.md"), "w", encoding="utf-8") as f:
            f.write(readme)
        
        print(f"[TEMPLATE] Flask app criado em: {project_path}")
        return True
        
    except Exception as e:
        print(f"[TEMPLATE] Erro ao criar Flask app: {e}")
        return False

def create_react_app_template(project_path: str, app_name: str = "my-app") -> bool:
    """
    Cria um template mínimo de aplicação React (Vite).
    
    Args:
        project_path: Caminho onde criar o projeto
        app_name: Nome da aplicação
        
    Returns:
        True se bem-sucedido
    """
    try:
        os.makedirs(project_path, exist_ok=True)
        os.makedirs(os.path.join(project_path, "src"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "public"), exist_ok=True)
        
        # package.json
        package_json = {
            "name": app_name,
            "version": "0.1.0",
            "private": True,
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0"
            },
            "devDependencies": {
                "@vitejs/plugin-react": "^4.0.0",
                "vite": "^4.3.0"
            }
        }
        
        with open(os.path.join(project_path, "package.json"), "w", encoding="utf-8") as f:
            json.dump(package_json, f, indent=2)
        
        # vite.config.js
        vite_config = '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
'''
        with open(os.path.join(project_path, "vite.config.js"), "w", encoding="utf-8") as f:
            f.write(vite_config)
        
        # index.html
        index_html = f'''<!DOCTYPE html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{app_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
'''
        with open(os.path.join(project_path, "index.html"), "w", encoding="utf-8") as f:
            f.write(index_html)
        
        # src/main.jsx
        main_jsx = '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
'''
        with open(os.path.join(project_path, "src", "main.jsx"), "w", encoding="utf-8") as f:
            f.write(main_jsx)
        
        # src/App.jsx
        app_jsx = f'''import {{ useState }} from 'react'
import './App.css'

function App() {{
  const [count, setCount] = useState(0)

  return (
    <div className="App">
      <h1>{app_name}</h1>
      <div className="card">
        <button onClick={{() => setCount((count) => count + 1)}}>
          Contador: {{count}}
        </button>
      </div>
    </div>
  )
}}

export default App
'''
        with open(os.path.join(project_path, "src", "App.jsx"), "w", encoding="utf-8") as f:
            f.write(app_jsx)
        
        # src/App.css
        app_css = '''.App {
  text-align: center;
  padding: 2rem;
}

.card {
  padding: 2em;
}

button {
  font-size: 1.2em;
  padding: 0.6em 1.2em;
  cursor: pointer;
}
'''
        with open(os.path.join(project_path, "src", "App.css"), "w", encoding="utf-8") as f:
            f.write(app_css)
        
        # src/index.css
        index_css = '''body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}
'''
        with open(os.path.join(project_path, "src", "index.css"), "w", encoding="utf-8") as f:
            f.write(index_css)
        
        # README.md
        readme = f"""# {app_name}

Aplicação React criada com Vite.

## Instalação

```bash
npm install
```

## Desenvolvimento

```bash
npm run dev
```

## Build

```bash
npm run build
```
"""
        with open(os.path.join(project_path, "README.md"), "w", encoding="utf-8") as f:
            f.write(readme)
        
        print(f"[TEMPLATE] React app criado em: {project_path}")
        return True
        
    except Exception as e:
        print(f"[TEMPLATE] Erro ao criar React app: {e}")
        return False

def create_template(template_type: str, project_path: str, **kwargs) -> bool:
    """
    Cria um template de projeto.
    
    Args:
        template_type: Tipo de template (telegram_bot, flask_app, react_app)
        project_path: Caminho onde criar o projeto
        **kwargs: Argumentos adicionais específicos do template
        
    Returns:
        True se bem-sucedido
    """
    if template_type == "telegram_bot":
        return create_telegram_bot_template(project_path, kwargs.get("bot_name", "MyBot"))
    
    elif template_type == "flask_app":
        return create_flask_app_template(project_path, kwargs.get("app_name", "MyApp"))
    
    elif template_type == "react_app":
        return create_react_app_template(project_path, kwargs.get("app_name", "my-app"))
    
    else:
        print(f"[TEMPLATE] Tipo de template desconhecido: {template_type}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Gerador de Templates")
    parser.add_argument("type", choices=["telegram_bot", "flask_app", "react_app"],
                        help="Tipo de template")
    parser.add_argument("path", help="Caminho onde criar o projeto")
    parser.add_argument("--name", help="Nome do projeto/bot/app")
    args = parser.parse_args()
    
    kwargs = {}
    if args.name:
        if args.type == "telegram_bot":
            kwargs["bot_name"] = args.name
        else:
            kwargs["app_name"] = args.name
    
    success = create_template(args.type, args.path, **kwargs)
    
    if success:
        print(f"\n✅ Template {args.type} criado com sucesso em: {args.path}")
    else:
        print(f"\n❌ Falha ao criar template {args.type}")

