#!/usr/bin/env python3
# interface/streamlit_dashboard.py
"""
Dashboard Streamlit para o Projeto Final.
Interface web para visualização e controle do sistema.
"""
import streamlit as st
import json
import os
import sys
from pathlib import Path

# Adicionar o diretório pai ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import scan_projects, setup_project, query_rag, add_document
from engineer import get_summary, analyze_project, run_cycle_with_patch

# Configuração da página
st.set_page_config(
    page_title="Projeto Final - Dashboard",
    page_icon="🚀",
    layout="wide"
)

# Caminhos
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
HISTORY_DIR = os.path.join(BASE_DIR, "history")
INDEX_FILE = os.path.join(DATA_DIR, "index.json")
METRICS_FILE = os.path.join(DATA_DIR, "metrics.json")
DOCS_FILE = os.path.join(DATA_DIR, "docs_store.json")

# Título principal
st.title("🚀 Projeto Final - Dashboard Inteligente")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configurações")
    
    # Diretórios para scan
    st.subheader("Diretórios de Scan")
    default_dirs = [
        os.path.expanduser("~/storage/downloads"),
        os.path.expanduser("~/projects")
    ]
    scan_dirs_text = st.text_area(
        "Diretórios (um por linha)",
        value="\n".join(default_dirs),
        height=100
    )
    scan_dirs = [d.strip() for d in scan_dirs_text.split("\n") if d.strip()]
    
    st.markdown("---")
    
    # Ações rápidas
    st.subheader("🔧 Ações Rápidas")
    
    if st.button("🔍 Escanear Projetos", use_container_width=True):
        with st.spinner("Escaneando projetos..."):
            projects = scan_projects(scan_dirs, DATA_DIR)
            st.success(f"✅ {len(projects)} projetos encontrados!")
            st.rerun()
    
    if st.button("📦 Configurar Ambientes", use_container_width=True):
        if os.path.exists(INDEX_FILE):
            with st.spinner("Configurando ambientes..."):
                with open(INDEX_FILE, "r", encoding="utf-8") as f:
                    projects = json.load(f)
                
                for project in projects:
                    success, msg = setup_project(project)
                    if success:
                        st.success(f"✅ {project['path']}")
                    else:
                        st.error(f"❌ {project['path']}: {msg}")
        else:
            st.warning("⚠️ Execute o scan primeiro!")

# Tabs principais
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Visão Geral",
    "📁 Projetos",
    "🤖 Auto-Engineer",
    "📚 RAG System",
    "📈 Métricas"
])

# Tab 1: Visão Geral
with tab1:
    st.header("📊 Visão Geral do Sistema")
    
    col1, col2, col3 = st.columns(3)
    
    # Estatísticas de projetos
    with col1:
        st.metric("Projetos Detectados", 
                  len(json.load(open(INDEX_FILE)) if os.path.exists(INDEX_FILE) else []))
    
    # Estatísticas de métricas
    with col2:
        if os.path.exists(METRICS_FILE):
            summary = get_summary()
            st.metric("Execuções Totais", summary["system"]["total_runs"])
        else:
            st.metric("Execuções Totais", 0)
    
    # Estatísticas de documentos
    with col3:
        if os.path.exists(DOCS_FILE):
            docs = json.load(open(DOCS_FILE, "r", encoding="utf-8"))
            st.metric("Documentos RAG", len(docs))
        else:
            st.metric("Documentos RAG", 0)
    
    st.markdown("---")
    
    # Status do sistema
    st.subheader("🔧 Status do Sistema")
    
    status_col1, status_col2 = st.columns(2)
    
    with status_col1:
        st.info("**Módulos Ativos:**\n- Core\n- Engineer\n- RAG\n- Dashboard")
    
    with status_col2:
        if os.path.exists(METRICS_FILE):
            summary = get_summary()
            success_rate = summary["system"].get("success_rate", 0) * 100
            st.success(f"**Taxa de Sucesso:** {success_rate:.1f}%")
        else:
            st.warning("**Taxa de Sucesso:** N/A")

# Tab 2: Projetos
with tab2:
    st.header("📁 Projetos Gerenciados")
    
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            projects = json.load(f)
        
        if projects:
            for i, project in enumerate(projects):
                with st.expander(f"{'🐍' if project['type'] == 'python' else '📦'} {os.path.basename(project['path'])}"):
                    st.write(f"**Caminho:** `{project['path']}`")
                    st.write(f"**Tipo:** {project['type'].upper()}")
                    st.write(f"**Fonte:** {project.get('source', 'unknown')}")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("⚙️ Configurar", key=f"setup_{i}"):
                            with st.spinner("Configurando..."):
                                success, msg = setup_project(project)
                                if success:
                                    st.success(msg)
                                else:
                                    st.error(msg)
                    
                    with col2:
                        if st.button("🔍 Analisar", key=f"analyze_{i}"):
                            with st.spinner("Analisando..."):
                                analysis = analyze_project(project['path'])
                                st.json(analysis)
                    
                    with col3:
                        if st.button("📂 Abrir", key=f"open_{i}"):
                            st.code(f"cd {project['path']}", language="bash")
        else:
            st.info("Nenhum projeto encontrado. Use o botão 'Escanear Projetos' na barra lateral.")
    else:
        st.warning("⚠️ Nenhum índice de projetos encontrado. Execute o scan primeiro!")

