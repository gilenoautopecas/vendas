# GSales Launcher

Abre o sistema com um duplo clique — sem terminal visível, sem abrir navegador manualmente.

## Gerar o GSales.exe (fazer no Windows)

```
cd launcher
build.bat
```

Gera `dist\GSales.exe`.

## Instalar no cliente

1. Copie `dist\GSales.exe` para a pasta raiz do projeto (onde está o `manage.py`):
   ```
   C:\Projetos\vendas-main\GSales.exe
   ```

2. Clique com o botão direito em `GSales.exe` → **Criar atalho**

3. Mova o atalho para a **Área de Trabalho** e renomeie para "GSales"

4. (Opcional) Para iniciar junto com o Windows:
   - Pressione `Win + R`, digite `shell:startup`, Enter
   - Cole o atalho nessa pasta

## Como funciona

- Duplo clique no atalho → servidor sobe → navegador abre em `http://127.0.0.1:8000`
- Se o servidor já estiver rodando (ex: iniciou com o Windows), apenas abre o navegador
- Sem janela preta, sem precisar abrir o navegador manualmente

## Ícone personalizado

Coloque um arquivo `launcher.ico` na pasta `launcher/` antes de rodar o `build.bat`.
Descomente a linha com `--icon=launcher.ico` no `build.bat`.
Conversores online: convertio.co (PNG → ICO)
