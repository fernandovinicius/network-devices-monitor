from flask import Blueprint, render_template, request

cadastrar_bp = Blueprint("cadastrar", __name__, template_folder="../templates")

@cadastrar_bp.route('/cadastrar')
def cadastrar():
    return render_template('cadastrar.html')