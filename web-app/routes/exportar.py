from flask import Blueprint, render_template, request

exportar_bp = Blueprint("exportar", __name__, template_folder="../templates")

@exportar_bp.route('/exportar')
def exportar():
    return render_template('exportar.html')