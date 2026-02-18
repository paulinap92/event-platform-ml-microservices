from app.service.user_service import UserService
from app.db.repository import user_repository, activation_token_repository

user_service = UserService(user_repository, activation_token_repository)
