#!/usr/bin/python
#-*- encoding: utf-8 -*-

''' /*  
:Programa de controle Residencial -- Beta - 1.0.0
>inicio - 03/02/2016
>Modificao do pino do led vermelho - 07/02/2016
>Inclusao da funcao para leitura da temperatura  07/02/2016
>Modificao de Todas as Variaveis do modulo rele - 15/02/2016
>Modificação na interface - Adicionado cores para os diferentes estados 14/04/2016
>Ajustes nos nomes e limpeza da interface 14/04/2016
>Adição do Rele IN4 para controle da Tomada 1 do quarto - 09/05/2016
>Adição da Função de Backup do Servidor com a chamada de um Shell Script Externo ( presente em /home/pi/backup.sh) 11/06/2016
> 09/07/2016 - Adição do Rele IN03 Para controle da Lâmpada dos Fundos.
> 01/09/2016 - Incluida a Função sincroniza_horadata para sincronização do horário do sistema com a internet
> 06/02/2018 - Incluida a funcão organiza_camera_4
> 06/02/2018 - Corrigido o erro em que a tela piscava quando o led_blink estava ativado.
> 21/02/2018 - Removida a Função organiza_camera_4
> 29/07/2018 - Corrigido o erro do VNC que iniciava como Root, Correção realizada no Script vnc.sh
> 25/12/2018 - Adição da Função LDR para ligar a luz de acordo com a leitura do Sensor

#01/09/2016 
DESENVOLVIMENTO E ADIÇÃO DE FUNÇÕES DA VERSÃO 1.0.0 ENCERRADA
MODIFICAÇÃO NO CÓDIGO APENAS PARA PEQUENAS MANUTENÇÕES

*/

''' 
#bibliotecas
import os
import time
import subprocess
import commands
from datetime import datetime
import RPi.GPIO as gpio

#variaveis globais
hora = 0
minuto = 0
hora_minuto = 0
temperatura_max_soc = 46   #padrão 49 °
temperatura_min_soc = 31   #padrão 32 °
cooler_status = 0
backup_status = 0
led_status = 0
organiza_camera_4_status = 0
funcao_sensor = 0                 # Em 0, Desativa de  	função de checagem do Sensor LDR, 1 Ativa a checagem
leitura_sensor_ldr = 0
status_sensor_ldr_noite = 1
hora_checar_sensor_ldr = 990      # horário que começa a verificação do sensor LDR, 16:30 ( 990 Minutos, padrão )
sensibilidade_ldr = 900           # Sensibilidade do Sensor LDR, próximo a 0 = claro

#hora de ligamento e desligamento do pino11 - IN2 //Lampada 1 - Frente
hora_liga_pin11 =17        #padrão 17
minuto_liga_pin11 =30
hora_desliga_pin11 = 23
minuto_desliga_pin11 = 50

#hora de ligamento e desligamento do pino12 - IN3 // Lampada 2 - Fundos
hora_liga_pin12 = 18       #padrão 17
minuto_liga_pin12 = 15
hora_desliga_pin12 = 22
minuto_desliga_pin12 = 00

#hora de ligamento e desligamento do pino13 - IN4 //Tomada 1 - Quarto
hora_liga_pin13 = 17
minuto_liga_pin13 = 30
hora_desliga_pin13 = 4
minuto_desliga_pin13 = 00

#hora de ligamento e desligamento do pino15 - IN5
hora_liga_pin15 = 1
minuto_liga_pin15 = 58
hora_desliga_pin15 = 2
minuto_desliga_pin15 = 00

#hora de ligamento e desligamento do pino16 - IN6
hora_liga_pin16 = 1
minuto_liga_pin16 = 58
hora_desliga_pin16 = 2
minuto_desliga_pin16 = 00

#hora de ligamento e desligamento do pino18 - IN7
hora_liga_pin18 = 1
minuto_liga_pin18 = 58
hora_desliga_pin18 = 2
minuto_desliga_pin18 = 00

#hora de ligamento e desligamento do pino22 - IN8
hora_liga_pin22 = 10
minuto_liga_pin22 = 35
hora_desliga_pin22 = 12
minuto_desliga_pin22 = 40


#Configura o acesso da placa pela numeraçao de pinos fisicos
#Configura a direçao dos pinos usados
gpio.setwarnings(False)
gpio.setmode(gpio.BOARD)

