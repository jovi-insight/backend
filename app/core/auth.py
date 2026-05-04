"""
Mock de autenticação.
Será substituído por autenticação real (Firebase Auth / JWT) no futuro.
"""


async def get_current_user() -> str:
    """Retorna um user_id fixo para desenvolvimento."""
    return "test_user_123"
