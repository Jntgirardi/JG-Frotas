/**
 * RotaFácil - Javascript Auxiliar de Interface
 * Lógicas para modais de CRUD, cálculo de lucros em tempo real e utilitários.
 */

document.addEventListener('DOMContentLoaded', () => {
    inicializarCalculoLucro();
    inicializarModais();
    configurarAutoFechamentoAlertas();
    configurarFormatacaoInputs();
    configurarLoadingOverlay();
});

/**
 * Lógica para cálculo em tempo real no formulário de Viagens
 * Calcula: Lucro = Frete - (Combustível + Pedágio + Outros Custos)
 */
function inicializarCalculoLucro() {
    const inputFrete = document.getElementById('valor_frete');
    const inputCombustivel = document.getElementById('custo_combustivel');
    const inputPedagio = document.getElementById('custo_pedagio');
    const inputOutros = document.getElementById('outros_custos');
    const inputComissao = document.getElementById('comissao_motorista');
    const inputPrestacao = document.getElementById('prestacao');
    const inputImpostos = document.getElementById('impostos');
    const boxLucro = document.getElementById('lucro_preview_valor');

    const inputs = [inputFrete, inputCombustivel, inputPedagio, inputOutros, inputComissao, inputPrestacao, inputImpostos];

    // Se algum dos elementos não existir na página, cancela execução da função
    if (!inputFrete || !boxLucro) return;

    function calcular() {
        const frete = parseFloat(inputFrete.value) || 0;
        const combustivel = parseFloat(inputCombustivel.value) || 0;
        const pedagio = parseFloat(inputPedagio.value) || 0;
        const outros = parseFloat(inputOutros.value) || 0;
        const comissao = parseFloat(inputComissao.value) || 0;
        const prestacao = parseFloat(inputPrestacao.value) || 0;
        const impostos = parseFloat(inputImpostos.value) || 0;

        const lucro = frete - (combustivel + pedagio + outros + comissao + prestacao + impostos);

        // Formatação em Real (R$)
        boxLucro.textContent = lucro.toLocaleString('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        });

        const container = boxLucro.closest('.lucro-preview-box');
        if (container) {
            if (lucro < 0) {
                container.style.backgroundColor = 'var(--danger-light)';
                container.style.color = 'var(--danger)';
                container.style.borderColor = 'var(--danger)';
            } else {
                container.style.backgroundColor = 'var(--success-light)';
                container.style.color = 'var(--success)';
                container.style.borderColor = 'var(--success)';
            }
        }
    }

    inputs.forEach(input => {
        if (input) {
            input.addEventListener('input', calcular);
        }
    });

    // Executa uma vez no início caso haja valores pré-preenchidos (edição)
    calcular();
}

/**
 * Controle genérico para abrir e fechar modais com transição suave
 */
function inicializarModais() {
    // Abrir Modal
    const botoesAbrir = document.querySelectorAll('[data-open-modal]');
    botoesAbrir.forEach(btn => {
        btn.addEventListener('click', () => {
            const modalId = btn.getAttribute('data-open-modal');
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.add('show');
                document.body.style.overflow = 'hidden'; // Impede scroll do fundo
            }
        });
    });

    // Fechar Modal pelo Botão Fechar ou pelo Botão Cancelar
    const botoesFechar = document.querySelectorAll('[data-close-modal], .modal-close');
    botoesFechar.forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = btn.closest('.modal-backdrop');
            if (modal) {
                modal.classList.remove('show');
                document.body.style.overflow = '';
            }
        });
    });

    // Fechar clicando fora do modal (no fundo)
    const modais = document.querySelectorAll('.modal-backdrop');
    modais.forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('show');
                document.body.style.overflow = '';
            }
        });
    });
}

/**
 * Fecha mensagens de alerta (Flash) automaticamente após 4 segundos
 */
function configurarAutoFechamentoAlertas() {
    const alertas = document.querySelectorAll('.alert');
    alertas.forEach(alerta => {
        setTimeout(() => {
            alerta.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            alerta.style.opacity = '0';
            alerta.style.transform = 'translateX(100px)';
            setTimeout(() => {
                alerta.remove();
            }, 500);
        }, 4000);
    });
}

/**
 * Validações e formatações de entrada automáticas para ajudar o usuário de 50+ anos
 */
function configurarFormatacaoInputs() {
    // Forçar placa de caminhão em Letras Maiúsculas e no formato correto
    const inputsPlaca = document.querySelectorAll('input[name="placa"]');
    inputsPlaca.forEach(input => {
        input.addEventListener('input', (e) => {
            let val = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
            
            // Auto insere traço no formato antigo (ABC-1234) para facilitar, se o usuário digitar 7 caracteres
            if (val.length === 7 && !isNaN(val.charAt(3))) {
                val = val.substring(0, 3) + '-' + val.substring(3);
            }
            
            e.target.value = val.substring(0, 8); // Máximo 8 caracteres (Ex: ABC-1234 ou ABC1D23)
        });
    });
}

/**
 * Função utilitária para preencher formulários de edição
 * @param {string} modalId - ID do modal a ser aberto
 * @param {object} dados - Objeto contendo os dados a serem preenchidos (nome_do_campo: valor)
 */
function abrirModalEdicao(modalId, dados) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    // Percorre cada dado e tenta preencher o campo correspondente dentro do modal
    for (const campo in dados) {
        if (dados.hasOwnProperty(campo)) {
            const input = modal.querySelector(`[name="${campo}"]`);
            if (input) {
                if (input.type === 'checkbox') {
                    input.checked = !!dados[campo];
                } else if (input.tagName === 'SELECT') {
                    // Seleciona a opção
                    input.value = dados[campo].toString();
                } else {
                    input.value = dados[campo];
                }
            }
        }
    }

    // Exibe o modal
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
    
    // Dispara evento de recalculação de lucro caso seja o modal de viagem
    const inputFrete = modal.querySelector('#valor_frete');
    if (inputFrete) {
        // Dispara evento manual
        const event = new Event('input');
        inputFrete.dispatchEvent(event);
    }
}

/**
 * Controla a exibição do overlay de carregamento em cliques de links e submissões de formulário
 */
function configurarLoadingOverlay() {
    // Intercepta submits de formulários
    document.addEventListener('submit', (e) => {
        const form = e.target;
        if (form.getAttribute('target') === '_blank') return;
        
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.add('show');
        }
    });

    // Intercepta cliques em links de navegação
    document.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (link) {
            const href = link.getAttribute('href');
            const target = link.getAttribute('target');
            
            // Ignora links sem destino, hashes/âncoras, javascript triggers, links para modais ou nova aba
            if (!href || 
                href.startsWith('#') || 
                href.startsWith('javascript:') || 
                target === '_blank' ||
                link.hasAttribute('data-open-modal') ||
                link.hasAttribute('data-close-modal') ||
                link.classList.contains('modal-close')
            ) {
                return;
            }
            
            const overlay = document.getElementById('loading-overlay');
            if (overlay) {
                overlay.classList.add('show');
            }
        }
    });
}
