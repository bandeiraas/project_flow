#!/usr/bin/env python3
# backend/run_tests.py
"""
Script para executar testes do backend com diferentes opções.

Usage:
    python run_tests.py                    # Executa todos os testes
    python run_tests.py --unit             # Apenas testes unitários
    python run_tests.py --integration      # Apenas testes de integração
    python run_tests.py --coverage         # Com relatório de cobertura
    python run_tests.py --verbose          # Modo verboso
    python run_tests.py --fast             # Execução rápida (sem testes lentos)
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path


def run_command(command, description=""):
    """Executa um comando e retorna o código de saída."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"Executando: {' '.join(command)}")
    print()
    
    result = subprocess.run(command, cwd=Path(__file__).parent)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Executa testes do backend")
    
    # Tipos de teste
    parser.add_argument('--unit', action='store_true', 
                       help='Executa apenas testes unitários')
    parser.add_argument('--integration', action='store_true', 
                       help='Executa apenas testes de integração')
    parser.add_argument('--auth', action='store_true', 
                       help='Executa apenas testes de autenticação')
    parser.add_argument('--api', action='store_true', 
                       help='Executa apenas testes de API')
    parser.add_argument('--security', action='store_true', 
                       help='Executa apenas testes de segurança')
    parser.add_argument('--database', action='store_true', 
                       help='Executa apenas testes de banco de dados')
    
    # Opções de execução
    parser.add_argument('--coverage', action='store_true', 
                       help='Gera relatório de cobertura')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Modo verboso')
    parser.add_argument('--fast', action='store_true', 
                       help='Execução rápida (pula testes lentos)')
    parser.add_argument('--parallel', action='store_true', 
                       help='Executa testes em paralelo')
    parser.add_argument('--html-report', action='store_true', 
                       help='Gera relatório HTML de cobertura')
    parser.add_argument('--xml-report', action='store_true', 
                       help='Gera relatório XML para CI/CD')
    
    # Opções de filtro
    parser.add_argument('--pattern', '-k', type=str, 
                       help='Executa apenas testes que correspondem ao padrão')
    parser.add_argument('--file', type=str, 
                       help='Executa apenas testes de um arquivo específico')
    
    # Opções de ambiente
    parser.add_argument('--env', type=str, default='testing',
                       help='Ambiente de teste (default: testing)')
    parser.add_argument('--db-url', type=str,
                       help='URL do banco de dados para testes')
    
    args = parser.parse_args()
    
    # Configura variáveis de ambiente
    os.environ['FLASK_ENV'] = args.env
    if args.db_url:
        os.environ['DATABASE_URL'] = args.db_url
    
    # Constrói o comando pytest
    command = ['python', '-m', 'pytest']
    
    # Adiciona marcadores baseados nos argumentos
    markers = []
    if args.unit:
        markers.append('unit')
    if args.integration:
        markers.append('integration')
    if args.auth:
        markers.append('auth')
    if args.api:
        markers.append('api')
    if args.security:
        markers.append('security')
    if args.database:
        markers.append('database')
    
    if markers:
        command.extend(['-m', ' or '.join(markers)])
    
    # Adiciona opções de execução
    if args.verbose:
        command.append('-v')
    else:
        command.append('-q')
    
    if args.fast:
        command.extend(['-m', 'not slow'])
    
    if args.parallel:
        command.extend(['-n', 'auto'])  # Requer pytest-xdist
    
    # Adiciona filtros
    if args.pattern:
        command.extend(['-k', args.pattern])
    
    if args.file:
        command.append(args.file)
    
    # Configurações de cobertura
    if args.coverage or args.html_report or args.xml_report:
        command.extend(['--cov=.', '--cov-report=term-missing'])
        
        if args.html_report:
            command.extend(['--cov-report=html:htmlcov'])
        
        if args.xml_report:
            command.extend(['--cov-report=xml'])
    
    # Configurações adicionais
    command.extend([
        '--tb=short',  # Traceback curto
        '--strict-markers',  # Marcadores rigorosos
        '--disable-warnings'  # Desabilita warnings
    ])
    
    # Executa os testes
    exit_code = run_command(command, "Executando Testes")
    
    # Relatórios pós-execução
    if args.html_report and exit_code == 0:
        html_path = Path(__file__).parent / 'htmlcov' / 'index.html'
        print(f"\n📊 Relatório de cobertura HTML disponível em: {html_path}")
        print(f"   Abra no navegador: file://{html_path.absolute()}")
    
    if args.xml_report and exit_code == 0:
        xml_path = Path(__file__).parent / 'coverage.xml'
        print(f"\n📄 Relatório de cobertura XML disponível em: {xml_path}")
    
    # Resumo final
    print(f"\n{'='*60}")
    if exit_code == 0:
        print("✅ TODOS OS TESTES PASSARAM!")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
    print(f"{'='*60}")
    
    return exit_code


def run_specific_scenarios():
    """Executa cenários específicos de teste."""
    scenarios = {
        'smoke': {
            'description': 'Testes de Smoke (básicos)',
            'command': ['python', '-m', 'pytest', '-m', 'unit', '--maxfail=5', '-q']
        },
        'regression': {
            'description': 'Testes de Regressão (completos)',
            'command': ['python', '-m', 'pytest', '--cov=.', '--cov-report=html']
        },
        'security': {
            'description': 'Testes de Segurança',
            'command': ['python', '-m', 'pytest', '-m', 'security', '-v']
        },
        'performance': {
            'description': 'Testes de Performance',
            'command': ['python', '-m', 'pytest', '-m', 'slow', '--durations=10']
        }
    }
    
    if len(sys.argv) > 1 and sys.argv[1] in scenarios:
        scenario = scenarios[sys.argv[1]]
        return run_command(scenario['command'], scenario['description'])
    
    return None


if __name__ == '__main__':
    # Verifica se é um cenário específico
    scenario_result = run_specific_scenarios()
    if scenario_result is not None:
        sys.exit(scenario_result)
    
    # Execução normal
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante a execução dos testes: {e}")
        sys.exit(1)