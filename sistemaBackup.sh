#!/bin/bash

#backup do Servidor

# Verifica se o Backup já foi realizado, confirmando se a pasta já existe no local.
# O Script realiza backup das pastas, "www", "desenvolvimento" e os arquivos .sh da "home"
# Exclui os videos da pasta "Videos" para reduzir o tamanho do backup
# Comprime a pasta para .zip

# Changelog ------------
# 11/06/16 - Criação - Realiza apenas o Backup, sem funcoes extras
# 12/06/16 - Adição da condição de só realizar Backup se o mesmo já não tiver sido feito no dia corrente
# 14/06/16 - Adição da Função para compactador o arquivo no final do backup ( necessida do Zip instalado no Sistema.)
# 31/07/18 - Adiçao do parametro -y no zip, para nao seguir links simbolicos
# 08/08/18 - Adiçao da Funcao de criar pastas de ano e mes.
# 08/08/18 - Adicao da Funcao para verificar se o HD externo esta presente, se nao, encerra o backup
# 08/08/18 - Adicao do Registo no log de Eventos do Sistema
# 28/08/18 - Adiçao do Backup de configuracoes, do Motion e Samba.
# 04/04/19 - Adiçao do Backup de configuraçoes, do Vsftpd, fstab, Apache2, Fail2ban e Megatools.

# Novas funcoes a serem adicionadas
# - Salvar Bakcup em um diretorio temporario, caso o HD externo nao esteja presente.
# - Salvar em nuvem


#Global
dia=`date +%d`
mes=`date +%m-%B`
ano=`date +%Y`
pasta_data=`date +%d%m%Y`
data_log=`date +%d/%m/%Y-%H:%M:%S`
hd_externo="/media/michael_hd/Raspberry/Backups"

echo "Verificando HD Externo"
sleep 1
if [ -r "$hd_externo/.ok" ]; then   # -- 1 -- Verifica se o acesso ao HD externo está ok, se sim, executa os comandos abaixo:
	echo "Ok"
	sleep 2
	cd $hd_externo
	mkdir -p $ano/$mes/
	cd $ano/$mes
	if [ ! -s "$pasta_data.zip" ]; then
		echo "Realizando Backup do Servidor, Aguarde..."
		sleep 2
		echo "Criando Estrutura de Pastas..."
		sleep 1
		mkdir $pasta_data
		mkdir $pasta_data/shel_script
		mkdir -p $pasta_data/configuracoes/motion
		mkdir -p $pasta_data/configuracoes/samba
		mkdir -p $pasta_data/configuracoes/transmission
        mkdir -p $pasta_data/configuracoes/fail2ban
        mkdir -p $pasta_data/configuracoes/fstab
        mkdir -p $pasta_data/configuracoes/megatools
        mkdir -p $pasta_data/configuracoes/vsftpd
        mkdir -p $pasta_data/configuracoes/apache2

		# echo "Realizando Backup do Servidor, Aguarde ..."
		echo "Diretorio criado >> $pasta_data"
		echo "Realizando Backup do Diretorio www"
		sudo cp -R -P /var/www/ /media/michael_hd/Raspberry/Backups/$ano/$mes/$pasta_data
		echo "Excluindo videos"
		#rm $pasta_data/www/arquivos/videos/*.mp4 #obsoleto
		echo "Realizando Backup do Diretorio desenvolvimento"
		sudo cp -R /home/pi/compartilhamento/desenvolvimento/ /media/michael_hd/Raspberry/Backups/$ano/$mes/$pasta_data
		echo "Realizando Backup dos Arquivos shel_script"
		cp  /home/pi/*.sh /media/michael_hd/Raspberry/Backups/$ano/$mes/$pasta_data/shel_script

		#Backup das configurações
		echo "Realizando Backup de Configuracoes"

	        # Motion
		echo "> Motion"
		sudo cp -R -P /etc/motion/* /media/michael_hd/Raspberry/Backups/$ano/$mes/$pasta_data/configuracoes/motion

		# Samba
		echo "> Samba"
		sudo cp -R -P /etc/samba/*  /media/michael_hd/Raspberry/Backups/$ano/$mes/$pasta_data/configuracoes/samba

		# Transmission
		echo "> Trasmission"
		sudo cp -R -P /etc/transmission-daemon/*  /media/michael_hd/Raspberry/Backups/$ano/$mes/$pasta_data/configuracoes/transmission

		# Fail2ban
		echo "> Fail2ban"
                sudo cp -R -P /etc/fail2ban/*  /media/michael_hd/Raspberry/Backups/$ano/$mes/$pasta_data/configuracoes/fail2ban

		#fstab
		echo "> Fstab"
		sudo cp -R -P /etc/fstab  /media/michael_hd/Raspberry/Backups/$ano/$mes/$pasta_data/configuracoes/fstab

		#vsftpd
		echo "> Vsftpd"
		sudo cp -R -P /etc/vsftpd.conf  /media/michael_hd/Raspberry/Backups/$ano/$mes/$pasta_data/configuracoes/vsftpd

		#Megatools
		echo "> Megatools"
                cp /home/pi/.megarc /media/michael_hd/Raspberry/Backups/$ano/$mes/$pasta_data/configuracoes/megatools

		#Apache2
		echo "> Apache2"
                cp -R -P /etc/apache2/* /media/michael_hd/Raspberry/Backups/$ano/$mes/$pasta_data/configuracoes/apache2

                echo "Compactando backup.."
		zip -r -y -9 -T $pasta_data.zip $pasta_data >/dev/null
		echo "Arquivo $pasta_data.zip criado "
		echo "Fazendo a faxina..."
		rm -R $pasta_data
		echo "Concluido"
		echo "$data_log - Sistema - Backup Finalizado">>/home/pi/compartilhamento/log.txt
		exit
	else
		echo "O backup ja foi realizado hoje, Ate amanha..."
		exit
	fi
else
	echo "HD Externo nao encontrado - Backup nao realizado - Saindo...."
	echo "$data_log - Sistema - Backup NAO realizado - HD Externo nao encontrado">>/home/pi/compartilhamento/log.txt
	sleep 10
fi
