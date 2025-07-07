from flask import Blueprint, render_template, request

editar_bp = Blueprint("editar", __name__, template_folder="../templates")

@editar_bp.route('/editar')
def editar():
    return render_template('editar.html')