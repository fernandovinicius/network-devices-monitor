from flask import Blueprint, render_template

exportar_bp = Blueprint("exportar", __name__, template_folder="../templates")


@exportar_bp.route("/exportar")
def exportar():
    # Lógica para obter dispositivos
    return render_template("exportar.html")
