# Forex Decsters

A **Forex Decsters** gastou tempo e dinheiro demais com licenca de Windows e com instalador de terceiro. Agora o instalador e nosso.

Este programa entra por SSH num VPS Linux e instala **Windows Server 2019 ServerDatacenter**, com area de trabalho, usuario e senha que voce escolhe. Sem TinyInstaller. A ISO nao fica neste repositorio: no VPS, o script pede a imagem `Windows Server 2019 ServerDatacenter` pelo [reinstall.sh](https://github.com/bin456789/reinstall). Nao ativa o Windows, nao usa KMS e nao usa crack. A licenca continua sua.

**Apaga o disco inteiro do VPS.** Use uma maquina descartavel.

## Download

Executavel portatil. Nao precisa de Python.

[Baixar forexdecsters-windows-installer.exe](https://github.com/decsters01/forexdecsters-windows-installer/releases/download/v0.1.0/forexdecsters-windows-installer.exe)

Abra o arquivo. A janela so fecha quando voce pressiona Enter.

## O que o VPS precisa

- KVM, x86_64, Linux (Debian ou Ubuntu). OpenVZ, LXC e ARM nao servem.
- SSH com root e senha.
- 1 GB de RAM, 25 GB de disco, um disco so.

## O que a tela pede

1. IP do VPS.
2. Porta SSH. Enter deixa `22`.
3. Usuario SSH. Enter deixa `root`.
4. Senha SSH. Nao e salva.
5. Porta RDP. Enter deixa `3389`.
6. Usuario Windows. Enter deixa `Administrator`. `Random` gera um nome `fd` + 8 caracteres. Ou um nome ate 20, sem `/ \ [ ] : | < > + = ; , ? * % @`.
7. Senha Windows. Enter gera uma senha aleatoria e mostra na tela. Ou digite a sua: minimo 8, com maiuscula, minuscula e numero, sem o nome do usuario.
8. URL da ISO. Enter usa a busca automatica.
9. O IP de novo, igual ao primeiro, e `Install`.

Quando o VPS reiniciar, o SSH cai. Isso e esperado. Entre por RDP quando a instalacao terminar.

## Credenciais salvas

Usuario e senha do Windows vao para `installs.json`, na pasta de onde o programa foi aberto, antes do SSH. O IP ja vai com a porta RDP.

```text
ip: 1.2.3.4:3389
user: administrator
pass: senha
```

## Lockout

A instalacao ja coloca `net accounts /lockoutthreshold:0` no unattend, para o Windows nao travar a conta depois de senhas erradas.

Se a politica voltar, rode `destrave.bat` na mesma pasta, como Administrador. Sem lockout, forca bruta no RDP fica mais facil. Use senha longa e, se der, limite o RDP por IP.

## Quem for desenvolver

```powershell
py -3 -m venv .venv
.\.venv\Scripts\activate
pip install -e ".[dev]"
py -3 -m pytest
.\scripts\build_exe.ps1
```

`--dry-run` so mostra o que seria enviado. Nao conecta e nao apaga disco.

## Licenca

Este instalador e MIT. O `reinstall.sh` continua GPL-3.0 e nao entra neste repositorio.
