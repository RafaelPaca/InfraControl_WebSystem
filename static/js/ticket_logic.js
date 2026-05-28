document.addEventListener('DOMContentLoaded', function() {
    const categoriaSelect = document.getElementById('categoria');
    const problemaSelect = document.getElementById('problema');
    const detalhesTextarea = document.getElementById('detalhes');
    const formNovoChamado = document.getElementById('form-novo-chamado');

    const opcoesProblema = {
        'MANUTENÇÃO ELÉTRICA': [
            'SOBRECARGA ELÉTRICA', 'FALHA DE ILUMINAÇÃO', 'PROBLEMAS/FALHA DE GERADOR', 
            'PROBLEMAS COM PÁRA-RAIOS', 'PROBLEMAS COM TOMADAS/DISJUNTORES', 'OUTRO'
        ],
        'MANUTENÇÃO HIDRÁULICA': [
            'ENTUPIMENTOS DE PIAS/VASOS SANITÁRIOS', 'ENTUPIMENTOS DE CANALIZAÇÃO', 
            'ENTUPIMENTOS EM CAIXAS DE PASSAGEM', 'VAZAMENTOS', 'ALAGAMENTOS', 
            'ÁGUA MINANDO DO CHÃO', 'PEÇAS SANITÁRIAS COM DEFEITO/QUEBRADAS', 'OUTRO'
        ],
        'MANUTENÇÃO ESTRUTURAL/CIVIL': [
            'INFILTRAÇÕES/PAREDES COM UMIDADE', 'INFILTRAÇÕES EM TELHADOS', 
            'AZULEJOS QUEBRADOS/DESTACADOS', 'REBOCO OU CERÂMICA QUEBRADOS/DESTACADOS', 
            'PISOS QUEBRADOS/DESTACADOS', 'VIDROS E ESQUADRIAS TRINCADOS/QUEBRADOS', 
            'TELHAS QUEBRADAS', 'PROBLEMAS EM FORROS', 'PROBLEMAS COM PINTURA INTERNA DE AMBIENTES', 
            'PROBLEMAS COM PINTURA DE ÁREAS EXTERNAS', 'PORTAS E PORTÕES INSEGUROS/COM DEFEITO', 
            'MUROS, CERCAS OU ALAMBRADOS INSEGUROS', 'IRREGULARIDADES EM ESCADAS', 'OUTRO'
        ],
        'CLIMATIZAÇÃO': [
            'AR CONDICIONADO COM MAL FUNCIONAMENTO/QUEBRADO', 'AR CONDICIONADO EXPELINDO SUJIDADES', 
            'AR CONDICIONADO EXALANDO MAL ODOR', 'AR CONDICIONADO COM VAZAMENTO', 
            'CAPACIDADE DO AR INSUFICIENTE', 'OUTRO'
        ],
        'SERVIÇOS GERAIS': [
            'PROBLEMA OU FALTA DE MICROONDAS', 'PROBLEMA OU FALTA DE IMPRESSORA MULTIFUNCIONAL', 
            'PROBLEMA OU FALTA DE MESAS', 'PROBLEMA OU FALTA DE GAVETEIROS', 
            'PROBLEMA OU FALTA DE ARMÁRIOS', 'PROBLEMA OU FALTA DE OUTROS MÓVEIS', 
            'PROBLEMA OU FALTA DE CADEIRAS', 'PROBLEMA OU FALTA DE PERSIANAS', 
            'PERSIANAS SUJAS/QUEBRADAS', 'AUSÊNCIA DE SINALIZAÇÃO, PLACAS E ORIENTAÇÃO', 'OUTRO'
        ]
    };

    if(categoriaSelect) {
        categoriaSelect.addEventListener('change', function() {
            const categoria = this.value;
            problemaSelect.innerHTML = '<option value="">Selecione...</option>';
            
            if (categoria) {
                problemaSelect.disabled = false;
                const opcoes = opcoesProblema[categoria];
                opcoes.forEach(op => {
                    const option = document.createElement('option');
                    option.value = op;
                    option.textContent = op;
                    problemaSelect.appendChild(option);
                });
            } else {
                problemaSelect.disabled = true;
            }
        });
    }

    if(problemaSelect) {
        problemaSelect.addEventListener('change', function() {
            if (this.value === 'OUTRO') {
                detalhesTextarea.required = true;
            } else {
                detalhesTextarea.required = false;
            }
        });
    }

    if(formNovoChamado) {
        formNovoChamado.addEventListener('submit', function(e) {
            e.preventDefault();
            

            const payload = {
                setor: document.getElementById('setor').value,
                categoria: document.getElementById('categoria').value,
                problema: document.getElementById('problema').value,
                prioridade: document.getElementById('prioridade').value,
                detalhes: document.getElementById('detalhes').value
            };

            fetch('/api/chamados', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                alert('Chamado aberto com sucesso! Tempo estimado de conclusão (ML): ' + data.tempo_estimado + ' horas.');
                window.location.reload();
            })
            .catch(err => {
                console.error(err);
                alert('Erro ao abrir o chamado.');
            });
        });
    }
});

