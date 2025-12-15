"""
Servicio de autenticación de usuarios.
"""
import json
import os
from typing import Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
USERS_PATH = os.path.join(BASE_DIR, 'data', 'users.json')

class AuthService:
    
    @staticmethod
    def load_users() -> list:
        """Carga la lista de usuarios desde el JSON."""
        try:
            with open(USERS_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('users', [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[AuthService] Error cargando usuarios: {e}")
            return []
    
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autentica un usuario y devuelve sus datos si es válido.
        Retorna None si las credenciales son inválidas.
        """
        users = AuthService.load_users()
        
        for user in users:
            if user.get('username') == username and user.get('password') == password:
                # Devolver usuario sin la contraseña
                return {
                    'id': user.get('id'),
                    'username': user.get('username'),
                    'role': user.get('role'),
                    'name': user.get('name')
                }
        
        return None
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Busca un usuario por ID."""
        users = AuthService.load_users()
        
        for user in users:
            if str(user.get('id')) == str(user_id):
                return {
                    'id': user.get('id'),
                    'username': user.get('username'),
                    'role': user.get('role'),
                    'name': user.get('name')
                }
        
        return None
