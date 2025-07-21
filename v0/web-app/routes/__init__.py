from .home import home_bp
from .exportar import exportar_bp
from .cadastrar import cadastrar_bp
from .editar import editar_bp
from .excluir import excluir_bp

all_routes = [home_bp, exportar_bp, cadastrar_bp, editar_bp, excluir_bp]
