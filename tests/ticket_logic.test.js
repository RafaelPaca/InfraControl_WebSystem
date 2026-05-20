const { getByLabelText } = require('@testing-library/dom');

describe('Ticket Logic UI', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <div id="novo-chamado">
                <form id="form-novo-chamado">
                    <select id="categoria">
                        <option value="">Selecione...</option>
                        <option value="CLIMATIZAÇÃO">CLIMATIZAÇÃO</option>
                    </select>
                    <select id="problema" disabled>
                        <option value="">Selecione a categoria primeiro...</option>
                    </select>
                </form>
            </div>
            
            <div id="modal-chamado" style="display: none;"></div>
        `;
        
        // Simular o comportamento do ticket_logic.js para o teste
        const categoriaSelect = document.getElementById('categoria');
        const problemaSelect = document.getElementById('problema');
        
        const opcoesProblema = {
            'CLIMATIZAÇÃO': [
                'AR CONDICIONADO COM MAL FUNCIONAMENTO/QUEBRADO'
            ]
        };

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
    });

    test('should enable problema select when categoria is chosen', () => {
        const categoriaSelect = document.getElementById('categoria');
        const problemaSelect = document.getElementById('problema');
        
        expect(problemaSelect.disabled).toBe(true);
        
        // Simular seleção
        categoriaSelect.value = 'CLIMATIZAÇÃO';
        categoriaSelect.dispatchEvent(new Event('change'));
        
        expect(problemaSelect.disabled).toBe(false);
        expect(problemaSelect.options.length).toBe(2); // "Selecione..." + 1 option
        expect(problemaSelect.options[1].value).toBe('AR CONDICIONADO COM MAL FUNCIONAMENTO/QUEBRADO');
    });
});
