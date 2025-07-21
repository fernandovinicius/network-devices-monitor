from flask import Blueprint, render_template

editar_bp = Blueprint("editar", __name__, template_folder="../templates")


@editar_bp.route("/editar")
def editar():
    # Lógica para obter dispositivos
    return render_template("editar.html")
