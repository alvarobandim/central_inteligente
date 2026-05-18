# 🔒 Central Inteligente - Ecossistema Pessoal de Gestão

Olá! Bem-vindo ao repositório da **Central Inteligente**. Este é um projeto que desenvolvi para resolver dois grandes problemas do meu dia a dia em um único lugar: o controle das minhas finanças pessoais e a gestão de anotações e insights rápidos (o meu *Second Brain*).

O software foi construído usando **Python** e **Flet**, com armazenamento local seguro em **SQLite**. Ele roda de forma 100% offline e independente.

---

## Funcionalidades do Sistema

### 1. Sistema de Cofre (Autenticação Segura)
* Cadastro e Login de múltiplos usuários com chaves de acesso criptografadas (Hash).
* **Modo Cofre Hardcore:** Como os dados ficam guardados apenas na máquina local de forma segura, não há recuperação de senha mágica. Perdeu a chave, perdeu o acesso!

### 2. Controle de Inteligência Financeira
* Lançamento rápido de **Receitas** e **Despesas**.
* Cálculo automático e dinâmico de totais e do Balanço Geral na tela.
* **Inline Swap para Categorias:** Criação dinâmica de novas categorias diretamente na interface, sem abrir pop-ups irritantes.
* **Gráficos Duplos (Apple Storage Bar Style):** Barras coloridas horizontais construídas do zero que mostram a distribuição percentual exata de receitas e despesas.
* **Exportação para Excel/CSV:** Um botão dinâmico que gera um arquivo formatado para o padrão Excel Brasileiro.

### 3. Second Brain (Central de Insights)
* **Sistema de Chips para Múltiplas Tags:** Etiquetas clicáveis (estilo Notion/Obsidian) para selecionar ou desmarcar várias tags de forma fluida.
* **Edição Inline de Notas:** O texto estático se transforma em campos editáveis diretamente no cartão da anotação, garantindo uma UX super fluida.
* **Busca Híbrida Inteligente:** A pesquisa faz uma varredura com `LIKE` e `OR` no banco de dados e encontra a nota pesquisando por Título, Conteúdo ou Tags simultaneamente.

---

## Tecnologias Utilizadas
* **Python 3+**
* **Flet** (Framework de interface gráfica baseado em Flutter)
* **SQLite** (Banco de dados relacional embutido)
* **PyInstaller** (Para empacotamento em formato `.exe` autônomo)

---

## Aprendizados de Desenvolvimento (Nota Pessoal)
* **Late Binding em loops:** Descobri o comportamento do Python ao passar variáveis dentro de funções `lambda` num laço `for`. Tive que criar `Closures` para isolar o escopo do ID de cada nota e evitar bugs de exclusão da última nota da lista!
* **UX sobre UI:** Trocar dropdowns de multi-seleção por componentes visuais clicáveis (*Chips*) mudou completamente a velocidade de utilização do app.
* **Workarounds de Compilação:** Resolvi o crash de `sys.stdout` gerado pelo servidor interno (Uvicorn) do Flet ao tentar usar o `--noconsole` do PyInstaller, redirecionando os logs para o `os.devnull`.

---
Feito com muito café e persistência! Se achou esse projeto interessante, deixa uma ⭐️ no repositório!