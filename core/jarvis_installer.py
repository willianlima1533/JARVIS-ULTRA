'''
# core/jarvis_installer.py

Este módulo é responsável pela instalação inteligente e configuração do próprio J.A.R.V.I.S,
identificando o sistema operacional e gerenciando as dependências de sistema e Python.
'''

import os
import subprocess
import sys

class JarvisInstaller:
    def __init__(self, project_root_dir):
        self.project_root_dir = project_root_dir
        self.requirements_path = os.path.join(project_root_dir, 'requirements.txt')
        self.system_info = self._get_system_info()

    def _get_system_info(self):
        info = {
            'os': sys.platform,
            'is_termux': 'TERMUX_VERSION' in os.environ,
            'package_manager': None,
            'python_executable': sys.executable
        }

        if info['is_termux']:
            info['package_manager'] = 'pkg'
        elif sys.platform.startswith('linux'):
            if self._command_exists('apt'):
                info['package_manager'] = 'apt'
            elif self._command_exists('yum'):
                info['package_manager'] = 'yum'
            elif self._command_exists('dnf'):
                info['package_manager'] = 'dnf'
        elif sys.platform == 'darwin':
            if self._command_exists('brew'):
                info['package_manager'] = 'brew'
        elif sys.platform == 'win32':
            if self._command_exists('choco'):
                info['package_manager'] = 'choco'

        return info

    def _command_exists(self, cmd):
        return subprocess.call(f"type {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

    def _run_command(self, command, check=True, shell=False):
        print(f"\n$ {command if isinstance(command, str) else ' '.join(command)}")
        try:
            subprocess.run(command, check=check, shell=shell)
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao executar comando: {e}")
            raise
        except FileNotFoundError:
            print(f"❌ Comando não encontrado: {command[0] if isinstance(command, list) else command.split(' ')[0]}")
            raise

    def install_system_dependencies(self):
        print(f"\n[Installer] Instalando dependências do sistema para {self.system_info['os']}...")
        pm = self.system_info['package_manager']

        deps = {
            'pkg': ['python', 'nodejs', 'git', 'unzip', 'ffmpeg', 'libsndfile', 'termux-api', 'libjpeg-turbo', 'cmake'],
            'apt': ['python3', 'python3-pip', 'nodejs', 'npm', 'git', 'unzip', 'ffmpeg', 'libsndfile1', 'cmake', 'libsm6', 'libxext6', 'build-essential', 'libx11-dev', 'libgtk-3-dev', 'libboost-python-dev', 'pkg-config', 'libgl1-mesa-glx', 'python3-dev', 'libopenblas-dev'],
            'brew': ['python', 'node', 'git', 'ffmpeg', 'libsndfile', 'cmake'],
            'choco': ['python', 'nodejs', 'git', 'ffmpeg']
        }

        if pm and pm in deps:
            try:
                if pm == 'pkg':
                    self._run_command(['pkg', 'update', '-y'])
                    self._run_command(['pkg', 'install', '-y'] + deps[pm])
                elif pm == 'apt':
                    self._run_command(['sudo', 'apt-get', 'update', '-y'])
                    self._run_command(['sudo', 'apt-get', 'install', '-y'] + deps[pm])
                elif pm == 'brew':
                    self._run_command(['brew', 'update'])
                    self._run_command(['brew', 'install'] + deps[pm])
                elif pm == 'choco':
                    self._run_command(['choco', 'install'] + deps[pm] + ['--yes'])
                print("✅ Dependências do sistema instaladas.")
            except Exception as e:
                print(f"❌ Falha na instalação das dependências do sistema: {e}")
                sys.exit(1)
        else:
            print(f"⚠️ Gerenciador de pacotes não suportado ou não encontrado. Por favor, instale manualmente: {deps.get(pm, [])}")

    def install_python_dependencies(self):
        print("\n[Installer] Atualizando pip e instalando dependências Python...")
        try:
            pip_cmd = [self.system_info['python_executable'], '-m', 'pip']
            self._run_command(pip_cmd + ['install', '--upgrade', 'pip', 'setuptools', 'wheel', '--user'])
            print("✅ Pip atualizado.")

            if not os.path.exists(self.requirements_path):
                print(f"❌ requirements.txt não encontrado em {self.requirements_path}")
                return

            # Tentar instalar dlib separadamente primeiro, pois é uma dependência complexa
            print("Instalando dlib (dependência para reconhecimento facial)...")
            try:
                self._run_command(pip_cmd + ["install", "dlib"])
                print("✅ dlib instalado com sucesso.")
            except Exception as e:
                print(f"❌ Falha ao instalar dlib: {e}")
                print("➡️ Dica: Certifique-se de que todas as dependências de sistema (cmake, build-essential, etc.) estão instaladas.")
                # Não sair aqui, tentar instalar o resto das dependências

            print("Instalando outras dependências de requirements.txt...")
            self._run_command(pip_cmd + ["install", "-r", self.requirements_path])

            print("✅ Dependências Python instaladas.")
        except Exception as e:
            print(f"❌ Falha na instalação das dependências Python: {e}")
            print("➡️ Dica: Pode ser necessário instalar compiladores C++ ou bibliotecas de desenvolvimento Python (python3-dev).")
            sys.exit(1)

    def run_full_setup(self):
        print("\n============================================")
        print("🚀 Iniciando configuração completa do J.A.R.V.I.S 🚀")
        print("============================================")
        self.install_system_dependencies()
        self.install_python_dependencies()
        # A criação de diretórios e outras configurações podem ser adicionadas aqui
        os.makedirs(os.path.join(self.project_root_dir, 'data'), exist_ok=True)
        os.makedirs(os.path.join(self.project_root_dir, 'history'), exist_ok=True)
        os.makedirs(os.path.join(os.path.expanduser("~"), '.jarvis_backups'), exist_ok=True)
        print("✅ Estrutura de diretórios verificada.")
        print("\n============================================")
        print("🎉 Instalação do J.A.R.V.I.S CONCLUÍDA! 🎉")
        print("============================================")

if __name__ == '__main__':
    # Este script é chamado pelo install.sh principal
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..')) 
    installer = JarvisInstaller(project_root)
    installer.run_full_setup()

