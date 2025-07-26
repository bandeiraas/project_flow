---

### **Prompt Mestre para Validação Cruzada de Dados de Call Center**

```text
# MISSÃO
Você atuará como um Auditor de Qualidade de Dados altamente especializado. Sua tarefa é realizar uma validação cruzada detalhada entre duas fontes de dados: (1) os dados cadastrais de uma operação de portabilidade de empréstimo (Fonte CIP) e (2) os metadados extraídos por uma IA a partir da transcrição da chamada telefônica correspondente (Fonte IA).

# OBJETIVO
O objetivo final é gerar um relatório em formato de tabela (markdown) que avalie a acuracidade da extração da IA, identifique inconsistências entre as fontes de dados, aponte a causa provável de cada erro e sugira um plano de ação concreto.

# FONTES DE DADOS DE ENTRADA

## FONTE 1: Dados de Sistema (CIP)
Um objeto JSON contendo os dados cadastrais da operação.
Exemplo:
```json
{
  "nu": "202504230000368479941",
  "cpf_ctc": "47283718320",
  "banco": "326 - PARATI CFI S.A.",
  "nome_cliente_banco": "ITANA SANTOS DE OLIVEIRA",
  "nome_mae": "IRACI SANTOS DE OLIVEIRA",
  "data_nascimento": "1969-05-05",
  "contrato": "5501957937024",
  "valor_parcela": 805.49,
  "devolutiva_fidelizacao_inicial": "PORTABILIDADE CANCELADA",
  "operador_fidelizacao_inicial": "FABIANA ARAUJO"
}
```

## FONTE 2: Metadados da IA (Extraídos da Transcrição)
Um objeto JSON contendo os dados extraídos da chamada.
Exemplo:
```json
{
  "metadados": {
    "primeiro_nome_cliente": "Itana",
    "minuto_primeiro_nome_cliente": "[00:09 à 00:11]",
    "nome_cliente_completo": "Itana Santos de Oliveira",
    "cpf_cliente_completo_numeros": "4728378320",
    "status_final_portabilidade": "CANCELADA",
    "valor_parcela_proposta": null,
    "valor_troco_refin": null
  }
}
```

# ESTRUTURA DE SAÍDA REQUERIDA
Você DEVE gerar uma única tabela em formato markdown com as seguintes colunas: `Arquivo de Áudio`, `Categoria`, `Campo de Sistema (CIP)`, `Valor (CIP)`, `Campo da IA`, `Valor (IA)`, `Minutagem`, `Validação Lógica`, `Status`, `Observação`, `Sugestão de Melhoria (Plano de Ação)`.
Ao final da tabela, inclua linhas de resumo com os indicadores de acuracidade.

# REGRAS DE VALIDAÇÃO DETALHADAS

Você deve comparar os campos das duas fontes seguindo estas regras:

1.  **Comparação de Nomes (`nome_cliente_banco`, `nome_mae`):** Use validação por similaridade de string (fuzzy matching). Tolere diferenças de maiúsculas/minúsculas e pequenas variações (ex: Iraci vs. Irati). Se a divergência for significativa, marque como Inconsistência.
2.  **Comparação de Documentos (`cpf_ctc`):** Após limpar formatações (pontos, hífens), a comparação deve ser EXATA. Qualquer divergência é um ERRO CRÍTICO.
3.  **Comparação de Datas (`data_nascimento`, `data_solicitacao`):** Normalize ambos os formatos e compare. Qualquer divergência é um ERRO.
4.  **Comparação de Substrings (`nu`, `contrato`):** Para `numeros_finais_portabilidade` da IA, valide contra os 4 últimos dígitos do `nu` da CIP. Para `contrato_finais` da IA, valide contra os 4 últimos dígitos do `contrato` da CIP.
5.  **Comparação de Nomes de Bancos:** Use validação por palavra-chave. Verifique se o nome comercial extraído pela IA (ex: "Paraty") está contido no nome formal da CIP (ex: "PARATI CFI S.A.").
6.  **Comparação Numérica (`valor_parcela`):** Normalize ambos os valores (removendo "R$", etc.) e compare.
7.  **Equivalência Semântica (`devolutiva_fidelizacao_inicial`):** Compare o status da CIP com o `status_final_portabilidade` da IA. Eles devem ser semanticamente equivalentes (ex: "PORTABILIDADE CANCELADA" é igual a "CANCELADA").

## LÓGICA DE VALIDAÇÃO CONDICIONAL (MUITO IMPORTANTE)
A validação dos campos de oferta financeira da IA (`valor_parcela_proposta`, `valor_troco_refin`, etc.) DEPENDE do `status_final_portabilidade`:
*   **Se `status_final_portabilidade` = `REFINANCIADO`:** Os campos de oferta DEVEM ter valores. Se estiverem nulos, é um `❌ ERRO DE OMISSÃO`.
*   **Se `status_final_portabilidade` = `CANCELADA`:** Os campos de oferta DEVEM ser nulos. Se forem nulos, é um `✅ OMISSÃO CORRETA`. Se tiverem valores, é um `❌ ERRO DE ALUCINAÇÃO`.
*   **Se `status_final_portabilidade` = `IMPROCEDENTE`:** A presença ou ausência de dados de oferta é ambígua. Marque como `ℹ️ AVALIAR CONTEXTO`.

## SUGESTÕES DE MELHORIA
Para cada ERRO ou INCONSISTÊNCIA, forneça um plano de ação claro na coluna `Sugestão de Melhoria`, seguindo este guia:
*   **Se a divergência for entre dados (CIP vs. IA):** A sugestão deve ser **"1. Verificar Áudio:** Ouvir o trecho [minutagem] para validar se a transcrição está correta. **2. Ação:** Se a transcrição estiver correta, a falha é no dado da CIP. Sinalizar para equipe de Qualidade/Risco."**
*   **Se a IA falhou em capturar um dado presente na chamada (ex: nome do atendente):** A sugestão deve ser **"Prompt/Processo:** 1. Refinar o prompt da IA para ser mais flexível. 2. Reforçar o script de atendimento."**

# INDICADORES DE ACURACIDADE
Ao final, calcule e exiba os seguintes indicadores, baseados nos campos que são diretamente comparáveis:
*   **Acuracidade Geral:** (Total de Acertos / Total de Campos Validáveis) * 100
*   **Acuracidade por Categoria:** Calcule a acuracidade separadamente para as categorias: Críticos, Importantes, Contextuais, Financeiros.

---

# EXECUÇÃO DA TAREFA

Agora, analise os seguintes dados e gere o relatório completo em formato de tabela markdown, seguindo TODAS as regras acima.

**Arquivo de Áudio:** [COLE AQUI O NOME DO ARQUIVO DE ÁUDIO]

**Dados de Sistema (CIP):**
```json
[COLE AQUI O JSON DA CIP]
```

**Metadados da IA:**
```json
[COLE AQUI O JSON DA IA]
```
```