# Relês
gpio.setup(7, gpio.OUT)  # IN1 //Cooler
gpio.setup(11, gpio.OUT) # IN2 //Lampada 1 - Frente 
#gpio.setup(12, gpio.OUT) # IN3 //Lampada 2 - Fundos
gpio.setup(13, gpio.OUT) # IN4 //Tomada 1 - Quarto
gpio.setup(15, gpio.OUT) # IN5
gpio.setup(16, gpio.OUT) # IN6
gpio.setup(18, gpio.OUT) # IN7
gpio.setup(22, gpio.OUT) # IN8
#Leds
gpio.setup(32, gpio.OUT) # Led Vermelho
gpio.setup(40, gpio.OUT) # Led Verde

#Funcao que inicializa o estado dos pinos
def inicializa_pinos():
    gpio.output(7, 1)  # IN1 //Cooler
    gpio.output(11, 1) # IN2 //Lampada 1 - Frente
    #gpio.output(12, 1) # IN3 //Lampada 2 - Fundos
    gpio.output(13, 1) # IN4 //Tomada 1 - Quarto
    gpio.output(15, 1) # IN5
    gpio.output(16, 1) # IN6
    gpio.output(18, 1) # IN7
    gpio.output(22, 1) # IN8
    print("Pinos Inicializados com sucesso!!")

#funcao que converte a hora atual em minutos
def converte_hora_minuto(hora, minuto):
    hora_temp = hora * 60
    hora_temp = hora_temp + minuto
    return hora_temp

#funcao Led Blink
def led_blink():
    gpio.output(40,1)
    time.sleep(0.15)
    gpio.output(40,0)

#####  Funcao para obter a temperatura do processador ###
def obter_temperatura():
    tfile = open ("/sys/class/thermal/thermal_zone0/temp") #abre o Arquivo "temp"
    tempdata = tfile.read()	#le o arquivo e salva na variavel "tempdata"
    tfile.close()	#fecha o arquivo
    temp = int(tempdata)	#converte para inteiro
    #temperatura vem em milesimas - calcular os graus celcius
    temp = temp / 1000
    return temp

####  Funcao que chamao Script de backup do Servidor ###
def realizar_backup():
    os.system("/home/pi/desenvolvimento/my_softwares/controle_residencial/sistemaBackup.sh")

###   Função que sincroniza o horário do sistema com o servidor NTP usando o NTPDATE ###
def sincroniza_horadata():
    print("Sincronizando Horário do Sistema com time.windows.com")
    os.system("ntpdate -u time.windows.com")

###   Função Para iniciar o VNC Server  ###
def inicia_vnc():
    os.system("/home/pi/vnc.sh")

###   Função para fazer a leitura do Sensor LDR, retorna um inteiro  ###
def checar_sensor_ldr():
    leitura_sensor_ldr_func = commands.getoutput("python /home/pi/desenvolvimento/my_softwares/controle_residencial/ldr_sensor.py")
    leitura_sensor_ldr_func = int(leitura_sensor_ldr_func)
    return leitura_sensor_ldr_func

###   Função Para iniciar o Script de organização dos arquivos da camera 4  ###
#def organiza_camera_4():
#    os.system("/home/pi/organiza_camera_4.sh")
    #subprocess.call(['lxterminal', 'x','/home/pi/ok.sh'])

### Função para checar se a função de leitura do LDR está ativa
def checar_funcao_sensor():
    if funcao_sensor == 0:
        status_sensor_ldr_noite = 1
        #Escreve No Log ( Essa função será temporária.)
        data_funcao_sensor_ldr=commands.getoutput("date +%d/%m/%Y-%H:%M:%S")  # o commands.getoutput pega a saida do comando, ao inves o seu retorno
        texto_funcao_sensor_ldr=("%s - Leitura do sensor LDR Desativada")%(data_funcao_sensor_ldr)
        log = open('/home/pi/compartilhamento/log.txt', 'a')
        texto = []
        texto.append(texto_funcao_sensor_ldr+'\n')
        log.writelines(texto)
        log.close()
    else:
        status_sensor_ldr_noite = 0
    return status_sensor_ldr_noite


# Programas iniciados com o sistema # 
inicializa_pinos()
#status_sensor_ldr_noite == checar_funcao_sensor()
#realizar_backup()
#sincroniza_horadata()
#inicia_vnc()
time.sleep(1.8)

###################################################################

