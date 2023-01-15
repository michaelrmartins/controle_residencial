#!/bin/bash

#chama Controle residencial

#Encerra o processo Iniciando automaticamente pelo sistema.
#O comando abaixo pega apenas i ID do processo e salva na variavel p_id
p_id=`ps -A | grep python |awk {'print $1'}`
kill $p_id
echo "Processo com ID  $p_id encerrado, iniciando o sistema."
sleep 3
#inicia o programa.
#lxterminal --command=/home/pi/camera_full.sh
python /home/pi/compartilhamento/desenvolvimento/my_softwares/controle_residencial/controle_residencial.py
