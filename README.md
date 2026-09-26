# SoundSwitch Plugin for Flow Launcher 🎧🎙️

Controle e alterne seus dispositivos de áudio, microfone, perfis e estado de mudo diretamente pelo **[Flow Launcher](https://www.flowlauncher.com/)** utilizando o **[SoundSwitch](https://soundswitch.aaflalo.me/)**.

![Flow Launcher SoundSwitch](Images/icon.png)

---

## 🚀 Funcionalidades

- **🔈 Alternar Reprodução (Playback)**: Alterne instantaneamente entre os dispositivos de saída de som configurados (fones de ouvido, caixas de som, headset, etc.).
- **🎙️ Alternar Gravação (Recording)**: Alterne entre microfones configurados com um simples toque de tecla.
- **🔇 Controle de Mudo (Microphone Mute)**: Ative ou desative o mudo do microfone com feedback visual imediato.
- **🎧 Perfis de Áudio (Profiles)**: Liste e ative os perfis definidos no SoundSwitch com indicação do perfil atualmente ativo.
- **📋 Dispositivos Configurados**: Visualize todos os dispositivos de entrada e saída selecionados no SoundSwitch com marcação visual do dispositivo em uso.
- **⚙️ Configurações Rápidas**: Atalho direto para abrir a tela de configurações do SoundSwitch.
- **🔍 Busca Inteligente**: Suporte a atalhos rápidos e filtros por palavra-chave (`play`, `rec`, `mute`, `profile`, `devices`, `settings`).
- **⚡ Sem Dependências Externas Obrigatórias**: Acompanha biblioteca FlowLauncher embutida com suporte nativo a UTF-8 no Windows, funcionando out-of-the-box.

---

## ⌨️ Como Usar

A palavra-chave padrão é **`ss`**.

Basta abrir o Flow Launcher (<kbd>Alt</kbd> + <kbd>Espaço</kbd>) e digitar:

```text
ss
```

Você verá o painel com as opções de reprodução, microfone, mute, perfis e configurações.

### Atalhos e Subcomandos

| Comando | Descrição |
|---|---|
| `ss` | Exibe o menu principal com status em tempo real de reprodução, gravação e mute |
| `ss play` (ou `ss saida`) | Mostra o card de alternância de áudio e lista de dispositivos de saída |
| `ss rec` (ou `ss mic`) | Mostra o card de alternância de microfone e lista de dispositivos de entrada |
| `ss mute` (ou `ss mudo`) | Alterna o mudo do microfone |
| `ss profile` (ou `ss p`) | Lista e filtra os perfis de áudio configurados |
| `ss devices` (ou `ss dev`) | Lista todos os dispositivos cadastrados no SoundSwitch |
| `ss settings` (ou `ss config`) | Abre a janela de preferências do SoundSwitch |

---

## 📦 Requisitos

1. **[Flow Launcher](https://www.flowlauncher.com/)** (v1.10+)
2. **[SoundSwitch](https://soundswitch.aaflalo.me/)** (v6.0+) instalado no Windows
3. **Python 3.8+** instalado no sistema

---

## 🛠️ Instalação

### Instalação Manual
1. Baixe ou clone este repositório.
2. Copie a pasta do plugin para a pasta de plugins do Flow Launcher:
   ```text
   %APPDATA%\FlowLauncher\Plugins\SoundSwitch
   ```
3. Reinicie o Flow Launcher ou execute o comando `rpd` (Reload Plugin Data) no Flow Launcher.

---

## 📂 Estrutura de Arquivos

```text
SoundSwitch-Plugin-For-FlowLauncher/
│
├── plugin.json              # Manifesto do Flow Launcher
├── main.py                  # Ponto de entrada e manipulador de queries e JSON-RPC
├── soundswitch_client.py    # Cliente CLI para integração silenciosa com SoundSwitch.CLI.exe
├── requirements.txt         # Especificação de dependências
├── README.md                # Documentação completa
├── .gitignore               # Ignora arquivos de compilação e cache
├── Images/                  # Ícones visuais de alta resolução
│   ├── icon.png
│   ├── playback.png
│   ├── recording.png
│   ├── mute.png
│   ├── unmute.png
│   ├── profile.png
│   ├── settings.png
│   └── device.png
└── lib/
    └── flowlauncher/        # Biblioteca FlowLauncher JSON-RPC embutida
```

---

## 📜 Histórico de Versões

### 🚀 v1.1.0 (Versão Atual)
- **Zero-Latency Instant Query**: Otimização profunda de performance eliminando chamadas síncronas de subprocessos durante a busca.
- **Ações Imediatas com Enter**: Digitar `ss` e apertar <kbd>Enter</kbd> agora funciona no mesmo milissegundo.
- **Leitura Direta de Configurações**: Leitura instantânea (< 1 ms) do arquivo `SoundSwitchConfiguration.json` para dispositivos e perfis.
- **Cache Inteligente em Background**: Atualização assíncrona do status dos dispositivos e estado de mudo em thread secundária sem travar a interface do Flow Launcher.
- **Tratamento Universal UTF-8**: Suporte robusto a caracteres acentuados no Windows para nomes de dispositivos (ex: "Alto-falantes").

### 📦 v1.0.0
- Lançamento inicial do plugin SoundSwitch para Flow Launcher.
- Alternância de dispositivos de reprodução e gravação.
- Suporte a perfis de áudio e controle de mudo do microfone.
- Biblioteca JSON-RPC embutida e ícones visuais dedicados.

---

## 👨‍💻 Autor

Criado por **[landrozaum](https://github.com/landrozaum)**.

## 📄 Licença

Distribuído sob a licença [MIT](LICENSE).
