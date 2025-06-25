
from flask import Flask, request, jsonify
from workflow.security.rate_limiting import rate_limiter, RateLimitType

app = Flask(__name__)

@app.route('/test/rate-limit', methods=['POST'])
def test_rate_limit():
    """Endpoint para testar rate limiting"""
    try:
        data = request.get_json()
        identifier = data.get('identifier', 'test_user')
        limit_type_str = data.get('limit_type', 'login_attempts')
        
        # Converte string para enum
        limit_type = RateLimitType(limit_type_str)
        
        # Verifica rate limit
        allowed, message = rate_limiter.check_rate_limit(identifier, limit_type)
        
        # Obtém status
        status = rate_limiter.get_status(identifier, limit_type)
        
        return jsonify({
            'success': True,
            'allowed': allowed,
            'message': message,
            'status': status
        }), 200 if allowed else 429
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
