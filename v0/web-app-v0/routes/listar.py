from flask import Blueprint, render_template

listar_bp = Blueprint("listar", __name__, template_folder="../templates")


@listar_bp.route("/listar")
def listar():
    # Lógica para obter dispositivos
    return render_template("listar.html")
