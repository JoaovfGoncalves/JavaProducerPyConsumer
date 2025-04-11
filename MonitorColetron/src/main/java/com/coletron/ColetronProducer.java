package com.coletron;

import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;

import java.nio.charset.StandardCharsets;

public class ColetronProducer {
    private static final String EXCHANGE_NAME = "coletron_exchange";
    private final Connection connection;
    private final Channel channel;

    public ColetronProducer(String host, int port, String username, String password) throws Exception {
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost(host);
        factory.setPort(port);
        factory.setUsername(username);
        factory.setPassword(password);

        this.connection = factory.newConnection();
        this.channel = connection.createChannel();

        this.channel.exchangeDeclare(EXCHANGE_NAME, "topic", true);
    }

    public void enviarMensagem(String mensagem) throws Exception {
        String routingKey = "coletron.events";

        if (mensagem.contains("\"tipo_mensagem\":\"URNA_CHEIA\"")) {
            routingKey = "coletron.urna_cheia";
        } else if (mensagem.contains("\"tipo_mensagem\":\"CAPACIDADE_ALERTA\"")) {
            routingKey = "coletron.capacidade_alerta";
        }

        channel.basicPublish(EXCHANGE_NAME, routingKey, null, mensagem.getBytes(StandardCharsets.UTF_8));
        System.out.println("Mensagem enviada com routing key [" + routingKey + "]: " + mensagem);
    }

    public void fecharConexao() throws Exception {
        if (channel != null && channel.isOpen()) {
            channel.close();
        }
        if (connection != null && connection.isOpen()) {
            connection.close();
        }
    }
}
