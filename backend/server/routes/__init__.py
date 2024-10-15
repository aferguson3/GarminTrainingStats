from backend.server.routes.admin import admin_bp
from backend.server.routes.database import database_bp
from backend.server.routes.service import service_bp
from backend.server.routes.status_codes import statues_bp

__all__ = ["admin_bp", "database_bp", "service_bp", "statues_bp"]
