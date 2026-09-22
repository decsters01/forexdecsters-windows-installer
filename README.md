# forexdecsters windows installer

No seu PC, a CLI entra por SSH num VPS Linux e instala **Windows Server 2019 ServerDatacenter** (com area de trabalho).

A ISO nao esta neste repositorio. No VPS, o script baixa o [reinstall.sh](https://github.com/bin456789/reinstall) (GPL-3.0) e pede a imagem `Windows Server 2019 ServerDatacenter`. Esse nome e o que o catalogo do NTriver reconhece. A ISO e a de volume, nao a Evaluation de 180 dias. Este projeto nao ativa o Windows.

**Apaga o disco inteiro do VPS.** Use uma maquina descartavel.

## O que o VPS precisa

- KVM, x86_64, Linux (Debian ou Ubuntu). OpenVZ, LXC e ARM nao servem.
- SSH com root e senha.
- 1 GB de RAM, 25 GB de disco, um disco so.

Ative depois com uma licenca sua. Sem KMS e sem crack.

## Rodar

Com Python:

```powershell
cd "caminho\deste\projeto"
py -3 -m venv .venv
.\.venv\Scripts\activate
pip install -e ".[dev]"
forexdecsters
```

Sem Python, use o executavel:

```powershell
.\dist\forexdecsters-windows-installer.exe
```

Para gerar esse exe de novo:

```powershell
.\scripts\build_exe.ps1
```

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

`--dry-run` so mostra o que seria enviado. Nao conecta e nao apaga disco.

```powershell
forexdecsters --dry-run
```

Se a busca da ISO falhar, passe um link direto que o VPS consiga baixar:

```powershell
forexdecsters --iso "https://exemplo/arquivo.iso"
```

A edicao dentro dessa ISO tem que ser `Windows Server 2019 ServerDatacenter`.

Quando o VPS reiniciar, o SSH cai. Isso e esperado. Entre por RDP quando a instalacao terminar (`mstsc /v:IP:porta`).

## Credenciais salvas

Usuario e senha do Windows sao gravados em `installs.json`, na pasta de onde o programa foi aberto, antes do SSH. O IP ja vai com a porta RDP (`1.2.3.4:3389`). A senha SSH nao e salva. A janela so fecha quando voce pressiona Enter.

```text
ip: 1.2.3.4:3389
user: administrator
pass: senha
```

```powershell
forexdecsters list
forexdecsters show 1.2.3.4
```

## Lockout

A instalacao ja coloca `net accounts /lockoutthreshold:0` no unattend, para o Windows nao travar a conta depois de senhas erradas. Nao precisa rodar o `.bat` no primeiro boot.

Se a politica voltar: `destrave.bat` na mesma pasta, como Administrador.

Sem lockout, forca bruta no RDP fica mais facil. Use senha longa e, se der, limite o RDP por IP.

## Testes

```powershell
py -3 -m pytest
```

## Licenca

Este wrapper e MIT. O `reinstall.sh` continua GPL-3.0 e nao entra neste repositorio.