#converte a hora de ligar os pinos em minutos
hora_minuto_liga11 = converte_hora_minuto(hora_liga_pin11,minuto_liga_pin11)
hora_minuto_liga12 = converte_hora_minuto(hora_liga_pin12,minuto_liga_pin12)
hora_minuto_liga13 = converte_hora_minuto(hora_liga_pin13,minuto_liga_pin13)
hora_minuto_liga15 = converte_hora_minuto(hora_liga_pin15,minuto_liga_pin15)
hora_minuto_liga16 = converte_hora_minuto(hora_liga_pin16,minuto_liga_pin16)
hora_minuto_liga18 = converte_hora_minuto(hora_liga_pin18,minuto_liga_pin18)
hora_minuto_liga22 = converte_hora_minuto(hora_liga_pin22,minuto_liga_pin22)
#converte a hora de desligar os pinos em minutos
hora_minuto_desliga11 = converte_hora_minuto(hora_desliga_pin11,minuto_desliga_pin11)
hora_minuto_desliga12 = converte_hora_minuto(hora_desliga_pin12,minuto_desliga_pin12)
hora_minuto_desliga13 = converte_hora_minuto(hora_desliga_pin13,minuto_desliga_pin13)
hora_minuto_desliga15 = converte_hora_minuto(hora_desliga_pin15,minuto_desliga_pin15)
hora_minuto_desliga16 = converte_hora_minuto(hora_desliga_pin16,minuto_desliga_pin16)
hora_minuto_desliga18 = converte_hora_minuto(hora_desliga_pin18,minuto_desliga_pin18)
hora_minuto_desliga22 = converte_hora_minuto(hora_desliga_pin22,minuto_desliga_pin22)

#Muda o diretório de trabalho
#os.chdir("/home/pi/desenvolvimento/my_softwares/controle_residencial")

