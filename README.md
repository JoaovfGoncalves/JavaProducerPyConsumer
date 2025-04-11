# 🗑️ Coletron – Sistema de Auditoria de Coleta Eletrônica

Este projeto integra duas aplicações que se comunicam por meio do RabbitMQ: um **produtor em Java** e um **consumidor em Python**. Ele simula máquinas coletoras de resíduos eletrônicos que enviam dados em tempo real para serem processados e auditados.

---

## Desenvolvedores

- [Igor Wanderley](https://github.com/igorfwds) | ifws@cesar.school
- [João Victor Ferraz](https://github.com/JoaovfGoncalves) | jvfg@cesar.school
- [Maria Júlia Menezes](https://github.com/mjuliamenezes) | mjotm@cesar.school
- [Maria Luísa Coimbra](https://github.com/Malucoimbr) | mlcl@cesar.school
- [Maria Luiza Calife](https://github.com/LuizaCalife) | mlcdf@cesar.school

---

## Visão Geral Do Projeto

- **Produtor (Java)**: simula máquinas de coleta e envia mensagens sobre descartes, status, falhas e alertas.
- **Consumidor (Python)**: recebe e processa as mensagens, salvando-as em um log para auditoria.

---

## Requisitos

- Docker (para o RabbitMQ)
- Java 8+ (para o produtor)
- Python 3.10+ (para o consumidor)

---

## Produtor (Java)

### 🛠 Tecnologias

- Java 17+
- RabbitMQ Java Client (AMQP)

### Exemplo de Mensagem Enviada

```
[01/08/2025 - 14:30] MCH001 : Av. Brasil, 123 : REGISTRO_DESCARTE : OK : 15.0 : 20.0
```

### 🚀 Como Executar

1. Suba o RabbitMQ via Docker:

   ```bash
   docker run -d --hostname rabbit-host --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
   ```

   - Porta: [http://localhost:15672](http://localhost:15672)
   - Login: `coletron` | Senha: `coletron123`

2. Compile e execute o produtor:
   - Usando Maven:
     ```bash
     mvn clean package
     java -jar target/coletron-produtor.jar
     ```
   - Usando Gradle:
     ```bash
     ./gradlew build
     java -jar build/libs/coletron-produtor.jar
     ```

---

## Consumidor (Python)

### 🛠 Tecnologias

- Python 3.10+
- RabbitMQ
- pika (AMQP client para Python)

### 🚀 Como Executar

1. Certifique-se de que o RabbitMQ está rodando.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o consumidor:
   ```bash
   python coletron.py
   ```

---

## Estrutura das Mensagens

Todas as mensagens trocadas seguem o seguinte padrão:

```
[dd/MM/yyyy - HH:mm] ID_Coletor : Localização : Tipo_Mensagem : Status : Volume_Coletado (kg) : Capacidade_Total (kg) : Informação_Adicional (se houver)
```

---

## 📄 Logs de Auditoria
Todas as mensagens recebidas pelo sistema são registradas em um arquivo de log em formato JSON, acompanhadas de data e hora.
Esses registros garantem a rastreabilidade completa dos eventos processados e formam um histórico confiável das operações simuladas pelas máquinas coletoras.

O log pode ser utilizado para análises, verificações e auditorias futuras, contribuindo para a transparência e integridade do sistema.
