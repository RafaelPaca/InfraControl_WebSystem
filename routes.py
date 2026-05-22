from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from models import db, Usuario, Chamado, Setor, Avaliacao, Logs_Chamado
from werkzeug.security import generate_password_hash
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from ml_model import predict_time

bp = Blueprint('main', __name__)

# --- WEB VIEWS (TEMPLATES) ---

@bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.perfil == 'Usuario':
            return redirect(url_for('main.user_dashboard'))
        elif current_user.perfil == 'Tecnico':
            return redirect(url_for('main.tech_dashboard'))
        elif current_user.perfil == 'Gestor':
            return redirect(url_for('main.manager_dashboard'))
        elif current_user.perfil == 'Admin':
            return redirect(url_for('main.admin_dashboard'))
    return redirect(url_for('main.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_username = request.form.get('nome')
        senha = request.form.get('senha')
        user = Usuario.query.filter((Usuario.email_corporativo == email_or_username) | (Usuario.nome == email_or_username)).first()
        if user and user.check_senha(senha):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('Nome de usuário ou senha inválidos')
    return render_template('login.html')

@bp.route('/register', methods=['POST'])
def register():
    nome = request.form.get('nome')
    sobrenome = request.form.get('sobrenome')
    cpf = request.form.get('cpf')
    data_nascimento = request.form.get('data_nascimento')
    email = request.form.get('email')
    senha = request.form.get('senha')
    
    if Usuario.query.filter_by(cpf=cpf).first() or Usuario.query.filter_by(email_corporativo=email).first():
        flash('CPF ou Email já cadastrado.')
        return redirect(url_for('main.login'))
        
    try:
        dt_nasc = datetime.strptime(data_nascimento, '%Y-%m-%d').date()
    except:
        flash('Data de nascimento inválida.')
        return redirect(url_for('main.login'))

    novo_usuario = Usuario(
        nome=nome,
        sobrenome=sobrenome,
        cpf=cpf,
        data_nascimento=dt_nasc,
        email_corporativo=email,
        perfil='Usuario'
    )
    novo_usuario.set_senha(senha)
    db.session.add(novo_usuario)
    db.session.commit()
    flash('Cadastro realizado com sucesso!')
    return redirect(url_for('main.login'))

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@bp.route('/dashboard/usuario')
@login_required
def user_dashboard():
    if current_user.perfil != 'Usuario' and current_user.perfil != 'Admin':
        return redirect(url_for('main.index'))
    chamados = Chamado.query.filter_by(usuario_id=current_user.id).all()
    return render_template('user_dashboard.html', chamados=chamados)

@bp.route('/dashboard/tecnico')
@login_required
def tech_dashboard():
    if current_user.perfil != 'Tecnico' and current_user.perfil != 'Admin':
        return redirect(url_for('main.index'))
        
    categoria_map = {
        'ELÉTRICA': 'MANUTENÇÃO ELÉTRICA',
        'HIDRÁULICA': 'MANUTENÇÃO HIDRÁULICA',
        'ESTRUTURAL': 'MANUTENÇÃO ESTRUTURAL/CIVIL',
        'CLIMATIZAÇÃO': 'CLIMATIZAÇÃO',
        'SERVIÇOS GERAIS': 'SERVIÇOS GERAIS'
    }
    
    query_atribuidos = Chamado.query.filter_by(status='EQUIPE TÉCNICA ACIONADA')
    query_atendimento = Chamado.query.filter_by(status='ATENDIMENTO INICIADO')
    query_concluidos = Chamado.query.filter_by(status='CONCLUÍDO')
    
    if current_user.perfil == 'Tecnico' and current_user.equipe:
        cat_alvo = categoria_map.get(current_user.equipe)
        if cat_alvo:
            query_atribuidos = query_atribuidos.filter_by(categoria=cat_alvo)
            query_atendimento = query_atendimento.filter_by(categoria=cat_alvo)
            query_concluidos = query_concluidos.filter_by(categoria=cat_alvo)
        else:
            query_atribuidos = query_atribuidos.filter_by(equipe_responsavel=current_user.equipe)
            query_atendimento = query_atendimento.filter_by(equipe_responsavel=current_user.equipe)
            query_concluidos = query_concluidos.filter_by(equipe_responsavel=current_user.equipe)
            
    chamados_atribuidos = query_atribuidos.all()
    chamados_atendimento = query_atendimento.all()
    chamados_concluidos = query_concluidos.all()
    
    return render_template('tech_dashboard.html', 
                           atribuidos=chamados_atribuidos, 
                           em_atendimento=chamados_atendimento,
                           concluidos=chamados_concluidos)

@bp.route('/dashboard/gestor')
@login_required
def manager_dashboard():
    if current_user.perfil != 'Gestor' and current_user.perfil != 'Admin':
        return redirect(url_for('main.index'))
    chamados_abertos = Chamado.query.filter_by(status='ABERTO').all()
    chamados_atendimento = Chamado.query.filter_by(status='ATENDIMENTO INICIADO').all()
    chamados_concluidos = Chamado.query.filter_by(status='CONCLUÍDO').all()
    tecnicos = Usuario.query.filter_by(perfil='Tecnico').all()
    return render_template('manager_dashboard.html', 
                           abertos=chamados_abertos,
                           em_atendimento=chamados_atendimento,
                           concluidos=chamados_concluidos,
                           tecnicos=tecnicos)

@bp.route('/dashboard/admin')
@login_required
def admin_dashboard():
    if current_user.perfil != 'Admin':
        return redirect(url_for('main.index'))
    return render_template('admin_dashboard.html')

@bp.route('/dashboard/admin/usuarios')
@login_required
def admin_usuarios():
    if current_user.perfil != 'Admin':
        return redirect(url_for('main.index'))
    usuarios = Usuario.query.all()
    return render_template('admin_usuarios.html', usuarios=usuarios)

# --- API ENDPOINTS ---

@bp.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.json
    user = Usuario.query.filter((Usuario.email_corporativo == data.get('nome')) | (Usuario.nome == data.get('nome'))).first()
    if user and user.check_senha(data.get('senha')):
        login_user(user)
        return jsonify({'message': 'Logado com sucesso', 'user_id': user.id})
    return jsonify({'error': 'Credenciais invalidas'}), 401

@bp.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.json
    # Implement registration logic
    return jsonify({'message': 'Registrado com sucesso'})

@bp.route('/api/usuarios', methods=['GET', 'POST'])
def api_usuarios():
    if request.method == 'GET':
        users = Usuario.query.all()
        return jsonify([{'id': u.id, 'nome': u.nome, 'perfil': u.perfil} for u in users])
    else:
        # Create user
        return jsonify({'message': 'Criado'})

@bp.route('/api/usuarios/<int:id>', methods=['PUT'])
def api_update_usuario(id):
    user = Usuario.query.get_or_404(id)
    data = request.json
    if 'perfil' in data:
        user.perfil = data['perfil']
    if 'equipe' in data:
        user.equipe = data['equipe']
    if 'funcao' in data:
        user.funcao = data['funcao']
    db.session.commit()
    return jsonify({'message': 'Atualizado'})

@bp.route('/api/chamados', methods=['GET', 'POST'])
def api_chamados():
    if request.method == 'GET':
        chamados = Chamado.query.all()
        return jsonify([{'id': c.id, 'status': c.status, 'prioridade': c.prioridade} for c in chamados])
    else:
        # Create chamado logic handles image upload so it's mostly form-data
        data = request.json
        setor_nome = data.get('setor')
        setor = Setor.query.filter_by(nome=setor_nome).first()
        if not setor:
            setor = Setor(nome=setor_nome)
            db.session.add(setor)
            db.session.commit()
            
        tempo_estimado = predict_time(data['categoria'], data['prioridade'], data['setor'], 'BOM')
        
        novo_chamado = Chamado(
            usuario_id=current_user.id if current_user.is_authenticated else 1,
            setor_id=setor.id,
            categoria=data['categoria'],
            problema=data['problema'],
            detalhes=data.get('detalhes', ''),
            prioridade=data['prioridade'],
            status='ABERTO',
            tempo_estimado=tempo_estimado
        )
        db.session.add(novo_chamado)
        db.session.commit()
        return jsonify({'message': 'Chamado criado', 'id': novo_chamado.id, 'tempo_estimado': tempo_estimado})

@bp.route('/api/chamados/<int:id>', methods=['GET', 'PUT'])
def api_chamado_detail(id):
    chamado = Chamado.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify({'id': chamado.id, 'status': chamado.status, 'categoria': chamado.categoria})
    else:
        data = request.json
        # update status logic
        if 'status' in data:
            chamado.status = data['status']
            if data['status'] == 'EQUIPE TÉCNICA ACIONADA':
                chamado.data_acionamento = datetime.utcnow()
                chamado.equipe_responsavel = data.get('equipe')
                chamado.tecnico_lider_id = data.get('tecnico_lider_id')
            elif data['status'] == 'ATENDIMENTO INICIADO':
                chamado.data_inicio = datetime.utcnow()
            elif data['status'] == 'CONCLUÍDO':
                chamado.data_conclusao = datetime.utcnow()
                
        db.session.commit()
        return jsonify({'message': 'Atualizado'})

@bp.route('/api/dashboard/metricas', methods=['GET'])
@login_required
def api_metricas():
    categoria_map = {
        'ELÉTRICA': 'MANUTENÇÃO ELÉTRICA',
        'HIDRÁULICA': 'MANUTENÇÃO HIDRÁULICA',
        'ESTRUTURAL': 'MANUTENÇÃO ESTRUTURAL/CIVIL',
        'CLIMATIZAÇÃO': 'CLIMATIZAÇÃO',
        'SERVIÇOS GERAIS': 'SERVIÇOS GERAIS'
    }

    if current_user.perfil == 'Tecnico' and current_user.equipe:
        cat_alvo = categoria_map.get(current_user.equipe)
        if cat_alvo:
            atribuidos = Chamado.query.filter_by(status='EQUIPE TÉCNICA ACIONADA', categoria=cat_alvo).count()
            em_atendimento = Chamado.query.filter_by(status='ATENDIMENTO INICIADO', categoria=cat_alvo).count()
            concluidos = Chamado.query.filter_by(status='CONCLUÍDO', categoria=cat_alvo).count()
            
            alta = Chamado.query.filter_by(prioridade='ALTA', categoria=cat_alvo).count()
            media = Chamado.query.filter_by(prioridade='MÉDIA', categoria=cat_alvo).count()
            baixa = Chamado.query.filter_by(prioridade='BAIXA', categoria=cat_alvo).count()
        else:
            atribuidos = Chamado.query.filter_by(status='EQUIPE TÉCNICA ACIONADA', equipe_responsavel=current_user.equipe).count()
            em_atendimento = Chamado.query.filter_by(status='ATENDIMENTO INICIADO', equipe_responsavel=current_user.equipe).count()
            concluidos = Chamado.query.filter_by(status='CONCLUÍDO', equipe_responsavel=current_user.equipe).count()
            
            alta = Chamado.query.filter_by(prioridade='ALTA', equipe_responsavel=current_user.equipe).count()
            media = Chamado.query.filter_by(prioridade='MÉDIA', equipe_responsavel=current_user.equipe).count()
            baixa = Chamado.query.filter_by(prioridade='BAIXA', equipe_responsavel=current_user.equipe).count()

        return jsonify({
            'atribuidos': atribuidos,
            'em_atendimento': em_atendimento,
            'concluidos': concluidos,
            'alta': alta,
            'media': media,
            'baixa': baixa
        })
    else:
        abertos = Chamado.query.filter_by(status='ABERTO').count()
        em_atendimento = Chamado.query.filter_by(status='ATENDIMENTO INICIADO').count()
        concluidos = Chamado.query.filter_by(status='CONCLUÍDO').count()
        return jsonify({'abertos': abertos, 'em_atendimento': em_atendimento, 'concluidos': concluidos})

@bp.route('/api/dashboard/previsao', methods=['POST'])
def api_previsao():
    data = request.json
    # data: categoria, prioridade, setor, historico_tecnico
    cat = data.get('categoria', 'SERVIÇOS GERAIS')
    prio = data.get('prioridade', 'MÉDIA')
    setor = data.get('setor', 'RH')
    hist = data.get('historico_tecnico', 'BOM')
    tempo = predict_time(cat, prio, setor, hist)
    return jsonify({'tempo_estimado_horas': tempo})

@bp.route('/meu-perfil', methods=['GET', 'POST'])
@login_required
def meu_perfil():

    if request.method == 'POST':

        novo_email = request.form.get('email')
        nova_senha = request.form.get('senha')

        current_user.email_corporativo = novo_email

        if nova_senha and nova_senha.strip() != "":
            current_user.set_senha(nova_senha)

        db.session.commit()

        flash('Perfil atualizado com sucesso!')

        return redirect(url_for('main.meu_perfil'))

    return render_template('my_profile.html')

