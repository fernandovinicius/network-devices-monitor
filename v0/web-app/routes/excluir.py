from flask import Blueprint, render_template

excluir_bp = Blueprint("excluir", __name__, template_folder="../templates")


@excluir_bp.route("/excluir")
def excluir():
    # Lógica para obter dispositivos
    return render_template("excluir.html")