/**
 * Converte horas decimais em formato legível: "X horas e Y minutos"
 * Ex: 3.7 => "3 horas e 42 minutos" | 0.5 => "30 minutos" | 1.0 => "1 hora"
 */
function formatarTempo(horas) {
    if (!horas && horas !== 0) return 'N/A';
    const h = Math.floor(horas);
    const min = Math.round((horas - h) * 60);
    
    if (h === 0) {
        return min === 1 ? '1 minuto' : `${min} minutos`;
    }
    
    const hStr = h === 1 ? '1 hora' : `${h} horas`;
    if (min === 0) {
        return hStr;
    }
    
    const minStr = min === 1 ? '1 minuto' : `${min} minutos`;
    return `${hStr} e ${minStr}`;
}

function visualizarChamado(id) {
    fetch(`/api/chamados/${id}`)
        .then(res => res.json())
        .then(data => {
            const modal = document.getElementById('modal-chamado');
            document.getElementById('modal-titulo').innerText = `Chamado #${data.id}`;

            // --- Linha da Vida (Timeline) ---
            const timelineHTML = buildTimeline(data.status);
            document.getElementById('timeline-container').innerHTML = timelineHTML;

            // --- Badge de prioridade ---
            const prioColor = data.prioridade === 'ALTA' ? '#dc2626' : data.prioridade === 'MÉDIA' ? '#d97706' : '#059669';

            // --- Seção de equipe/técnicos (EQUIPE TÉCNICA ACIONADA ou além) ---
            const statusAtivos = ['EQUIPE TÉCNICA ACIONADA', 'ATENDIMENTO INICIADO', 'CONCLUÍDO'];
            let equipeHTML = '';
            if (statusAtivos.includes(data.status) && data.equipe_responsavel) {
                equipeHTML = `
                <div style="background: rgba(245,158,11,0.08); border-radius: 12px; padding: 1.1rem 1.25rem; border: 1px solid rgba(245,158,11,0.2); margin-bottom: 1rem;">
                    <h4 style="margin: 0 0 0.6rem; font-size: 1rem; color: #92400e; display:flex; align-items:center; gap:8px;">🟡 Equipe Técnica Acionada</h4>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.75rem;">
                        <div>
                            <p style="color:#78716c; font-size:0.75rem; margin:0 0 3px; text-transform:uppercase;">Equipe Responsável</p>
                            <p style="font-weight:600; margin:0;">${data.equipe_responsavel}</p>
                        </div>
                        <div>
                            <p style="color:#78716c; font-size:0.75rem; margin:0 0 3px; text-transform:uppercase;">Técnico Líder</p>
                            <p style="font-weight:600; margin:0;">${data.tecnico_lider || 'N/A'}</p>
                        </div>
                    </div>
                </div>`;
            }

            // --- Seção de início de atendimento ---
            let inicioHTML = '';
            if (['ATENDIMENTO INICIADO', 'CONCLUÍDO'].includes(data.status) && data.data_inicio) {
                inicioHTML = `
                <div style="background: rgba(37,99,235,0.06); border-radius: 12px; padding: 1.1rem 1.25rem; border: 1px solid rgba(37,99,235,0.15); margin-bottom: 1rem;">
                    <h4 style="margin: 0 0 0.6rem; font-size: 1rem; color: #1d4ed8; display:flex; align-items:center; gap:8px;">🔵 Atendimento Iniciado</h4>
                    <p style="color:#78716c; font-size:0.75rem; margin:0 0 3px; text-transform:uppercase;">Data de Início</p>
                    <p style="font-weight:600; margin:0;">${data.data_inicio}</p>
                </div>`;
            }

            // --- Seção de conclusão ---
            let conclusaoHTML = '';
            if (data.status === 'CONCLUÍDO' && data.data_conclusao) {
                conclusaoHTML = `
                <div style="background: rgba(16,185,129,0.07); border-radius: 12px; padding: 1.1rem 1.25rem; border: 1px solid rgba(16,185,129,0.2); margin-bottom: 1rem;">
                    <h4 style="margin: 0 0 0.6rem; font-size: 1rem; color: #065f46; display:flex; align-items:center; gap:8px;">🟢 Chamado Concluído</h4>
                    <p style="color:#78716c; font-size:0.75rem; margin:0 0 3px; text-transform:uppercase;">Data de Conclusão</p>
                    <p style="font-weight:600; margin:0;">${data.data_conclusao}</p>
                </div>`;
            }

            // --- Conteúdo principal do chamado ---
            document.getElementById('modal-detalhes-conteudo').innerHTML = `
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.9rem; margin-bottom:1rem;">
                    <div style="background:rgba(37,99,235,0.07); border-radius:10px; padding:0.9rem;">
                        <p style="color:#64748b; font-size:0.75rem; margin:0 0 3px; text-transform:uppercase; letter-spacing:.05em;">Nº do Chamado</p>
                        <p style="font-weight:700; font-size:1.1rem; margin:0; color:#2563eb;">#${data.id}</p>
                    </div>
                    <div style="background:rgba(37,99,235,0.07); border-radius:10px; padding:0.9rem;">
                        <p style="color:#64748b; font-size:0.75rem; margin:0 0 3px; text-transform:uppercase; letter-spacing:.05em;">Prioridade</p>
                        <p style="font-weight:700; font-size:1.1rem; margin:0; color:${prioColor};">${data.prioridade}</p>
                    </div>
                    <div style="background:rgba(37,99,235,0.07); border-radius:10px; padding:0.9rem;">
                        <p style="color:#64748b; font-size:0.75rem; margin:0 0 3px; text-transform:uppercase; letter-spacing:.05em;">Setor / Local</p>
                        <p style="font-weight:600; margin:0;">${data.setor}</p>
                    </div>
                    <div style="background:rgba(37,99,235,0.07); border-radius:10px; padding:0.9rem;">
                        <p style="color:#64748b; font-size:0.75rem; margin:0 0 3px; text-transform:uppercase; letter-spacing:.05em;">Categoria</p>
                        <p style="font-weight:600; margin:0;">${data.categoria}</p>
                    </div>
                    <div style="background:rgba(37,99,235,0.07); border-radius:10px; padding:0.9rem;">
                        <p style="color:#64748b; font-size:0.75rem; margin:0 0 3px; text-transform:uppercase; letter-spacing:.05em;">Data de Abertura</p>
                        <p style="font-weight:600; margin:0;">${data.data_abertura}</p>
                    </div>
                    <div style="background:rgba(37,99,235,0.07); border-radius:10px; padding:0.9rem;">
                        <p style="color:#64748b; font-size:0.75rem; margin:0 0 3px; text-transform:uppercase; letter-spacing:.05em;">Status</p>
                        <p style="font-weight:600; margin:0;">${data.status}</p>
                    </div>
                </div>

                <div style="background:rgba(37,99,235,0.07); border-radius:10px; padding:0.9rem; margin-bottom:0.9rem;">
                    <p style="color:#64748b; font-size:0.75rem; margin:0 0 5px; text-transform:uppercase; letter-spacing:.05em;">Problema Relatado</p>
                    <p style="font-weight:500; margin:0;">${data.problema}</p>
                </div>

                ${data.detalhes ? `
                <div style="background:rgba(37,99,235,0.07); border-radius:10px; padding:0.9rem; margin-bottom:1rem;">
                    <p style="color:#64748b; font-size:0.75rem; margin:0 0 5px; text-transform:uppercase; letter-spacing:.05em;">Mais Detalhes</p>
                    <p style="font-weight:400; font-size:0.95rem; margin:0; white-space:pre-wrap;">${data.detalhes}</p>
                </div>` : ''}

                ${equipeHTML}
                ${inicioHTML}
                ${conclusaoHTML}
            `;

            // --- Tempo estimado ---
            document.getElementById('modal-tempo-estimado').innerHTML = data.tempo_estimado
                ? `<div style="background:rgba(5,150,105,0.08); border-radius:10px; padding:0.75rem 1rem; display:flex; align-items:center; gap:10px; margin-top:0.5rem;">
                       <span style="font-size:1.2rem;">⏱️</span>
                       <span style="color:#64748b; font-size:0.9rem;">Previsão de resolução (ML):</span>
                       <strong style="color:#059669;">${formatarTempo(data.tempo_estimado)}</strong>
                   </div>`
                : '';

            // --- Botões de ação ---
            const actionsDiv = document.getElementById('modal-actions');
            if (data.status === 'ABERTO') {
                actionsDiv.innerHTML = `
                    <button class="btn btn-secondary" style="color:#dc2626; border-color:#dc2626;" onclick="excluirChamado(${data.id})">🗑️ Cancelar Chamado</button>
                    <button class="btn btn-secondary" onclick="closeModal()">Fechar</button>`;
            } else {
                actionsDiv.innerHTML = `<button class="btn btn-secondary" style="width:100%;" onclick="closeModal()">Fechar</button>`;
            }

            modal.style.display = 'flex';
        });
}

function excluirChamado(id) {
    if (!confirm('Tem certeza que deseja cancelar este chamado?')) return;
    fetch(`/api/chamados/${id}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({status: 'CANCELADO'})
    }).then(() => {
        alert('Chamado cancelado.');
        window.location.reload();
    });
}

function buildTimeline(status) {
    const steps = ['ABERTO', 'EQUIPE TÉCNICA ACIONADA', 'ATENDIMENTO INICIADO', 'CONCLUÍDO'];
    let currentIndex = steps.indexOf(status);
    if(currentIndex === -1) currentIndex = 0;

    let html = '<ul class="timeline">';
    steps.forEach((step, index) => {
        let liClass = '';
        if (index <= currentIndex) liClass = 'active';
        html += `<li class="${liClass}">${step}</li>`;
    });
    html += '</ul>';
    return html;
}

function closeModal() {
    document.getElementById('modal-chamado').style.display = 'none';
}
