// Responsável exclusivamente por:
// 1. Detectar a forma de pagamento;
// 2. Abrir o modal quando for cartão;
// 3. Limpar cartão/parcela quando não for cartão;
// 4. Validar o fechamento do modal.


document.addEventListener("DOMContentLoaded", function () {

    // =========================================================================
    // MODAL CARTÃO
    // =========================================================================

    const modalElement = document.getElementById("modalCartao");
    const campoPagamento = document.getElementById("id_forma_pagamento");

    // Executa somente se os elementos existirem na página
    if (!modalElement || !campoPagamento) {
        return;
    }

    const campoCartao = document.getElementById("id_cartao");
    const campoParcela = document.getElementById("id_parcela");

    // Inicializa o Modal do Bootstrap 5
    const bootstrapModal = new bootstrap.Modal(modalElement);

    // =========================================================================
    // LÓGICA DE EXIBIÇÃO DO MODAL
    // =========================================================================

    function verificarEExibirModal() {
        if (campoPagamento.value === "CARTAO") {
            // Abre o modal se for cartão e o campo de cartão não estiver preenchido
            if (campoCartao && !campoCartao.value) {
                bootstrapModal.show();
            }
        } else {
            // Se não for cartão, limpa os campos relacionados
            if (campoCartao) {
                campoCartao.value = "";
            }

            if (campoParcela) {
                campoParcela.value = "1";
            }
        }
    }

    // 1. Executa no carregamento da página (Crucial para a tela de EDIÇÃO)
    verificarEExibirModal();

    // 2. Executa sempre que a forma de pagamento for alterada
    campoPagamento.addEventListener("change", function () {
        if (this.value === "CARTAO") {
            bootstrapModal.show();
        } else {
            if (campoCartao) campoCartao.value = "";
            if (campoParcela) campoParcela.value = "1";
        }
    });

    // =========================================================================
    // FECHAMENTO DO MODAL INCOMPLETO
    // =========================================================================

    function tratarFechamentoIncompleto() {
        // Se escolheu cartão, mas fechar sem selecionar um cartão válido
        if (
            campoPagamento.value === "CARTAO" &&
            campoCartao &&
            !campoCartao.value
        ) {
            alert(
                "Você precisa selecionar um cartão ou mudar a forma de pagamento."
            );

            // Redefine para DINHEIRO (evita valor nulo/vazio que quebra o Django)
            campoPagamento.value = "DINHEIRO";

            if (campoParcela) {
                campoParcela.value = "1";
            }
        }
    }

    // Trata o fechamento nos botões de fechar/cancelar
    const btnFecharX = document.getElementById("btnFecharModalX");
    if (btnFecharX) {
        btnFecharX.addEventListener("click", tratarFechamentoIncompleto);
    }

    const btnCancelar = document.getElementById("btnCancelarModal");
    if (btnCancelar) {
        btnCancelar.addEventListener("click", tratarFechamentoIncompleto);
    }

    // Captura também o evento nativo de quando o modal é ocultado (ex: clicar fora)
    modalElement.addEventListener("hidden.bs.modal", tratarFechamentoIncompleto);
});