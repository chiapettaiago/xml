# Validador e Corretor de Arquivos XML TISS

Este é um projeto desenvolvido para validar e corrigir arquivos XML do padrão TISS (Troca de Informação de Saúde Suplementar). Com esta ferramenta, você pode:

1. **Validar XML contra o Esquema XSD (XML Schema)**: O projeto permite que você valide um arquivo XML modificado contra o esquema XSD correspondente à versão do TISS identificada no arquivo.

2. **Corrigir Erros Comuns no XML**: A ferramenta analisa o arquivo XML e realiza as seguintes correções automáticas:
   - Corrige números com mais de duas casas decimais, arredondando-os para duas casas.
   - Atualiza o valor total geral (tag `<valorTotalGeral>`) para corresponder à soma dos valores totais das guias nas versões abaixo do `TISS 4.00.00`.

3. **Identificar Linhas Alteradas**: Ao fazer a correção do XML, o projeto identifica as linhas que foram alteradas e as exibe em uma página de visualização do XML modificado.

4. **Extrair Informações Relevantes**: O projeto extrai informações importantes do arquivo XML, como:
   - Versão do TISS
   - Número de guias
   - Valor total
   - Número do lote

5. **Regras Específicas**: Regras específicas para tratamento de acordo com a versão TISS detectada.

## Funcionalidades 
- Validar XML contra o Esquema XSD (XML Schema)
- Arredonda tags com 4 casas decimais para utilizar apenas duas
- Soma os valores e os arredonda no somatório para evitar erros.


## Tecnologias Utilizadas

- Python
- Flask (framework web)
- lxml (biblioteca para manipulação de XML)
- difflib (biblioteca para comparação de strings)
- MVC (Model-View-Controller) para melhor organização e manutenção de código

## Histórico de atualizações:
14/05/2024:
- Correção de bugs
- Sistema agora também traz informações sobre operadora e tipo de transação do XML.

13/05/2024:
- Adicionado suporte a todas as versões do tiss na verificação de arredondamento
- Melhorias no padão MVC
- Melhorias na leitura e organização do código.
- Imagem docker atualizada do Ubuntu 22.04 LTS para o Ubuntu 24.04 LTS

## Instalação e Utilização

Para utilizar o validador, siga os passos abaixo:

1. Clone o repositório para sua máquina local.
2. Instale as dependências necessárias utilizando `pip install -r requirements.txt`.
3. Execute o validador com o comando `python app.py`.

Ou utilize a imagem docker disponível no Docker Hub:

```
docker pull chiapettaiago/xml:latest
```

Para executar use o seguinte comando:

```
docker run -p 5000:5000 chiapettaiago/xml:latest
```

Após isso basta digitar http://localhost:5000 no seu navegador e o validador xml vai abrir.



