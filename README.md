# 🏙️ UrbanEye — Monitoramento Urbano Inteligente em Tempo Real

<p align="center">
  <img src="https://raw.githubusercontent.com/ultralytics/assets/main/yolov8/banner.png" alt="UrbanEye — visão computacional urbana" width="760">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Prot%C3%B3tipo%20Funcional-success?style=for-the-badge">
  <img src="https://img.shields.io/badge/YOLOv8-Detec%C3%A7%C3%A3o%20de%20Pessoas-red?style=for-the-badge">
  <img src="https://img.shields.io/badge/Flask-Tempo%20Real-black?style=for-the-badge&logo=flask">
  <img src="https://img.shields.io/badge/Smart%20City-Monitoramento-blue?style=for-the-badge">
</p>

<p align="center">
  <strong>UrbanEye</strong> é um sistema de **monitoramento urbano inteligente**, baseado em **visão computacional**, capaz de analisar o fluxo de pessoas em tempo real e gerar **status de lotação, recomendações automáticas e informações contextuais**, como clima.
</p>

---

## 🎯 Visão Geral

O **UrbanEye** foi desenvolvido para atuar como um **olho digital da cidade**, monitorando ambientes urbanos (eventos, praças, entradas públicas, terminais, feiras) e transformando vídeo ao vivo em **informação acionável**.

O sistema responde perguntas como:

* Quantas pessoas estão neste local agora?
* O ambiente está tranquilo, moderado ou lotado?
* Há alternativas mais seguras ou confortáveis?

Tudo isso ocorre **em tempo real**, sem identificação individual.

---

## 🧠 Conceito Central — Urban Flow Intelligence

O UrbanEye implementa o conceito de **Urban Flow Intelligence**, no qual:

* Pessoas são detectadas apenas como entidades genéricas
* Não há reconhecimento facial ou identificação
* O foco é o **fluxo coletivo**, não o indivíduo
* Decisões são baseadas em regras inteligentes

Esse conceito é ideal para **cidades inteligentes**, eventos públicos e gestão de multidões.

---

## 🧪 Pipeline do Sistema

```text
Câmera / Stream (DroidCam)
        │
        ▼
FFmpeg (decodificação H.264)
        │
        ▼
OpenCV (frames em tempo real)
        │
        ▼
YOLOv8 (detecção de pessoas)
        │
        ├── Contagem dinâmica
        ├── Classificação de status
        └── Bounding boxes
        │
        ▼
Flask Server
        │
        ├── API /status (JSON)
        ├── Stream /video_feed
        └── Interface Web
```

---

## 👥 Detecção de Pessoas

* Modelo: **YOLOv8n (Ultralytics)**
* Classe utilizada: `0 — person`
* Thresholds distintos:

  * **0.08** para contagem (sensível)
  * **0.50** para visualização (confiante)

Essa separação garante **robustez estatística** sem poluir a interface.

---

## 🚦 Lógica de Lotação

A lotação é classificada com base em limites configuráveis:

```python
LOTACAO = {
    "TRANQUILO": 4,
    "MODERADO": 10
}
```

Resultado possível:

* 🟢 TRANQUILO
* 🟡 MODERADO
* 🔴 LOTADO

---

## 💡 Sistema de Recomendações

O UrbanEye gera **recomendações automáticas**, combinando:

* Status de lotação
* Local atual
* Local alternativo
* Condições climáticas

Exemplo:

> "Muita movimentação na Entrada Principal. Recomendamos deslocamento para o Estande 2, onde o fluxo está menor."

---

## 🌦️ Integração com Clima (Open-Meteo)

O sistema consulta periodicamente a API **Open-Meteo** para obter o clima atual:

* Céu limpo / nublado
* Chuva leve, moderada ou forte

Esses dados influenciam diretamente as recomendações exibidas ao público.

---

## 🌐 Interface Web e API

### Rotas principais

| Rota          | Função                     |
| ------------- | -------------------------- |
| `/`           | Página inicial             |
| `/status`     | Dados em tempo real (JSON) |
| `/video_feed` | Stream MJPEG               |
| `/pontos`     | Pontos monitorados         |
| `/sobre`      | Informações do projeto     |
| `/contato`    | Contato                    |

---

## ▶️ Execução do Projeto

### Dependências

```bash
pip install ultralytics flask opencv-python requests numpy
```

### Executar

```bash
python app.py
```

Acesse:

```text
http://localhost:5000
```

---

## ⚖️ Privacidade e Ética

O UrbanEye:

* ❌ Não identifica pessoas
* ❌ Não armazena imagens pessoais
* ✅ Trabalha apenas com contagem e fluxo

Totalmente alinhado a princípios de **LGPD**, **ética em IA** e **uso responsável**.

---

## 🧪 Casos de Uso

* Eventos públicos (feiras, exposições)
* Entradas de prédios públicos
* Praças e espaços urbanos
* Apoio à guarda municipal
* Painéis de Smart City

---

## 🧱 Status do Projeto

* Protótipo funcional
* Testado em ambiente real (DroidCam)
* Arquitetura pronta para expansão

---

## 📜 Licença

Projeto experimental e institucional.

Uso permitido para pesquisa, demonstração e inovação urbana.

---

<p align="center"><strong>UrbanEye — IA observando o fluxo da cidade 🏙️👁️</strong></p>