#loop principal
while True:
    #Temperatura do SoC
    temperatura_SoC = obter_temperatura()
    #Hora do sistema
    now = datetime.now()
    hora = now.hour
    minuto = now.minute
    hora_minuto = converte_hora_minuto(hora,minuto)
    #interface


    os.system("clear")
    #print status_sensor_ldr_noite
    #print funcao_sensor
    print("                  Sistema de Controle Residencial - 1.0      ")
    print("hora atual do sistema: %i hora e %i minutos")%(hora,minuto)
    print("hora atual do sistema em minutos: %i minutos")%(hora_minuto)
    #os.system("uptime")
    #print("\nhora de Ligamento do pino 4: %i minutos")%(hora_minuto_liga13)
    #print("hora de Desligamento do pino 4: %i minutos")%(hora_minuto_desliga13)    
    print("Temperatura do Processador %i Graus\n\n")%(temperatura_SoC)
    print("------------Estados ---------\n")
   
    #Status do LDR
    #print("Hora checar Sensor LDR %i")%(hora_checar_sensor_ldr)
    #print("Staus do Sensor LDR: %i")%(status_sensor_ldr_noite)
    """print("Sensibilidade Sensor LDR: %i")%(sensibilidade_ldr)
    if leitura_sensor_ldr ==0:
        print("Ultima leitura LDR : Não Medido hoje")
    else:
        print("Ultima leitura LDR : %i")%(leitura_sensor_ldr)
    """
    #Backup do Servidor e Sincronição do horário do sistema com a internet- Configurado para realizar backup do servidor todos os dias às 3 da manhã
    
    if hora_minuto == 180 and backup_status == 0:
        realizar_backup()
        sincroniza_horadata()
        backup_status = 1

    #Atualiza o status do Backup e do sensor LDR para "0" a Partir da Meia noite.    
    if hora_minuto == 0:
        backup_status = 0
        #status_sensor_ldr_noite = 0
        #leitura_sensor_ldr = 0
        #status_sensor_ldr_noite == checar_funcao_sensor()
	"""
    ############################################################################################################################################
    #Sensor LDR
    #Faz a Leitura do Sensor diante de três condições, a hora ser maior/igual a definida, o status do LDR ser igual a Zero e a função sensor está ativada ( valor em 1)
    if hora_minuto >= hora_checar_sensor_ldr and status_sensor_ldr_noite == 0 and funcao_sensor == 1:
        leitura_sensor_ldr = checar_sensor_ldr()
        #time.sleep(3)
        #Verifica se a leitura é maior que a sensibilidade, se sim, muda o Status do Sensor Para 1 e a hora/minuto para 990
        if leitura_sensor_ldr > sensibilidade_ldr:
            status_sensor_ldr_noite = 1
            hora_checar_sensor_ldr = 990
            #Escreve No Log ( Essa função será temporária.)
            data_lampada1_ligar=commands.getoutput("date +%d/%m/%Y-%H:%M:%S")  # o commands.getoutput pega a saida do comando, ao inves o seu retorno
            texto_lampada1_ligar=("%s - Lampada 1 Ligada - Valor - %s")%(data_lampada1_ligar,leitura_sensor_ldr)
            log = open('/home/pi/compartilhamento/log.txt', 'a')
            texto = []
            texto.append(texto_lampada1_ligar+'\n')
            log.writelines(texto)
            log.close()
            #Caso Contrário, Incrementa o valor da hora de Verificação em 1 minuto
        else:
            #print("chegou aqui 2")
            #time.sleep(3)
            hora_checar_sensor_ldr = hora_minuto + 1
	"""
    
    ############################################################################################################################################
    #Backup Status
    if backup_status == 1:
        print("Backup Realizado?  - \033[32mSim\033[0;0m")
    if backup_status == 0:
        print("Backup Realizado?  - \033[31mNão\033[0;0m")

    ############################################################################################################################################
    #led de Status
    if hora_minuto >= 420:
        print("Led de Status      - \033[32mLigado\033[0;0m")
        led_status = 1
    else:
        led_status = 0
        print("Led de Status      - \033[31mDesligado\033[0;0m")

    ############################################################################################################################################        
	"""
    #Controle do cooler
    if temperatura_SoC >= temperatura_max_soc:
        gpio.output(7,0)
        gpio.output(32,1)
        cooler_status = 1

    if temperatura_SoC <= temperatura_min_soc:
        gpio.output(7,1)
        gpio.output(32,0)
        cooler_status = 0
    #                                ::::::: Mensagem na tela :::::::         
    if cooler_status == 1:
        print("Cooler             - \033[32mLigado\033[0;0m")
    if cooler_status == 0:
        print("Cooler             - \033[31mDesligado\033[0;0m")
	"""
    
    ################################################## RELE IN2 ################################################################################
        #Controle de ligamento do pino11 - IN2 - Lampada de Frente
        #Liga a Lampada no horário Definido e caso o Status do LDR Seja igual a 1
    if hora_minuto >= hora_minuto_liga11 and hora_minuto_desliga11 >= hora_minuto and status_sensor_ldr_noite == 1:
        gpio.output(11,0) # Como estamos lidando com o Relê, a Lógica é invertida, pois enviamos Low para Armar, e High para desarmar o Relê.
        print("Lampada da Frente  - \033[32mLigada\033[0;0m")
    else:
        gpio.output(11,1) # Como estamos lidando com o Relê, a Lógica é invertida, pois enviamos Low para Armar, e High para desarmar o Relê.
        print("Lampada da Frente  - \033[31mDesligada\033[0;0m")


    """ ################################################## RELE IN3 ################################################################################
        #Controle de ligamento do pino12 - IN3 - Lampada dos Fundos
        #Liga a Lampada no horário Definido e caso o Status do LDR Seja igual a 1
    if hora_minuto >= hora_minuto_liga12 and hora_minuto_desliga12 >= hora_minuto and status_sensor_ldr_noite == 1:
        gpio.output(12,0) # Como estamos lidando com o Relê, a Lógica é invertida, pois enviamos Low para Armar, e High para desarmar o Relê.
        print("Lampada dos Fundos - \033[32mLigada\033[0;0m")
    else:
        gpio.output(12,1) # Como estamos lidando com o Relê, a Lógica é invertida, pois enviamos Low para Armar, e High para desarmar o Relê.
        print("Lampada dos Fundos - \033[31mDesligada\033[0;0m")
 
    """
    ################################################## RELE IN4 ################################################################################
        #Controle de ligamento do pino13 - IN4 - Tomada do Quarto
    if hora_minuto >= hora_minuto_liga13 and hora_minuto_desliga13 <= hora_minuto:
        gpio.output(13,0) # Como estamos lidando com o Relê, a Lógica é invertida, pois enviamos Low para Armar, e High para desarmar o Relê.
        print("Tomada 1           - \033[32mLigada\033[0;0m")
    elif hora_minuto_liga13 >= hora_minuto and hora_minuto_desliga13 >= hora_minuto:
        gpio.output(13,0) # Como estamos lidando com o Relê, a Lógica é invertida, pois enviamos Low para Armar, e High para desarmar o Relê.
        print("Tomada 1           - \033[32mLigada\033[0;0m")
    else:
        gpio.output(13,1) # Como estamos lidando com o Relê, a Lógica é invertida, pois enviamos Low para Armar, e High para desarmar o Relê.
        print("Tomada 1 - Quarto  - \033[31mDesligada\033[0;0m")
    
        '''        
        Comentários .... 

        '''
    #DEBUG - Verificar o diretório de trabalho
    #os.system("ls")
    if led_status == 1:
        led_blink()       
    time.sleep(3.5)
