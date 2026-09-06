// Responsável exclusivamente por:

// 1. Detectar alteração do grupo;
// 2. Buscar as espécies via AJAX;
// 3. Preencher a combobox de espécie;
// 4. Tratar erro da requisição.


document.addEventListener("DOMContentLoaded", function () {

    // =========================================================================
    // FILTRO GRUPO → ESPÉCIE
    // =========================================================================

    const grupo = document.getElementById("id_grupo");
    const especie = document.getElementById("id_especie");

    // Executa somente se os dois campos existirem
    if (!grupo || !especie) {
        return;
    }

    // =========================================================================
    // ALTERAÇÃO DO GRUPO
    // =========================================================================

    grupo.addEventListener("change", function () {

        const grupoId = this.value;

        // Limpa as espécies atuais
        especie.innerHTML =
            '<option value="">Selecione uma espécie</option>';

        // Se nenhum grupo foi selecionado, encerra
        if (!grupoId) {
            return;
        }

        // =========================================================================
        // BUSCA AS ESPÉCIES NO DJANGO
        // =========================================================================

        fetch(`/buscar-especies/?grupo_id=${grupoId}`)
            .then(response => {

                // Verifica se o Django retornou HTTP 200
                if (!response.ok) {
                    throw new Error(
                        `Erro HTTP: ${response.status}`
                    );
                }

                return response.json();
            })

            .then(data => {

                // Preenche a combobox de espécies
                data.forEach(item => {

                    const option = document.createElement("option");

                    option.value = item.id;
                    option.textContent = item.nomeEspecie;

                    especie.appendChild(option);
                });
            })

            .catch(error => {

                console.error(
                    "Erro ao carregar espécies:",
                    error
                );
            });

    });

});

