# Agente Gdoor

Script que roda na máquina onde o Gdoor está instalado e envia os produtos
para o sistema web central, via API autenticada por token da empresa.

## Gerar o `.exe` (precisa ser feito em uma máquina Windows)

PyInstaller não cross-compila — não dá pra gerar `.exe` a partir do macOS/Linux.
Rode isto em um Windows (pode ser o próprio PC do cliente ou uma VM):

```
cd agente_gdoor
build.bat
```

Isso instala as dependências e gera `dist\agente_gdoor.exe`.

## Instalar no cliente

1. Copie `dist\agente_gdoor.exe` para uma pasta na máquina do cliente
   (ex: `C:\AgenteGdoor\`).
2. Copie `config.ini.example` para a mesma pasta e renomeie para `config.ini`
   (ou apenas rode o `.exe` uma vez — ele cria o `config.ini` automaticamente
   se não existir, e te avisa onde editar).
3. Edite o `config.ini`:
   - `isql_path` / `db_path`: caminho do `isql.exe` e do `.FDB` do Gdoor.
   - `url`: endereço do sistema web central.
   - `token`: token de sincronização da empresa (gerado automaticamente ao
     criar a `Empresa` no `/admin/` do Django — campo `sync_token`).
4. Rode `agente_gdoor.exe` manualmente pra testar.

## Rodar automaticamente

Use o Agendador de Tarefas do Windows (Task Scheduler) para rodar o
`.exe` periodicamente (ex: a cada 1h), ou crie um serviço com `nssm`
se quiser rodar em segundo plano sem login de usuário.

## Rodar sem empacotar (modo dev, em qualquer SO com Python)

```
pip install -r requirements.txt
python agente.py
```
