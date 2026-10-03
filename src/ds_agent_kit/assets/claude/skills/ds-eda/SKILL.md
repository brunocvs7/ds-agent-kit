---
name: ds-eda
description: Faz análise exploratória (EDA) de um dataset em data/ seguindo as convenções do template — notebook numerado em notebooks/, figuras em reports/figures/. Use quando o usuário pedir EDA, perfil dos dados ou exploração inicial.
---

# EDA

1. Identifique o arquivo em `data/raw/` ou `data/processed/` (pergunte se houver mais de um).
2. Garanta as dependências: `uv add --dev pandas matplotlib ipykernel` se ainda não existirem.
3. Crie `notebooks/NN-<iniciais>-eda-<dataset>.ipynb` (NN = próximo número livre) contendo:
   - shape, dtypes, `% de nulos` por coluna, cardinalidade;
   - estatísticas descritivas e distribuição das principais variáveis;
   - correlações e possíveis vazamentos em relação ao target (se houver um);
   - figuras salvas em `reports/figures/`.
4. Funções reutilizáveis vão para `src/<pacote>/` com teste em `tests/` — não deixe lógica só no notebook.
5. Termine com um resumo de 5-10 bullets dos principais achados e próximos passos.
