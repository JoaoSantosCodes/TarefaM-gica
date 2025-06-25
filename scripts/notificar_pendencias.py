import os

PENDENCIAS_FILE = 'outputs/pendencias_criticas.txt'

# Simula envio de notificação (pode ser adaptado para e-mail, Slack, etc.)
def enviar_notificacao(mensagem, destino='equipe@tarefamagica.com'):
    print(f'--- Notificação enviada para {destino} ---')
    print(mensagem)
    print('----------------------------------------')

if __name__ == '__main__':
    if not os.path.exists(PENDENCIAS_FILE):
        print('Arquivo de pendências não encontrado!')
        exit(1)
    with open(PENDENCIAS_FILE, encoding='utf-8') as f:
        pendencias = f.read().strip()
    if not pendencias or 'Nenhuma pendência' in pendencias:
        print('Nenhuma pendência crítica para notificar.')
    else:
        mensagem = f"Pendências Críticas Detectadas:\n\n{pendencias}\n\nPor favor, priorize a resolução destas tarefas."
        enviar_notificacao(mensagem) 