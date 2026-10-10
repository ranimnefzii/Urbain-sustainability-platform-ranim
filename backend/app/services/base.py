"""
Base Service - Urbain Sustainability System
Service de base avec logging et gestion d'erreurs
"""

import logging
from datetime import datetime
from typing import TypeVar, Generic, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import get_db
from app.core.exceptions import (
    DatabaseError,
    NotFoundError,
    ValidationError,
    BusinessLogicError
)

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

logger = logging.getLogger(__name__)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Service de base avec logging et gestion d'erreurs
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def handle_database_error(self, error: Exception, operation: str) -> None:
        """
        Gère les erreurs de base de données avec logging approprié
        """
        if isinstance(error, SQLAlchemyError):
            logger.error(f"Database error during {operation}: {str(error)}")
            raise DatabaseError(f"Database operation failed: {operation}")
        else:
            logger.error(f"Unexpected error during {operation}: {str(error)}")
            raise BusinessLogicError(f"Operation failed: {operation}")
    
    async def validate_required_fields(self, data: Dict[str, Any], required_fields: list) -> None:
        """
        Valide les champs requis
        """
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
    
    async def log_operation(self, operation: str, details: Dict[str, Any] = None) -> None:
        """
        Log les opérations importantes
        """
        log_data = f"Operation: {operation}"
        if details:
            log_data += f" | Details: {details}"
        logger.info(log_data)
    
    async def log_error(self, operation: str, error: Exception, details: Dict[str, Any] = None) -> None:
        """
        Log les erreurs avec contexte
        """
        error_data = f"Error in {operation}: {str(error)}"
        if details:
            error_data += f" | Details: {details}"
        logger.error(error_data, exc_info=True)
    
    async def check_permissions(self, user_id: int, required_permissions: list) -> bool:
        """
        Vérifie les permissions de l'utilisateur (à implémenter selon le système)
        """
        # TODO: Implémenter la logique de permissions
        return True
    
    async def audit_log(self, action: str, entity_type: str, entity_id: int, 
                     user_id: int, old_values: Dict[str, Any] = None, 
                     new_values: Dict[str, Any] = None) -> None:
        """
        Crée un log d'audit pour les opérations critiques
        """
        audit_data = {
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "old_values": old_values,
            "new_values": new_values
        }
        
        # TODO: Sauvegarder dans la table d'audit
        logger.info(f"Audit log: {audit_data}")
    
    async def validate_business_rules(self, entity: ModelType, rules: Dict[str, Any]) -> None:
        """
        Valide les règles métier spécifiques
        """
        for rule_name, rule_func in rules.items():
            try:
                if not rule_func(entity):
                    raise BusinessLogicError(f"Business rule '{rule_name}' violated")
            except Exception as e:
                logger.error(f"Error validating business rule '{rule_name}': {str(e)}")
                raise ValidationError(f"Validation failed for rule '{rule_name}'")
    
    async def calculate_metrics(self, operation: str, start_time: float, end_time: float) -> Dict[str, Any]:
        """
        Calcule les métriques de performance
        """
        duration = end_time - start_time
        
        return {
            "operation": operation,
            "duration_seconds": duration,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def cache_result(self, key: str, data: Any, ttl: int = 3600) -> None:
        """
        Met en cache un résultat (à implémenter avec Redis)
        """
        # TODO: Implémenter le caching avec Redis
        logger.info(f"Caching result for key: {key}")
    
    async def get_cached_result(self, key: str) -> Optional[Any]:
        """
        Récupère un résultat depuis le cache
        """
        # TODO: Implémenter le cache retrieval avec Redis
        logger.info(f"Getting cached result for key: {key}")
        return None
    
    async def invalidate_cache(self, pattern: str) -> None:
        """
        Invalide le cache selon un pattern
        """
        # TODO: Implémenter le cache invalidation avec Redis
        logger.info(f"Invalidating cache for pattern: {pattern}")
    
    async def send_notification(self, notification_type: str, recipients: list, data: Dict[str, Any]) -> None:
        """
        Envoie des notifications (à implémenter avec le service de notification)
        """
        # TODO: Implémenter l'envoi de notifications
        logger.info(f"Sending {notification_type} notification to {len(recipients)} recipients")
    
    async def generate_reference_number(self, entity_type: str) -> str:
        """
        Génère un numéro de référence unique
        """
        import uuid
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8].upper()
        
        return f"{entity_type.upper()}-{timestamp}-{unique_id}"
    
    async def validate_file_upload(self, file_data: bytes, file_type: str, max_size: int = 10 * 1024 * 1024) -> bool:
        """
        Valide l'upload de fichiers
        """
        if len(file_data) > max_size:
            raise ValidationError(f"File size exceeds maximum allowed size of {max_size} bytes")
        
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'text/plain']
        if file_type not in allowed_types:
            raise ValidationError(f"File type {file_type} is not allowed")
        
        return True
    
    async def sanitize_input(self, data: Any) -> Any:
        """
        Nettoie et valide les entrées utilisateur
        """
        if isinstance(data, str):
            # TODO: Implémenter le nettoyage XSS et injection
            return data.strip()
        elif isinstance(data, dict):
            return {k: await self.sanitize_input(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [await self.sanitize_input(item) for item in data]
        
        return data
    
    async def check_rate_limit(self, user_id: int, action: str, limit: int = 100, window_minutes: int = 60) -> bool:
        """
        Vérifie les limites de taux d'utilisation
        """
        # TODO: Implémenter le rate limiting avec Redis
        logger.info(f"Checking rate limit for user {user_id}, action {action}")
        return True
    
    async def get_user_context(self, user_id: int) -> Dict[str, Any]:
        """
        Récupère le contexte utilisateur pour les permissions et préférences
        """
        # TODO: Implémenter la récupération du contexte utilisateur
        return {
            "user_id": user_id,
            "permissions": [],
            "preferences": {},
            "sector_id": None
        }
