package com.coletron;

import java.io.IOException;
import java.util.Scanner;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.io.FileWriter;
import java.io.PrintWriter;

public class Main {
    private static final String HOST = "localhost";
    private static final int PORT = 5672;
    private static final String USERNAME = "coletron";
    private static final String PASSWORD = "coletron123";

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.println("=== SISTEMA DE PRODUÇÃO DE MENSAGENS COLETRON ===");
        System.out.println("1. Modo Single Producer");
        System.out.println("2. Modo Multi Producer (Paralelo)");
        System.out.print("Escolha o modo (1 ou 2): ");

        int modo = scanner.nextInt();
        scanner.nextLine(); // Consumir quebra de linha

        System.out.print("Número de mensagens a enviar: ");
        int numMensagens = scanner.nextInt();
        scanner.nextLine();

        if (modo == 1) {
            executarSingleProducer(numMensagens);
        } else if (modo == 2) {
            System.out.print("Número de produtores a utilizar: ");
            int numProdutores = scanner.nextInt();
            scanner.nextLine();

            executarMultiProducer(numProdutores, numMensagens);
        } else {
            System.err.println("Opção inválida!");
        }

        scanner.close();
    }

    private static void executarSingleProducer(int numMensagens) {
        System.out.println("Iniciando modo Single Producer...");
        long tempoInicio = System.currentTimeMillis();

        ColetronProducer producer = null;
        try {
            producer = new ColetronProducer(HOST, PORT, USERNAME, PASSWORD);

            for (int i = 1; i <= numMensagens; i++) {
                String mensagem = MensagemColetron.gerarMensagemJsonAleatoria();
                producer.enviarMensagem(mensagem);

                System.out.println(mensagem);

                salvarMensagemNoLog(mensagem);

                if (i % 100 == 0 || i == numMensagens) {
                    System.out.printf("Progresso: %d/%d mensagens enviadas (%.1f%%)\n",
                            i, numMensagens, (i * 100.0 / numMensagens));
                }
            }

            long tempoTotal = System.currentTimeMillis() - tempoInicio;
            double mensagensPorSegundo = numMensagens * 1000.0 / tempoTotal;

            System.out.println("\n=== RESULTADO SINGLE PRODUCER ===");
            System.out.println("Total de mensagens enviadas: " + numMensagens);
            System.out.println("Tempo total: " + formatarTempo(tempoTotal));
            System.out.printf("Taxa: %.2f mensagens/segundo\n", mensagensPorSegundo);

        } catch (Exception e) {
            System.err.println("Erro no modo Single Producer: " + e.getMessage());
            e.printStackTrace();
        } finally {
            try {
                if (producer != null) {
                    producer.fecharConexao();
                }
            } catch (Exception e) {
                System.err.println("Erro ao fechar produtor: " + e.getMessage());
            }
        }
    }

    private static void executarMultiProducer(int numProdutores, int numMensagens) {
        System.out.println("Iniciando modo Multi Producer com " + numProdutores + " threads paralelas...");
        long tempoInicio = System.currentTimeMillis();

        // Usar um contador atômico para controlar as mensagens enviadas (thread-safe)
        AtomicInteger mensagensEnviadas = new AtomicInteger(0);
        AtomicInteger mensagensFalhas = new AtomicInteger(0);

        // Executor para gerenciar o pool de threads
        ExecutorService executor = Executors.newFixedThreadPool(numProdutores);
        CountDownLatch latch = new CountDownLatch(numProdutores);

        try {
            // Criar e iniciar uma thread para cada produtor
            for (int i = 0; i < numProdutores; i++) {
                final int produtorId = i + 1;

                // Cada thread terá sua própria instância do produtor
                executor.submit(() -> {
                    Thread.currentThread().setName("Producer-" + produtorId);
                    System.out.println("Thread " + Thread.currentThread().getName() + " iniciada");

                    ColetronProducer producer = null;
                    try {
                        producer = new ColetronProducer(HOST, PORT, USERNAME, PASSWORD);

                        while (true) {
                            int mensagemNum = mensagensEnviadas.incrementAndGet();

                            if (mensagemNum > numMensagens) {
                                break;
                            }

                            // Enviar a mensagem
                            String mensagem = MensagemColetron.gerarMensagemJsonAleatoria();
                            producer.enviarMensagem(mensagem);

                            System.out.println("[Thread " + produtorId + "] " + mensagem);
                            salvarMensagemNoLog("[Thread " + produtorId + "] " + mensagem);
                            // Feedback de progresso
                            if (mensagemNum % 100 == 0 || mensagemNum == numMensagens) {
                                System.out.printf("Thread %d: Enviada mensagem %d/%d (%.1f%%)\n",
                                        produtorId, mensagemNum, numMensagens,
                                        (mensagemNum * 100.0 / numMensagens));
                            }
                        }
                    } catch (Exception e) {
                        System.err.println("Erro na thread " + produtorId + ": " + e.getMessage());
                        e.printStackTrace();
                        mensagensFalhas.incrementAndGet();
                    } finally {
                        try {
                            if (producer != null) {
                                producer.fecharConexao();
                            }
                        } catch (Exception e) {
                            System.err.println("Erro ao fechar produtor " + produtorId + ": " + e.getMessage());
                        }
                        System.out.println("Thread " + Thread.currentThread().getName() + " finalizada");
                        latch.countDown();
                    }
                });
            }

            Thread monitorThread = new Thread(() -> {
                try {
                    while (!latch.await(1, TimeUnit.SECONDS)) {
                        int enviadas = mensagensEnviadas.get() - 1; // Ajuste porque incrementamos antes de enviar
                        if (enviadas > numMensagens) {
                            enviadas = numMensagens;
                        }
                        System.out.printf("Progresso geral: %d/%d mensagens (%.1f%%)\n",
                                enviadas, numMensagens, (enviadas * 100.0 / numMensagens));
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            });
            monitorThread.setDaemon(true);
            monitorThread.start();

            latch.await();

            long tempoTotal = System.currentTimeMillis() - tempoInicio;
            int mensagensReaisEnviadas = Math.min(mensagensEnviadas.get() - 1, numMensagens);
            double mensagensPorSegundo = mensagensReaisEnviadas * 1000.0 / tempoTotal;

            System.out.println("\n=== RESULTADO MULTI PRODUCER PARALELO ===");
            System.out.println("Total de produtores (threads): " + numProdutores);
            System.out.println("Total de mensagens enviadas: " + mensagensReaisEnviadas);
            System.out.println("Total de falhas: " + mensagensFalhas.get());
            System.out.println("Tempo total: " + formatarTempo(tempoTotal));
            System.out.printf("Taxa: %.2f mensagens/segundo\n", mensagensPorSegundo);
            System.out.printf("Eficiência: %.2fx em relação ao uso sequencial (estimado)\n",
                    numProdutores > 0 ? (double)numProdutores / (numProdutores / (mensagensPorSegundo / (numMensagens / (tempoTotal / 1000.0)))) : 0);

        } catch (Exception e) {
            System.err.println("Erro geral no modo Multi Producer: " + e.getMessage());
            e.printStackTrace();
        } finally {
            // Encerrar o executor
            executor.shutdown();
            try {
                if (!executor.awaitTermination(30, TimeUnit.SECONDS)) {
                    System.err.println("⚠️ Timeout ao esperar threads finalizarem, forçando encerramento.");
                    executor.shutdownNow();
                }
            } catch (InterruptedException e) {
                executor.shutdownNow();
                Thread.currentThread().interrupt();
            }
        }
    }
    public static void salvarMensagemNoLog(String mensagem) {
        try (PrintWriter out = new PrintWriter(new FileWriter("logs/mensagens_enviadas.log", true))) {
            out.println(mensagem);
        } catch (IOException e) {
            System.err.println("Erro ao escrever no log: " + e.getMessage());
        }
    }

    private static String formatarTempo(long milissegundos) {
        if (milissegundos < 1000) {
            return milissegundos + " ms";
        } else {
            double segundos = milissegundos / 1000.0;
            return String.format("%.2f s", segundos);
        }
    }
}