#!/data/data/com.termux/files/usr/bin/bash

# scripts/master_launcher.sh
# Lançador principal para projetos e dashboard.

PROJECT_DIR="$(dirname "$(dirname "$(readlink -f "$0")")")"

echo "[LAUNCHER] Selecione uma opção:"
echo "1. Abrir Dashboard"
echo "2. Listar e Abrir Projetos"
echo "3. Executar Auto-Engineer (ciclo único)"
echo "4. Consultar RAG"
echo "5. Sair"

read -p "Opção: " choice

case $choice in
    1)
        echo "[LAUNCHER] Abrindo Dashboard..."
        ~/.shortcuts/open_dashboard.sh
        ;;
    2)
        echo "[LAUNCHER] Listando projetos..."
        if [ -f "$PROJECT_DIR/data/index.json" ]; then
            python -c "
import json, os
index_file = os.path.join(os.environ.get("PROJECT_DIR"), "data", "index.json")
with open(index_file, "r", encoding="utf-8") as f:
    projects = json.load(f)

print("\nProjetos disponíveis:")
for i, p in enumerate(projects):
    print(f\"  {i+1}. {os.path.basename(p["path"])} ({p["type"]})\")

choice = input(\"Selecione um projeto para abrir (número): \")
try:
    idx = int(choice) - 1
    if 0 <= idx < len(projects):
        project_path = projects[idx]["path"]
        project_type = projects[idx]["type"]
        print(f\"Abrindo {project_path} (tipo: {project_type})...\")
        if project_type == \"python\":
            print(f\"cd {project_path} && venv/bin/python main.py (ou similar)\")
            os.system(f\"cd {project_path} && bash\") # Abre um shell no diretório
        elif project_type == \"node\":
            print(f\"cd {project_path} && npm start (ou similar)\")
            os.system(f\"cd {project_path} && bash\") # Abre um shell no diretório
        else:
            print(\"Tipo de projeto não suportado para abertura direta.\")
    else:
        print(\"Seleção inválida.\")
except ValueError:
    print(\"Entrada inválida.\")
            " PROJECT_DIR="$PROJECT_DIR"
        else:
            echo "[LAUNCHER] Nenhum projeto encontrado. Execute o scan primeiro."
        ;;
    3)
        read -p "Consulta para Auto-Engineer: " ae_query
        read -p "Arquivo alvo (ex: core/project_scan.py, opcional): " ae_file
        read -p "Aplicar automaticamente? (s/n): " ae_auto_apply_raw
        ae_auto_apply="false"
        if [[ "$ae_auto_apply_raw" == "s" || "$ae_auto_apply_raw" == "S" ]]; then
            ae_auto_apply="true"
        fi
        
        echo "[LAUNCHER] Executando Auto-Engineer..."
        python "$PROJECT_DIR/engineer/auto_engineer.py" --query "$ae_query" --file "$ae_file" --auto-apply "$ae_auto_apply"
        ;;
    4)
        read -p "Sua pergunta para o RAG: " rag_query
        echo "[LAUNCHER] Consultando RAG..."
        python "$PROJECT_DIR/core/rag_core.py" --query "$rag_query"
        ;;
    5)
        echo "[LAUNCHER] Saindo."
        ;;
    *)
        echo "[LAUNCHER] Opção inválida."
        ;;
esac

