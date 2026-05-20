document.addEventListener('DOMContentLoaded', function() {
    const categoriaSelect = document.getElementById('categoria');
    const problemaSelect = document.getElementById('problema');
    const detalhesTextarea = document.getElementById('detalhes');
    const formNovoChamado = document.getElementById('form-novo-chamado');

    const opcoesProblema = {
        'MANUTENÇÃO ELÉTRICA': [
            'SOBRECARGA ELÉTRICA', 'FALHA DE ILUMINAÇÃO', 'PROBLEMAS/FALHA DE GERADOR', 
            'PROBLEMAS COM PÁRA-RAIOS', 'PROBELMAS COM TOAMADAS/DISJUNTORES', 'OUTRO'
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
            
            // Validate limits of image files
            const imagensInput = document.getElementById('imagens');
            if (imagensInput.files.length > 3) {
                alert('Você pode enviar no máximo 3 imagens.');
                return;
            }

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

function visualizarChamado(id) {
    // Busca detalhes do chamado na API
    fetch(`/api/chamados/${id}`)
        .then(res => res.json())
        .then(data => {
            const modal = document.getElementById('modal-chamado');
            document.getElementById('modal-titulo').innerText = `Chamado #${data.id}`;
            
            // Build timeline
            const timelineHTML = buildTimeline(data.status);
            document.getElementById('timeline-container').innerHTML = timelineHTML;
            
            // Build content
            document.getElementById('modal-detalhes-conteudo').innerHTML = `
                <p><strong>Categoria:</strong> ${data.categoria}</p>
            `;
            
            modal.style.display = 'block';
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
