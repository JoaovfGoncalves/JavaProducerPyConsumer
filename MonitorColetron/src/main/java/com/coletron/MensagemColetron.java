package com.coletron;

import java.time.Instant;
import java.util.Random;

public class MensagemColetron {

    private static final String ID_COLETOR = "M001";
    private static final String LOCALIZACAO = "-23.5505,-46.6333";
    private static final double CAPACIDADE_TOTAL = 30.0;
    private static final Random rand = new Random();

    public static String gerarMensagemJsonAleatoria() {
        String[] tipos = {
                "REGISTRO_DESCARTE",
                "CAPACIDADE_ALERTA",
                "URNA_CHEIA",
                "FALHA_MAQUINA",
                "STATUS_PERIODICO"
        };

        String tipo = tipos[rand.nextInt(tipos.length)];
        double volumeAtual = gerarVolumePorTipo(tipo);
        String status;
        String informacaoAdicional;

        switch (tipo) {
            case "REGISTRO_DESCARTE":
                status = "OK";
                informacaoAdicional = "";
                break;
            case "CAPACIDADE_ALERTA":
                status = "ATENCAO";
                informacaoAdicional = "80% Ocupado";
                break;
            case "URNA_CHEIA":
                status = "CRITICO";
                informacaoAdicional = "COLETA URGENTE NECESSARIA";
                volumeAtual = CAPACIDADE_TOTAL;
                break;
            case "FALHA_MAQUINA":
                status = "INOPERANTE";
                informacaoAdicional = "Erro no descarte - Reparo necessario";
                break;
            case "STATUS_PERIODICO":
                status = "OPERACIONAL";
                informacaoAdicional = "";
                break;
            default:
                status = "DESCONHECIDO";
                informacaoAdicional = "";
        }

        StringBuilder json = new StringBuilder();
        json.append("{")
                .append("\"id_coletor\":\"").append(ID_COLETOR).append("\",")
                .append("\"timestamp\":\"").append(Instant.now()).append("\",")
                .append("\"localizacao\":\"").append(LOCALIZACAO).append("\",")
                .append("\"tipo_mensagem\":\"").append(tipo).append("\",")
                .append("\"status\":\"").append(status).append("\",")
                .append("\"volume_atual\":").append(String.format(java.util.Locale.US, "%.1f", volumeAtual)).append(",")
                .append("\"capacidade_total\":").append(String.format(java.util.Locale.US, "%.1f", CAPACIDADE_TOTAL)).append(",")
                .append("\"informacao_adicional\":\"").append(informacaoAdicional).append("\"")
                .append("}");

        return json.toString();
    }

    private static double gerarVolumePorTipo(String tipo) {
        switch (tipo) {
            case "URNA_CHEIA":
                return CAPACIDADE_TOTAL;
            case "CAPACIDADE_ALERTA":
                return CAPACIDADE_TOTAL * 0.8;
            default:
                return 1.0 + (rand.nextDouble() * (CAPACIDADE_TOTAL - 1.0));
        }
    }
}
