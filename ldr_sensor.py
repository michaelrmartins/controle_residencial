#!/usr/bin/python
#-*- encoding: utf-8 -*-

# Este Scrit tem a finalidade de ler o Sensor LDR e Retornar um valor De Acordo com a Quantidade de Luz. 
# Michael Martins 2018

# Changelog
'''   
> 20/12/2018 - Criação
> 25/12/2018 - Adaptação do retorno de valores
> 26/12/2018 - Inclusão da função de log
> 31/01/2019 - Inclusão da opção de ativar ou desativar o registro do log através da variável registrar_log

'''  
import RPi.GPIO as GPIO
import time
import os
import commands
from datetime import datetime

GPIO.setmode(GPIO.BOARD)

#Ativa ou desativa a função de registro no log, 0 para desativado e 1 para ativado.
registrar_log = 0

#define the pin that goes to the circuit
pin_to_circuit = 29

#define o tempo de exibicaoo dos valores
delay_time = 0.1

#Funcaoo que faz a leitura do LDR e retorna o Valor
def rc_time (pin_to_circuit):
    count = 0

    #Output on the pin for
    GPIO.setup(pin_to_circuit, GPIO.OUT)
    GPIO.output(pin_to_circuit, GPIO.LOW)
    time.sleep(delay_time)

    #Change the pin back to input
    GPIO.setup(pin_to_circuit, GPIO.IN)

    #Count until the pin goes high
    while (GPIO.input(pin_to_circuit) == GPIO.LOW):
        count += 1
       # print count

    return count

# Retornar o Valor da leitura
def retorna(valor_leitura):
    temp_valor_leitura=valor_leitura
    #print temp_valor_leitura 
    return temp_valor_leitura
    #exit(temp_valor_leitura)

# Escreve no log o evento realizado
def registrar_log_ldr(leitura):
    leitura_temp=leitura
    #Inicia a gravação do Log do Evento
    #Obter data e hora
    data_inicio_ldr=commands.getoutput("date +%d/%m/%Y-%H:%M:%S")  # o commands.getoutput pega a saida do comando, ao inves o seu retorno
    texto_sensor_ldr=("%s - Sensor LDR - Valor - %s")%(data_inicio_ldr,leitura_temp)
    log = open('/home/pi/compartilhamento/log.txt', 'a')
    texto = []
    texto.append(texto_sensor_ldr+'\n')
    log.writelines(texto)
    log.close()

#Catch when script is interrupted, cleanup correctly
# Loop com Try / Exception
try:
    # Main loop
    precisao = 5
    contador = 0
    leituras = 0
    while (contador < precisao):
        leituras = leituras + (rc_time(pin_to_circuit))
        contador += 1
    leituras = leituras / precisao
    if registrar_log == 1:
        registrar_log_ldr(leituras)
    #retorna(leituras)
except KeyboardInterrupt:
    pass
finally:
    print(leituras)
    GPIO.cleanup()