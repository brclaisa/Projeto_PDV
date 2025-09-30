#!/usr/bin/env python3
"""
Script para executar o Projeto_PDV
"""

import uvicorn
import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Iniciando Projeto_PDV...")
    print("📱 Acesse: http://localhost:8005")
    print("📚 Documentação da API (Sistema_PDV): http://localhost:8005/docs")
    print("🛑 Para parar: Ctrl+C")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8005,
        reload=True,
        log_level="info"
    )
