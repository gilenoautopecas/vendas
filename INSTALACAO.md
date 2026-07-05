# GSales — Roteiro de Instalação em PC Novo (Windows)

Siga os passos na ordem. Leva em torno de 15 a 20 minutos na primeira vez.

---

## 1. Instalar o Python

1. Acesse: https://www.python.org/downloads/
2. Baixe a versão mais recente (3.13 ou superior)
3. **IMPORTANTE:** na tela de instalação, marque a opção **"Add Python to PATH"** antes de clicar em Install
4. Conclua a instalação normalmente

Para confirmar que funcionou, abra o **Prompt de Comando** e digite:
```
python --version
```
Deve aparecer algo como `Python 3.13.x`.

---

## 2. Instalar o Git

1. Acesse: https://git-scm.com/download/win
2. Baixe e instale com todas as opções padrão (só clicar em Next até o fim)

Para confirmar que funcionou:
```
git --version
```
Deve aparecer algo como `git version 2.x.x`.

---

## 3. Baixar o projeto

Abra o **Prompt de Comando** e rode:

```bat
git clone https://github.com/gilenoautopecas/vendas.git C:\projetos\vendas-main
```

A estrutura vai ficar assim:
```
C:\projetos\vendas-main\
    manage.py
    venda\
    core\
    atualizar.bat
    ...
```

---

## 4. Criar o ambiente virtual e instalar dependências

Ainda no Prompt de Comando:

```bat
cd C:\projetos\vendas-main
python -m venv venv
venv\Scripts\pip install -r requirements.txt
```

Aguarde — vai baixar e instalar os pacotes. Pode levar alguns minutos.

---

## 5. Configurar o banco de dados

```bat
venv\Scripts\python manage.py migrate
```

Isso cria o banco de dados SQLite automaticamente.

---

## 6. Criar o usuário administrador

```bat
venv\Scripts\python manage.py createsuperuser
```

Digite um nome de usuário, e-mail (pode deixar em branco) e senha quando solicitado.

---

## 7. Instalar a licença

1. Solicite o arquivo `licenca.key` pelo WhatsApp **(84) 98865-0730**
2. Cole o arquivo `licenca.key` dentro da pasta `C:\projetos\vendas-main\`

Sem esse arquivo o sistema não abre.

---

## 8. Instalar o launcher (GSales.exe)

O `GSales.exe` é o atalho que abre o sistema com um duplo clique.

### Gerar o GSales.exe

```bat
cd C:\projetos\vendas-main\launcher
build.bat
```

Quando terminar, copie o executável para a pasta raiz:

```bat
copy dist\GSales.exe C:\projetos\vendas-main\GSales.exe
```

### Criar o atalho na Área de Trabalho

1. Vá até `C:\projetos\vendas-main\`
2. Clique com o botão direito em `GSales.exe` → **Criar atalho**
3. Mova o atalho para a **Área de Trabalho**

### (Opcional) Iniciar junto com o Windows

Para o sistema já estar rodando quando o PC liga:

1. Pressione `Win + R`, digite `shell:startup` e pressione Enter
2. Cole o atalho do `GSales.exe` nessa pasta

---

## 9. Primeiro acesso — criar a empresa

1. Dê duplo clique em **GSales** na Área de Trabalho
2. O navegador abre automaticamente — faça login com o usuário criado no passo 6
3. O sistema detecta que ainda não há empresa cadastrada e abre uma tela de configuração
4. Digite o nome do seu negócio e clique em **Criar empresa e entrar**
5. Pronto — o sistema está pronto para uso

---

## 10. Configurar o agente Gdoor (sincronização de produtos)

O agente lê os produtos do Gdoor e envia para o GSales automaticamente.

### Gerar o agente_gdoor.exe

```bat
cd C:\projetos\vendas-main\agente_gdoor
build.bat
```

### Configurar

1. Execute `dist\agente_gdoor.exe` uma vez — ele cria o `config.ini` automaticamente
2. Abra o `config.ini` e preencha:
   - `isql_path` — caminho do `isql.exe` do Firebird (ex: `C:\Program Files (x86)\Firebird\Firebird_5_0\isql.exe`)
   - `db_path` — caminho do banco `.FDB` do Gdoor (ex: `C:\GDOOR Sistemas\GDOOR PRO\DATAGES.FDB`)
   - `url` — `http://127.0.0.1:8000`
   - `token` — copie do painel admin: **Empresas → clique na empresa → campo Sync token**

3. Execute novamente para testar:
```bat
agente_gdoor.exe
```
Deve aparecer: `Sincronização concluída: XXXX produtos importados.`

### Agendar execução automática

1. Abra o **Agendador de Tarefas** do Windows (pesquise na barra de tarefas)
2. Clique em **Criar Tarefa Básica**
3. Nome: `Sincronizar Gdoor`
4. Gatilho: **Diariamente** (ou de hora em hora, conforme preferir)
5. Ação: **Iniciar um programa** → selecione o `agente_gdoor.exe`
6. Conclua

---

## 11. Teste final

1. Abra o GSales pelo atalho da Área de Trabalho
2. Faça login normalmente
3. Confirme que os produtos do Gdoor aparecem em **Produtos**
4. Crie uma venda de teste

---

## Como atualizar o sistema

Sempre que houver uma atualização, basta dar duplo clique no arquivo:

```
C:\projetos\vendas-main\atualizar.bat
```

Ele vai baixar as novidades, atualizar o banco e avisar quando terminar.
**Não apaga nenhum dado.**

> Após atualizar, feche e abra o GSales novamente pelo atalho.

---

## Resumo dos arquivos importantes

| Arquivo | Onde fica | Para que serve |
|---|---|---|
| `GSales.exe` | Raiz do projeto | Abre o sistema com 1 clique |
| `licenca.key` | Raiz do projeto | Libera o acesso — não apague |
| `db.sqlite3` | Raiz do projeto | Banco de dados — **nunca apague** |
| `atualizar.bat` | Raiz do projeto | Atualiza o sistema |
| `agente_gdoor.exe` | `agente_gdoor\` | Sincroniza produtos do Gdoor |
| `config.ini` | `agente_gdoor\` | Configuração do agente |

---

## Suporte

WhatsApp: **(84) 98865-0730**
