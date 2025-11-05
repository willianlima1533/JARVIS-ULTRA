# core/env_manager_v2.py

import os
import subprocess
import sys
import json

class EnvironmentManager:
    def __init__(self, project_root_dir):
        self.project_root_dir = project_root_dir
        self.requirements_path = os.path.join(project_root_dir, 'requirements.txt')
        self.config_path = os.path.join(project_root_dir, 'config.json') # Para configurações futuras
        self.system_info = self._get_system_info()

    def _get_system_info(self):
        info = {
            'os': sys.platform,
            'is_termux': 'TERMUX_VERSION' in os.environ,
            'package_manager': None,
            'python_version': sys.version.split(' ')[0]
        }

        if info['is_termux']:
            info['package_manager'] = 'pkg'
        elif sys.platform.startswith('linux'):
            if os.path.exists('/etc/debian_version'):
                info['package_manager'] = 'apt'
            elif os.path.exists('/etc/redhat-release'):
                info['package_manager'] = 'yum' # ou dnf
            # Adicionar outros gerênciadores de pacote para Linux
        elif sys.platform == 'darwin':
            info['package_manager'] = 'brew'
        elif sys.platform == 'win32':
            info['package_manager'] = 'choco' # Chocolatey para Windows

        return info

    def _run_command(self, command, check=True, shell=False, capture_output=False):
        print(f"Executando comando: {' '.join(command) if isinstance(command, list) else command}")
        try:
            result = subprocess.run(command, check=check, shell=shell, capture_output=capture_output, text=True)
            if capture_output:
                print(result.stdout)
                if result.stderr:
                    print(f"Stderr: {result.stderr}")
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao executar comando: {e}")
            if capture_output:
                print(f"Stderr: {e.stderr}")
            raise
        except FileNotFoundError:
            print(f"❌ Comando não encontrado: {command[0] if isinstance(command, list) else command.split(' ')[0]}")
            raise

    def install_system_dependencies(self):
        print(f"\n[EnvironmentManager] Instalando dependências do sistema para {self.system_info['os']}...")
        pm = self.system_info['package_manager']

        common_deps = []
        if self.system_info['is_termux']:
            common_deps = ['python', 'nodejs', 'git', 'unzip', 'ffmpeg', 'libsndfile', 'termux-api']
        elif pm == 'apt':
            common_deps = ['python3', 'python3-pip', 'nodejs', 'git', 'unzip', 'ffmpeg', 'libsndfile1']
        elif pm == 'brew':
            common_deps = ['python', 'nodejs', 'git', 'unzip', 'ffmpeg', 'libsndfile']
        # Adicionar mais sistemas operacionais e seus gerenciadores de pacotes

        if pm:
            try:
                if pm == 'pkg':
                    self._run_command(['pkg', 'update', '-y'])
                    self._run_command(['pkg', 'upgrade', '-y'])
                    self._run_command(['pkg', 'install', '-y'] + common_deps)
                elif pm == 'apt':
                    self._run_command(['sudo', 'apt-get', 'update', '-y'])
                    self._run_command(['sudo', 'apt-get', 'upgrade', '-y'])
                    self._run_command(['sudo', 'apt-get', 'install', '-y'] + common_deps)
                elif pm == 'brew':
                    # Certificar-se de que o brew está instalado
                    try:
                        self._run_command(['brew', '--version'], capture_output=True)
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        print("Homebrew não encontrado. Instalando Homebrew...")
                        self._run_command(['/bin/bash', '-c', '"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'], shell=True)
                        # Adicionar ao PATH se necessário
                        self._run_command(['echo', 'eval "$(/opt/homebrew/bin/brew shellenv)"', '>>', os.path.expanduser('~/.zprofile')], shell=True)
                        self._run_command(['eval', '"$(/opt/homebrew/bin/brew shellenv)"'], shell=True)
                    self._run_command(['brew', 'update'])
                    self._run_command(['brew', 'install'] + common_deps)
                else:
                    print(f"⚠️ Gerenciador de pacotes '{pm}' não suportado para instalação automática de dependências de sistema.")
                    print("Por favor, instale as seguintes dependências manualmente: " + ", ".join(common_deps))
                print("✅ Dependências do sistema instaladas.")
            except Exception as e:
                print(f"❌ Falha na instalação das dependências do sistema: {e}")
                sys.exit(1)
        else:
            print("⚠️ Não foi possível determinar o gerenciador de pacotes do sistema. Instale as dependências manualmente.")
            print("Dependências sugeridas: " + ", ".join(common_deps))

    def install_python_dependencies(self):
        print("\n[EnvironmentManager] Atualizando pip e instalando dependências Python...")
        try:
            self._run_command([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel'])
            print("✅ Pip atualizado.")

            if not os.path.exists(self.requirements_path):
                print(f"❌ requirements.txt não encontrado em {self.requirements_path}")
                return

            # Tentar instalar faiss-cpu, com fallback para annoy
            faiss_installed = False
            if self.system_info['os'].startswith('linux'): # faiss-cpu geralmente tem problemas no Termux, mas funciona em Linux
                print("Tentando instalar faiss-cpu...")
                try:
                    self._run_command([sys.executable, '-m', 'pip', 'install', 'faiss-cpu'])
                    print("✅ faiss-cpu instalado com sucesso.")
                    faiss_installed = True
                except Exception:
                    print("⚠️ Falha ao instalar faiss-cpu. Usando Annoy como fallback.")

            # Instalar outras dependências e Annoy se faiss-cpu não foi instalado
            if not faiss_installed:
                print("Instalando dependências restantes e Annoy...")
                self._run_command([sys.executable, '-m', 'pip', 'install', '-r', self.requirements_path, 'annoy'])
            else:
                print("Instalando dependências restantes...")
                self._run_command([sys.executable, '-m', 'pip', 'install', '-r', self.requirements_path])

            print("✅ Dependências Python instaladas.")
        except Exception as e:
            print(f"❌ Falha na instalação das dependências Python: {e}")
            sys.exit(1)

    def setup_environment(self):
        print("\n[EnvironmentManager] Configurando ambiente...")
        # Exemplo: criar diretórios necessários
        os.makedirs(os.path.join(self.project_root_dir, 'data'), exist_ok=True)
        os.makedirs(os.path.join(self.project_root_dir, 'history'), exist_ok=True)
        print("✅ Diretórios de dados e histórico criados.")

    def run_full_setup(self):
        print("\n==========================================")
        print("🚀 Iniciando configuração completa do J.A.R.V.I.S 🚀")
        print("==========================================")
        self.install_system_dependencies()
        self.install_python_dependencies()
        self.setup_environment()
        print("\n==========================================")
        print("🎉 Configuração do J.A.R.V.I.S CONCLUÍDA! 🎉")
        print("==========================================")

if __name__ == '__main__':
    # Este script será chamado pelo install.sh principal
    # Para teste direto:
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # project_root = os.path.abspath(os.path.join(current_dir, '..')) # Assumindo que core está em project_root/core
    # manager = EnvironmentManager(project_root)
    # manager.run_full_setup()
    pass

