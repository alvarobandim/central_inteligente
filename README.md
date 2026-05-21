# Central Inteligente - ERP & Produtividade Integrada

Plataforma unificada desenvolvida em Python corporativo utilizando o framework reativo Flet para entrega de interfaces ricas (Rich Interfaces) e persistência de dados local segura.

## Arquitetura da Camada de Tarefas (Kanban)

* **UX sob Demanda:** Arquitetura limpa onde ferramentas de mutação de estado (edição e exclusão) são expostas dinamicamente apenas via eventos locais de interação (clique/on_click).
* **Camada de Validação Estrita:** Captura automatizada de strings, aplicação de máscaras dinâmicas de formatação de dados de data e validação Server-Side baseada em Expressões Regulares (Regex).
* **Indicadores de Status Dinâmicos:** Cálculo reativo de datas comparadas com o carimbo de tempo da máquina atual, sinalizando tarefas em conformidade, em iminência de vencimento ou em atraso severo.
* **Viewport Reset Mechanism:** Arquitetura à prova de cache reativo de listas onde os nós filhos são reestruturados de forma imutável em tempo de execução para garantir integridade na classificação.

## Instruções para Inicialização do Ambiente

Certifique-se de ter o Python 3.10+ instalado no ambiente operacional.

1. Clone o repositório remoto:
git clone https://github.com/alvarobandim/central_inteligente
cd central_inteligente

2. Inicialize e ative o ambiente isolado do Python:
python -m venv .venv

# Windows Environment:
.\.venv\Scripts\Activate.ps1

# Unix Environment:
source .venv/bin/activate

3. Instale os pacotes de dependências mapeados:
pip install flet

4. Execute o ponto de entrada da aplicação:
python main.py