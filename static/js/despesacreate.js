

document.addEventListener("DOMContentLoaded", function () {
    
    // =========================================================================
    // MODAL CARTÃO (Executa apenas na tela de criação se o modal existir)
    // =========================================================================
    const modalElement = document.getElementById("modalCartao");
    const campoPagamento = document.getElementById("id_forma_pagamento");

    if (modalElement && campoPagamento) {
        const campoCartao = document.getElementById("id_cartao");
        const campoParcela = document.getElementById("id_parcela");
        
        // Inicializa o objeto do Modal do Bootstrap 5 com segurança
        const bootstrapModal = new bootstrap.Modal(modalElement);

        // Dispara o evento sempre que o usuário muda a Forma de Pagamento
        campoPagamento.addEventListener("change", function () {
            if (this.value === "CARTAO") {
                bootstrapModal.show();
            } else {
                campoCartao.value = "";
                campoParcela.value = "1";
            }
        });

        // Trata o fechamento do modal sem seleção
        function tratarFechamentoIncompleto() {
            if (campoPagamento.value === "CARTAO" && !campoCartao.value) {
                alert("Você precisa selecionar um cartão ou mudar a forma de pagamento.");
                campoPagamento.value = ""; 
            }
        }

        const btnFecharX = document.getElementById("btnFecharModalX");
        const btnCancelar = document.getElementById("btnCancelarModal");

        if (btnFecharX) btnFecharX.addEventListener("click", tratarFechamentoIncompleto);
        if (btnCancelar) btnCancelar.addEventListener("click", tratarFechamentoIncompleto);
    }
   
   
    // =========================================================================
    // FILTRO GRUPO → ESPÉCIE (Executa em qualquer tela se as comboboxes existirem)
    // =========================================================================
    const grupo = document.getElementById("id_grupo");
    const especie = document.getElementById("id_especie");

    if (grupo && especie) {
        grupo.addEventListener("change", function () {
            const grupoId = this.value;

            especie.innerHTML = '<option value="">Selecione uma espécie</option>';

            if (!grupoId) return;

            fetch(`/buscar-especies/?grupo_id=${grupoId}`)
                .then(response => response.json())
                .then(data => {
                    data.forEach(item => {
                        let option = document.createElement("option");
                        option.value = item.id;
                        option.textContent = item.nomeEspecie;
                        especie.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error("Erro ao carregar espécies:", error);
                });
        }); 
    }

});