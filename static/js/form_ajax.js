document.addEventListener('DOMContentLoaded', () => {
    const formularios = document.querySelectorAll('form.form-ajax');

    formularios.forEach(form => {
        // 🔒 Variável de controle local para cada formulário

        let submetendo = false;       

        form.addEventListener('submit', async function(event) {
            event.preventDefault();
            
            // 🛑 Se já estiver enviando, interrompe imediatamente a execução
            if (submetendo) return;
            
            // Ativa a trava
            submetendo = true;            
            
            // ADICIONA O BOTÃO CLICADO AO POST
            const formData = new FormData(form);

            // BOTÃO QUE DISPAROU O SUBMIT
            const botaoSubmit = event.submitter;

            if (botaoSubmit) {

                formData.set(
                    botaoSubmit.name,
                    botaoSubmit.value
                );
            }

            Swal.fire({
                title: 'Processando...',
                text: 'Por favor, aguarde.',
                allowOutsideClick: false,
                didOpen: () => { Swal.showLoading(); }
            });

            try {
                const response = await fetch(form.action || window.location.href, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'Accept': 'application/json',
                        'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                const textResponse = await response.text();               
                
                let dados;
                try {
                    dados = JSON.parse(textResponse);
                    console.log('Resposta parseada (JSON):', dados);
                } catch (e) {
                    console.error('Falha ao fazer parse do JSON:', e);
                    throw new Error('Resposta não é um JSON válido');
                }

                if (response.ok && dados.status === 'sucesso') {
                    Swal.close();
                    await Swal.fire({
                        icon: 'success',
                        title: dados.titulo,
                        html: dados.mensagem,
                        confirmButtonText: 'OK'
                    });
                    
                    // ==========================================
                    // BOTÃO "SALVAR E NOVA DESPESA"
                    // ==========================================
                    if (dados.acao === 'salvar_novo') {

                        // PRESERVA ALGUNS CAMPOS
                        const data =
                            document.getElementById('id_data')?.value;

                        const conta =
                            document.getElementById('id_conta')?.value;

                        const cartao =
                            document.getElementById('id_cartao')?.value;

                        // LIMPA O FORM
                        form.reset();

                        // RESTAURA CAMPOS IMPORTANTES
                        if (data)
                            document.getElementById('id_data').value = data;

                        if (conta)
                            document.getElementById('id_conta').value = conta;

                        if (cartao)
                            document.getElementById('id_cartao').value = cartao;

                        // FOCO NO PRIMEIRO CAMPO
                        document.getElementById('id_descricao')?.focus();

                        // 🔓 LIBERA NOVO ENVIO
                        submetendo = false;
                    }
                    
                    // ==========================================
                    // BOTÃO "SALVAR DESPESA"
                    // ==========================================
                    else {

                        window.location.href =
                            dados.redirect_url ||
                            form.action ||
                            window.location.href;
                    }
                }

                else {
                    Swal.close();
                    // 🔓 Destrava se houver erro de validação (para o usuário corrigir e tentar de novo)
                    submetendo = false; 

                    await Swal.fire({
                        icon: 'error',
                        title: dados.titulo || 'Ops! Algo deu errado',
                        html: dados.mensagem || 'Verifique os dados informados.',
                        confirmButtonText: 'Tentar novamente'
                    });
                }
                
            } catch (error) {
                console.error('ERRO NO CATCH:', error);
                Swal.close();
                // 🔓 Destrava se houver erro de conexão/servidor
                submetendo = false; 

                await Swal.fire({
                    icon: 'error',
                    title: 'Erro de Conexão',
                    text: `Erro: ${error.message}`,
                    confirmButtonText: 'Fechar'
                });
            }
        });
    });
});