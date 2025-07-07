from flask import Blueprint, render_template, request

excluir_bp = Blueprint("excluir", __name__, template_folder="../templates")

@excluir_bp.route('/excluir')
def excluir():
    return render_template('excluir.html')