# Tab 3: Auto-Engineer
with tab3:
    st.header("🤖 Auto-Engineer")
    
    st.markdown("""
    O Auto-Engineer analisa código, gera patches e aplica melhorias automaticamente.
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        query = st.text_input("Consulta/Objetivo", value="melhorar qualidade do código")
    
    with col2:
        auto_apply = st.checkbox("Aplicar automaticamente", value=False)
    
    target_file = st.text_input("Arquivo alvo (relativo ao projeto)", 
                                placeholder="ex: core/project_scan.py")
    
    if st.button("▶️ Executar Ciclo", use_container_width=True):
        if target_file:
            with st.spinner("Executando ciclo de auto-engenharia..."):
                result = run_cycle_with_patch(
                    query=query,
                    target_file=target_file,
                    auto_apply=auto_apply
                )
                
                st.success("✅ Ciclo concluído!")
                
                # Mostrar resultados
                st.subheader("Resultados")
                
                result_col1, result_col2 = st.columns(2)
                
                with result_col1:
                    st.metric("Status", "Sucesso" if result["success"] else "Falha")
                    st.metric("Duração", f"{result['duration']:.2f}s")
                
                with result_col2:
                    if result.get("patch"):
                        st.metric("Confiança do Patch", 
                                 f"{result['patch'].get('confidence', 0):.2f}")
                        st.metric("Patch Aplicado", 
                                 "Sim" if result.get("patch_applied") else "Não")
                
                # Detalhes
                with st.expander("📋 Detalhes Completos"):
                    st.json(result)
        else:
            st.warning("⚠️ Especifique um arquivo alvo!")
    
    st.markdown("---")
    
    # Logs recentes
    st.subheader("📜 Logs Recentes")
    log_file = os.path.join(HISTORY_DIR, "auto_engineer.log")
    
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()[-20:]
        
        log_text = "".join(lines)
        st.code(log_text, language="json")
    else:
        st.info("Nenhum log disponível ainda.")

# Tab 4: RAG System
with tab4:
    st.header("📚 Sistema RAG")
    
    st.markdown("""
    Sistema de Recuperação e Geração Aumentada para consultas inteligentes.
    """)
    
    # Consulta
    st.subheader("🔍 Consultar")
    
    rag_query = st.text_input("Sua pergunta", placeholder="ex: Como funciona o sistema de patches?")
    
    if st.button("🔍 Consultar RAG", use_container_width=True):
        if rag_query:
            with st.spinner("Processando consulta..."):
                answer = query_rag(rag_query, top_k=3)
                st.markdown(answer)
        else:
            st.warning("⚠️ Digite uma pergunta!")
    
    st.markdown("---")
    
    # Adicionar documento
    st.subheader("➕ Adicionar Documento")
    
    with st.form("add_doc_form"):
        doc_title = st.text_input("Título")
        doc_text = st.text_area("Conteúdo", height=150)
        doc_source = st.text_input("Fonte", value="manual")
        
        if st.form_submit_button("Adicionar Documento"):
            if doc_title and doc_text:
                add_document(doc_title, doc_text, doc_source)
                st.success(f"✅ Documento '{doc_title}' adicionado!")
            else:
                st.warning("⚠️ Preencha título e conteúdo!")
    
    st.markdown("---")
    
    # Documentos existentes
    st.subheader("📚 Documentos Existentes")
    
    if os.path.exists(DOCS_FILE):
        with open(DOCS_FILE, "r", encoding="utf-8") as f:
            docs = json.load(f)
        
        if docs:
            for doc in docs:
                with st.expander(f"📄 {doc.get('title', 'Sem título')}"):
                    st.write(f"**ID:** {doc.get('id')}")
                    st.write(f"**Fonte:** {doc.get('source')}")
                    st.write(f"**Conteúdo:**")
                    st.text(doc.get('text', '')[:500] + ("..." if len(doc.get('text', '')) > 500 else ""))
        else:
            st.info("Nenhum documento no sistema. Adicione documentos acima.")
    else:
        st.warning("⚠️ Arquivo de documentos não encontrado.")

# Tab 5: Métricas
with tab5:
    st.header("📈 Métricas e Estatísticas")
    
    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, "r", encoding="utf-8") as f:
            metrics = json.load(f)
        
        # Resumo do sistema
        st.subheader("🎯 Resumo do Sistema")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Execuções", metrics["system"]["total_runs"])
        
        with col2:
            st.metric("Total de Patches", metrics["system"]["total_patches"])
        
        with col3:
            success_rate = metrics["system"].get("success_rate", 0) * 100
            st.metric("Taxa de Sucesso", f"{success_rate:.1f}%")
        
        with col4:
            st.metric("Projetos Monitorados", len(metrics.get("projects", {})))
        
        st.markdown("---")
        
        # Execuções recentes
        st.subheader("🔄 Execuções Recentes")
        
        runs = metrics.get("runs", [])[-10:][::-1]
        
        if runs:
            for i, run in enumerate(runs):
                status_emoji = "✅" if run.get("success") else "❌"
                timestamp = run.get("timestamp", "N/A")
                
                with st.expander(f"{status_emoji} Execução {len(runs)-i} - {timestamp}"):
                    st.json(run)
        else:
            st.info("Nenhuma execução registrada ainda.")
        
        st.markdown("---")
        
        # Patches aplicados
        st.subheader("🔧 Patches Aplicados")
        
        patches = metrics.get("patches", [])[-10:][::-1]
        
        if patches:
            for i, patch in enumerate(patches):
                timestamp = patch.get("timestamp", "N/A")
                file_name = patch.get("file", "N/A")
                
                with st.expander(f"🔧 Patch {len(patches)-i} - {file_name} - {timestamp}"):
                    st.json(patch)
        else:
            st.info("Nenhum patch aplicado ainda.")
    else:
        st.warning("⚠️ Nenhuma métrica disponível. Execute o auto-engineer para gerar métricas.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Projeto Final - Sistema Inteligente de Gerenciamento de Projetos</p>
    <p>Desenvolvido com ❤️ usando Streamlit</p>
</div>
""", unsafe_allow_html=True)

