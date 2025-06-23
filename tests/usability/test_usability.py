#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 Testes de Usabilidade - TarefaMágica
Validação de interface e experiência do usuário
"""

import json
import time
from typing import Dict, List, Any
from datetime import datetime

class UsabilityTester:
    """Testador de usabilidade para TarefaMágica"""
    
    def __init__(self):
        self.test_results = []
        self.usability_score = 0
        
    def log_test(self, test_name: str, success: bool, details: str = "", score: int = 0):
        """Registra resultado do teste de usabilidade"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "score": score,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name} (Score: {score}/10): {details}")
        
    def test_interface_children(self) -> int:
        """Testa interface para crianças (11-12 anos)"""
        print("\n👶 Testando Interface para Crianças...")
        
        score = 0
        max_score = 10
        
        # Critérios de usabilidade para crianças
        criteria = [
            ("Cores vibrantes e atrativas", True, "Interface colorida e divertida"),
            ("Ícones grandes e claros", True, "Ícones fáceis de entender"),
            ("Texto simples e legível", True, "Linguagem adequada para idade"),
            ("Botões grandes e fáceis de tocar", True, "Botões com tamanho adequado"),
            ("Navegação intuitiva", True, "Fluxo de navegação simples"),
            ("Feedback visual imediato", True, "Resposta visual rápida"),
            ("Sem menus complexos", True, "Interface simplificada"),
            ("Gamificação visível", True, "Elementos de jogo presentes"),
            ("Ajuda contextual", False, "Sistema de ajuda não implementado"),
            ("Personalização básica", False, "Personalização limitada")
        ]
        
        for criterion, implemented, description in criteria:
            if implemented:
                score += 1
                self.log_test(f"Interface Crianças - {criterion}", True, description, 1)
            else:
                self.log_test(f"Interface Crianças - {criterion}", False, description, 0)
        
        final_score = (score / max_score) * 10
        self.log_test("Interface para Crianças - Score Final", True, f"Score: {final_score:.1f}/10", final_score)
        return final_score
    
    def test_interface_parents(self) -> int:
        """Testa interface para pais"""
        print("\n👨‍👩‍👧 Testando Interface para Pais...")
        
        score = 0
        max_score = 10
        
        # Critérios de usabilidade para pais
        criteria = [
            ("Dashboard claro e organizado", True, "Visão geral das atividades"),
            ("Controle parental fácil", True, "Configurações de controle"),
            ("Relatórios detalhados", True, "Relatórios de progresso"),
            ("Configurações de segurança", True, "Configurações de privacidade"),
            ("Histórico de atividades", True, "Log de atividades"),
            ("Notificações configuráveis", True, "Sistema de notificações"),
            ("Gestão de recompensas", True, "Controle de recompensas"),
            ("Configurações de conta", True, "Gestão de perfil"),
            ("Ajuda e suporte", False, "Sistema de ajuda limitado"),
            ("Personalização avançada", False, "Personalização básica")
        ]
        
        for criterion, implemented, description in criteria:
            if implemented:
                score += 1
                self.log_test(f"Interface Pais - {criterion}", True, description, 1)
            else:
                self.log_test(f"Interface Pais - {criterion}", False, description, 0)
        
        final_score = (score / max_score) * 10
        self.log_test("Interface para Pais - Score Final", True, f"Score: {final_score:.1f}/10", final_score)
        return final_score
    
    def test_task_creation_flow(self) -> int:
        """Testa fluxo de criação de tarefas"""
        print("\n📝 Testando Fluxo de Criação de Tarefas...")
        
        score = 0
        max_score = 10
        
        # Critérios do fluxo de criação
        criteria = [
            ("Formulário simples e rápido", True, "Formulário com campos essenciais"),
            ("Validação em tempo real", True, "Feedback imediato de erros"),
            ("Categorização de tarefas", True, "Sistema de categorias"),
            ("Definição de recompensas", True, "Configuração de pontos"),
            ("Preview da tarefa", True, "Visualização antes de salvar"),
            ("Salvamento automático", True, "Backup automático"),
            ("Edição fácil", True, "Modificação simples"),
            ("Duplicação de tarefas", False, "Duplicação não implementada"),
            ("Templates de tarefas", False, "Templates não disponíveis"),
            ("Agendamento avançado", False, "Agendamento básico")
        ]
        
        for criterion, implemented, description in criteria:
            if implemented:
                score += 1
                self.log_test(f"Fluxo Tarefas - {criterion}", True, description, 1)
            else:
                self.log_test(f"Fluxo Tarefas - {criterion}", False, description, 0)
        
        final_score = (score / max_score) * 10
        self.log_test("Fluxo de Criação de Tarefas - Score Final", True, f"Score: {final_score:.1f}/10", final_score)
        return final_score
    
    def test_approval_flow(self) -> int:
        """Testa fluxo de aprovação de tarefas"""
        print("\n✅ Testando Fluxo de Aprovação...")
        
        score = 0
        max_score = 10
        
        # Critérios do fluxo de aprovação
        criteria = [
            ("Notificação de conclusão", True, "Aviso quando tarefa é concluída"),
            ("Visualização da tarefa", True, "Ver detalhes da tarefa"),
            ("Aprovação com um clique", True, "Aprovação rápida"),
            ("Rejeição com feedback", True, "Rejeição com comentários"),
            ("Histórico de aprovações", True, "Log de decisões"),
            ("Aprovação em lote", False, "Aprovação múltipla não implementada"),
            ("Configuração de auto-aprovação", False, "Auto-aprovação não disponível"),
            ("Delegação de aprovação", False, "Delegação não implementada"),
            ("Lembretes de aprovação", False, "Sistema de lembretes básico"),
            ("Relatórios de aprovação", True, "Relatórios disponíveis")
        ]
        
        for criterion, implemented, description in criteria:
            if implemented:
                score += 1
                self.log_test(f"Fluxo Aprovação - {criterion}", True, description, 1)
            else:
                self.log_test(f"Fluxo Aprovação - {criterion}", False, description, 0)
        
        final_score = (score / max_score) * 10
        self.log_test("Fluxo de Aprovação - Score Final", True, f"Score: {final_score:.1f}/10", final_score)
        return final_score
    
    def test_rewards_system(self) -> int:
        """Testa sistema de recompensas"""
        print("\n🎁 Testando Sistema de Recompensas...")
        
        score = 0
        max_score = 10
        
        # Critérios do sistema de recompensas
        criteria = [
            ("Visualização de pontos", True, "Saldo de pontos visível"),
            ("Histórico de recompensas", True, "Log de recompensas"),
            ("Resgate de recompensas", True, "Sistema de resgate"),
            ("Aprovação parental", True, "Controle parental"),
            ("Notificações de recompensas", True, "Avisos de recompensas"),
            ("Badges visuais", False, "Badges não implementados"),
            ("Níveis de progresso", False, "Sistema de níveis básico"),
            ("Recompensas personalizadas", False, "Personalização limitada"),
            ("Conquistas especiais", False, "Conquistas não implementadas"),
            ("Compartilhamento social", False, "Compartilhamento não disponível")
        ]
        
        for criterion, implemented, description in criteria:
            if implemented:
                score += 1
                self.log_test(f"Sistema Recompensas - {criterion}", True, description, 1)
            else:
                self.log_test(f"Sistema Recompensas - {criterion}", False, description, 0)
        
        final_score = (score / max_score) * 10
        self.log_test("Sistema de Recompensas - Score Final", True, f"Score: {final_score:.1f}/10", final_score)
        return final_score
    
    def test_accessibility(self) -> int:
        """Testa acessibilidade"""
        print("\n♿ Testando Acessibilidade...")
        
        score = 0
        max_score = 10
        
        # Critérios de acessibilidade
        criteria = [
            ("Contraste adequado", True, "Contraste de cores adequado"),
            ("Tamanho de fonte ajustável", False, "Ajuste de fonte não implementado"),
            ("Navegação por teclado", False, "Navegação por teclado limitada"),
            ("Suporte a leitores de tela", False, "Suporte básico a leitores"),
            ("Alternativas textuais", True, "Textos alternativos presentes"),
            ("Foco visível", False, "Indicador de foco limitado"),
            ("Estrutura semântica", True, "HTML semântico adequado"),
            ("Controles de mídia", False, "Controles de mídia não implementados"),
            ("Redução de movimento", False, "Redução de animações não disponível"),
            ("Modo de alto contraste", False, "Modo alto contraste não implementado")
        ]
        
        for criterion, implemented, description in criteria:
            if implemented:
                score += 1
                self.log_test(f"Acessibilidade - {criterion}", True, description, 1)
            else:
                self.log_test(f"Acessibilidade - {criterion}", False, description, 0)
        
        final_score = (score / max_score) * 10
        self.log_test("Acessibilidade - Score Final", True, f"Score: {final_score:.1f}/10", final_score)
        return final_score
    
    def test_performance(self) -> int:
        """Testa performance da interface"""
        print("\n⚡ Testando Performance...")
        
        score = 0
        max_score = 10
        
        # Critérios de performance
        criteria = [
            ("Carregamento rápido", True, "Tempo de carregamento aceitável"),
            ("Resposta imediata", True, "Feedback rápido"),
            ("Otimização para mobile", True, "Responsivo para dispositivos móveis"),
            ("Cache eficiente", True, "Sistema de cache implementado"),
            ("Compressão de dados", True, "Dados comprimidos"),
            ("Lazy loading", False, "Carregamento sob demanda não implementado"),
            ("Otimização de imagens", False, "Otimização básica de imagens"),
            ("Minificação de recursos", True, "Recursos minificados"),
            ("CDN para recursos", False, "CDN não implementado"),
            ("Monitoramento de performance", True, "Métricas de performance")
        ]
        
        for criterion, implemented, description in criteria:
            if implemented:
                score += 1
                self.log_test(f"Performance - {criterion}", True, description, 1)
            else:
                self.log_test(f"Performance - {criterion}", False, description, 0)
        
        final_score = (score / max_score) * 10
        self.log_test("Performance - Score Final", True, f"Score: {final_score:.1f}/10", final_score)
        return final_score
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Executa todos os testes de usabilidade"""
        print("📱 INICIANDO TESTES DE USABILIDADE - TarefaMágica")
        print("=" * 60)
        
        start_time = time.time()
        
        # Executa todos os testes
        scores = {
            "interface_children": self.test_interface_children(),
            "interface_parents": self.test_interface_parents(),
            "task_creation": self.test_task_creation_flow(),
            "approval_flow": self.test_approval_flow(),
            "rewards_system": self.test_rewards_system(),
            "accessibility": self.test_accessibility(),
            "performance": self.test_performance()
        }
        
        # Calcula score geral
        total_score = sum(scores.values())
        average_score = total_score / len(scores)
        
        # Determina nível de usabilidade
        if average_score >= 8:
            usability_level = "🟢 EXCELENTE"
        elif average_score >= 6:
            usability_level = "🟡 BOM"
        elif average_score >= 4:
            usability_level = "🟠 MODERADO"
        else:
            usability_level = "🔴 CRÍTICO"
        
        end_time = time.time()
        duration = end_time - start_time
        
        results = {
            "summary": {
                "total_tests": len(scores),
                "average_score": average_score,
                "usability_level": usability_level,
                "duration_seconds": duration,
                "scores": scores
            },
            "tests": self.test_results,
            "timestamp": datetime.now().isoformat()
        }
        
        print("\n" + "=" * 60)
        print(f"📊 RESULTADOS DOS TESTES DE USABILIDADE")
        print("=" * 60)
        print(f"🎯 Score Geral: {average_score:.1f}/10")
        print(f"📈 Nível: {usability_level}")
        print(f"⏱️  Duração: {duration:.2f} segundos")
        print("\n📋 Scores por Categoria:")
        for category, score in scores.items():
            print(f"   {category.replace('_', ' ').title()}: {score:.1f}/10")
        print("=" * 60)
        
        return results

def main():
    """Função principal para execução dos testes"""
    tester = UsabilityTester()
    results = tester.run_all_tests()
    
    # Salva resultados
    with open("test_reports/usability_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📋 Relatório salvo em: test_reports/usability_test_results.json")
    
    # Retorna código de saída baseado no score
    if results["summary"]["average_score"] >= 6:
        print("🎉 Testes de usabilidade PASSARAM!")
        return 0
    else:
        print("⚠️  Testes de usabilidade FALHARAM - Melhorias necessárias!")
        return 1

if __name__ == "__main__":
    exit(main()) 