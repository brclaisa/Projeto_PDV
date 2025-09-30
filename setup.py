#!/usr/bin/env python3
"""
Script de configuração inicial do Projeto_PDV
"""

import subprocess
import sys
import os

def install_requirements():
    """Instalar dependências do projeto"""
    print("📦 Instalando dependências...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def initialize_database():
    """Inicializar banco de dados com dados de exemplo"""
    print("🗄️ Inicializando banco de dados...")
    try:
        from backend.init_data import main as init_main
        init_main()
        return True
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        return False

def main():
    """Função principal de configuração"""
    print("🧩 Configuração do Projeto_PDV")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("requirements.txt"):
        print("❌ Execute este script no diretório raiz do projeto")
        sys.exit(1)
    
    # Instalar dependências
    if not install_requirements():
        print("❌ Falha na instalação das dependências")
        sys.exit(1)
    
    # Inicializar banco de dados
    if not initialize_database():
        print("❌ Falha na inicialização do banco de dados")
        sys.exit(1)
    
    print("\n🎉 Configuração concluída com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Execute: python run.py")
    print("2. Acesse: http://localhost:8000")
    print("3. Documentação da API: http://localhost:8000/docs")
    print("\n🧾 Projeto_PDV está pronto para uso!")

if __name__ == "__main__":
    main()
