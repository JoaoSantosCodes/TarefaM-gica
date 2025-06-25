import unittest

# Exemplo de função a ser testada
def soma(a, b):
    return a + b

class TestSoma(unittest.TestCase):
    def test_soma_basica(self):
        self.assertEqual(soma(2, 3), 5)
        self.assertEqual(soma(-1, 1), 0)

    def test_soma_zero(self):
        self.assertEqual(soma(0, 0), 0)

# Exemplo de teste de integração (simulado)
def autenticar_usuario(usuario, senha):
    # Simulação de autenticação
    return usuario == 'admin' and senha == '1234'

class TestIntegracaoAutenticacao(unittest.TestCase):
    def test_autenticacao_sucesso(self):
        self.assertTrue(autenticar_usuario('admin', '1234'))
    def test_autenticacao_falha(self):
        self.assertFalse(autenticar_usuario('user', 'wrong'))

if __name__ == '__main__':
    unittest.main() 