import logging
import random
import time

logging.basicConfig(filename='outputs/pix_validation.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def simular_transacao_pix(valor, usuario):
    try:
        logging.info(f'Iniciando transação PIX para {usuario} no valor de R${valor:.2f}')
        # Simula validação de limites
        if valor > 1000:
            raise ValueError('Valor excede o limite permitido')
        # Simula chance de erro
        if random.random() < 0.1:
            raise Exception('Erro aleatório na transação PIX')
        # Simula tempo de processamento
        time.sleep(1)
        logging.info(f'Transação PIX concluída com sucesso para {usuario} no valor de R${valor:.2f}')
        return True
    except Exception as e:
        logging.error(f'Falha na transação PIX para {usuario}: {e}')
        return False

if __name__ == '__main__':
    usuarios = ['joao', 'maria', 'ana']
    for usuario in usuarios:
        valor = random.choice([50, 200, 1200])
        sucesso = simular_transacao_pix(valor, usuario)
        print(f'Transação para {usuario} (R${valor}):', 'Sucesso' if sucesso else 'Falhou') 