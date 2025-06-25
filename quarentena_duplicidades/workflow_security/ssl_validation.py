"""
Validação de Certificados SSL - TarefaMágica (P2-4)
Implementa validação rigorosa de certificados SSL
"""

import ssl
import socket
import requests
import urllib3
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import certifi

@dataclass
class SSLCertificate:
    subject: str
    issuer: str
    not_before: datetime
    not_after: datetime
    serial_number: str
    fingerprint: str
    version: int
    signature_algorithm: str
    key_size: int
    key_type: str
    san_domains: List[str]
    is_valid: bool
    validation_errors: List[str]

class SSLValidator:
    def __init__(self):
        """
        Inicializa o validador de certificados SSL
        """
        # Configuração de segurança
        self.min_key_size = 2048
        self.max_cert_age_days = 365
        self.required_signature_algorithms = [
            'sha256WithRSAEncryption',
            'sha384WithRSAEncryption',
            'sha512WithRSAEncryption',
            'ecdsa-with-SHA256',
            'ecdsa-with-SHA384',
            'ecdsa-with-SHA512'
        ]
        
        # Domínios confiáveis
        self.trusted_domains = [
            'tarefamagica.com',
            'api.tarefamagica.com',
            'pix.bcb.gov.br',
            'api.pix.bcb.gov.br',
            'googleapis.com',
            'firebase.google.com'
        ]
        
        # Configuração do requests
        self.session = requests.Session()
        self.session.verify = certifi.where()
        
        # Desabilita avisos de SSL
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
    def validate_certificate(self, hostname: str, port: int = 443) -> SSLCertificate:
        """
        Valida certificado SSL de um hostname
        
        Args:
            hostname: Nome do host
            port: Porta (padrão: 443)
            
        Returns:
            SSLCertificate: Informações do certificado
        """
        try:
            # Cria contexto SSL
            context = ssl.create_default_context()
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED
            
            # Conecta ao servidor
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
            # Extrai informações do certificado
            subject = dict(x[0] for x in cert['subject'])
            issuer = dict(x[0] for x in cert['issuer'])
            
            # Converte datas
            not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
            not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            
            # Extrai informações adicionais
            serial_number = cert.get('serialNumber', '')
            version = cert.get('version', 0)
            signature_algorithm = cert.get('signatureAlgorithm', '')
            
            # Calcula fingerprint
            fingerprint = cert.get('fingerprint', '')
            
            # Extrai SAN (Subject Alternative Names)
            san_domains = []
            if 'subjectAltName' in cert:
                for type_name, value in cert['subjectAltName']:
                    if type_name == 'DNS':
                        san_domains.append(value)
                        
            # Valida certificado
            is_valid, errors = self._validate_certificate_details(
                hostname, subject, issuer, not_before, not_after,
                signature_algorithm, san_domains
            )
            
            return SSLCertificate(
                subject=subject.get('commonName', ''),
                issuer=issuer.get('commonName', ''),
                not_before=not_before,
                not_after=not_after,
                serial_number=serial_number,
                fingerprint=fingerprint,
                version=version,
                signature_algorithm=signature_algorithm,
                key_size=0,  # Não disponível via socket
                key_type='',  # Não disponível via socket
                san_domains=san_domains,
                is_valid=is_valid,
                validation_errors=errors
            )
            
        except Exception as e:
            logging.error(f"Erro ao validar certificado SSL para {hostname}: {str(e)}")
            return SSLCertificate(
                subject='',
                issuer='',
                not_before=datetime.utcnow(),
                not_after=datetime.utcnow(),
                serial_number='',
                fingerprint='',
                version=0,
                signature_algorithm='',
                key_size=0,
                key_type='',
                san_domains=[],
                is_valid=False,
                validation_errors=[f"Erro de conexão: {str(e)}"]
            )
            
    def _validate_certificate_details(
        self,
        hostname: str,
        subject: Dict,
        issuer: Dict,
        not_before: datetime,
        not_after: datetime,
        signature_algorithm: str,
        san_domains: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Valida detalhes do certificado
        
        Args:
            hostname: Nome do host
            subject: Assunto do certificado
            issuer: Emissor do certificado
            not_before: Data de início da validade
            not_after: Data de fim da validade
            signature_algorithm: Algoritmo de assinatura
            san_domains: Domínios alternativos
            
        Returns:
            Tuple[bool, List[str]]: (válido, lista de erros)
        """
        errors = []
        current_time = datetime.utcnow()
        
        # Verifica validade temporal
        if current_time < not_before:
            errors.append(f"Certificado ainda não é válido. Válido a partir de {not_before}")
            
        if current_time > not_after:
            errors.append(f"Certificado expirado. Expirou em {not_after}")
            
        # Verifica se está próximo da expiração (30 dias)
        if not_after - current_time < timedelta(days=30):
            errors.append(f"Certificado expira em {(not_after - current_time).days} dias")
            
        # Verifica algoritmo de assinatura
        if signature_algorithm not in self.required_signature_algorithms:
            errors.append(f"Algoritmo de assinatura não seguro: {signature_algorithm}")
            
        # Verifica SAN
        if not san_domains:
            errors.append("Certificado não possui Subject Alternative Names")
        elif hostname not in san_domains:
            # Verifica se o hostname corresponde a algum domínio
            hostname_matches = False
            for san_domain in san_domains:
                if self._domain_matches(hostname, san_domain):
                    hostname_matches = True
                    break
                    
            if not hostname_matches:
                errors.append(f"Hostname {hostname} não corresponde aos SANs: {san_domains}")
                
        # Verifica se é um domínio confiável
        if not self._is_trusted_domain(hostname):
            errors.append(f"Domínio não está na lista de confiança: {hostname}")
            
        return len(errors) == 0, errors
        
    def _domain_matches(self, hostname: str, domain: str) -> bool:
        """
        Verifica se o hostname corresponde ao domínio
        
        Args:
            hostname: Nome do host
            domain: Domínio
            
        Returns:
            bool: True se corresponder
        """
        if hostname == domain:
            return True
            
        # Verifica wildcards
        if domain.startswith('*.'):
            wildcard_domain = domain[2:]
            return hostname.endswith(wildcard_domain)
            
        return False
        
    def _is_trusted_domain(self, hostname: str) -> bool:
        """
        Verifica se o domínio está na lista de confiança
        
        Args:
            hostname: Nome do host
            
        Returns:
            bool: True se confiável
        """
        for trusted_domain in self.trusted_domains:
            if self._domain_matches(hostname, trusted_domain):
                return True
        return False
        
    def make_secure_request(
        self,
        url: str,
        method: str = 'GET',
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None,
        timeout: int = 30
    ) -> Tuple[bool, Optional[requests.Response], List[str]]:
        """
        Faz requisição HTTP segura com validação SSL
        
        Args:
            url: URL da requisição
            method: Método HTTP
            headers: Headers da requisição
            data: Dados da requisição
            timeout: Timeout em segundos
            
        Returns:
            Tuple[bool, Optional[Response], List[str]]: (sucesso, resposta, erros)
        """
        try:
            from urllib.parse import urlparse
            
            # Parse da URL
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname
            port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
            
            # Valida certificado SSL
            if parsed_url.scheme == 'https':
                cert = self.validate_certificate(hostname, port)
                if not cert.is_valid:
                    return False, None, cert.validation_errors
                    
            # Faz requisição
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data if method in ['POST', 'PUT', 'PATCH'] else None,
                params=data if method == 'GET' else None,
                timeout=timeout
            )
            
            return True, response, []
            
        except requests.exceptions.SSLError as e:
            return False, None, [f"Erro SSL: {str(e)}"]
        except requests.exceptions.ConnectionError as e:
            return False, None, [f"Erro de conexão: {str(e)}"]
        except requests.exceptions.Timeout as e:
            return False, None, [f"Timeout: {str(e)}"]
        except Exception as e:
            return False, None, [f"Erro inesperado: {str(e)}"]
            
    def validate_webhook_url(self, url: str) -> Tuple[bool, List[str]]:
        """
        Valida URL de webhook para uso seguro
        
        Args:
            url: URL do webhook
            
        Returns:
            Tuple[bool, List[str]]: (válido, erros)
        """
        try:
            from urllib.parse import urlparse
            
            parsed_url = urlparse(url)
            
            # Verifica se é HTTPS
            if parsed_url.scheme != 'https':
                return False, ["Webhook deve usar HTTPS"]
                
            # Verifica hostname
            hostname = parsed_url.hostname
            if not hostname:
                return False, ["Hostname inválido"]
                
            # Valida certificado
            cert = self.validate_certificate(hostname)
            if not cert.is_valid:
                return False, cert.validation_errors
                
            # Verifica se é domínio confiável
            if not self._is_trusted_domain(hostname):
                return False, [f"Domínio não confiável: {hostname}"]
                
            return True, []
            
        except Exception as e:
            return False, [f"Erro ao validar webhook: {str(e)}"]
            
    def get_certificate_info(self, hostname: str, port: int = 443) -> Dict:
        """
        Obtém informações detalhadas do certificado
        
        Args:
            hostname: Nome do host
            port: Porta
            
        Returns:
            Dict: Informações do certificado
        """
        try:
            cert = self.validate_certificate(hostname, port)
            
            return {
                'hostname': hostname,
                'port': port,
                'subject': cert.subject,
                'issuer': cert.issuer,
                'not_before': cert.not_before.isoformat(),
                'not_after': cert.not_after.isoformat(),
                'serial_number': cert.serial_number,
                'fingerprint': cert.fingerprint,
                'version': cert.version,
                'signature_algorithm': cert.signature_algorithm,
                'san_domains': cert.san_domains,
                'is_valid': cert.is_valid,
                'validation_errors': cert.validation_errors,
                'days_until_expiry': (cert.not_after - datetime.utcnow()).days if cert.not_after else 0
            }
            
        except Exception as e:
            logging.error(f"Erro ao obter informações do certificado: {str(e)}")
            return {
                'hostname': hostname,
                'port': port,
                'error': str(e)
            }
            
    def check_certificate_health(self) -> Dict:
        """
        Verifica saúde dos certificados dos domínios confiáveis
        
        Returns:
            Dict: Relatório de saúde
        """
        try:
            health_report = {
                'total_domains': len(self.trusted_domains),
                'valid_certificates': 0,
                'expiring_soon': 0,
                'invalid_certificates': 0,
                'domains': {}
            }
            
            for domain in self.trusted_domains:
                try:
                    cert_info = self.get_certificate_info(domain)
                    
                    if cert_info.get('is_valid', False):
                        health_report['valid_certificates'] += 1
                        
                        # Verifica se está próximo da expiração
                        days_until_expiry = cert_info.get('days_until_expiry', 0)
                        if days_until_expiry <= 30:
                            health_report['expiring_soon'] += 1
                    else:
                        health_report['invalid_certificates'] += 1
                        
                    health_report['domains'][domain] = cert_info
                    
                except Exception as e:
                    health_report['invalid_certificates'] += 1
                    health_report['domains'][domain] = {'error': str(e)}
                    
            return health_report
            
        except Exception as e:
            logging.error(f"Erro ao verificar saúde dos certificados: {str(e)}")
            return {'error': str(e)}

# Instância global do validador SSL
ssl_validator = SSLValidator() 