# Especificações do Projeto

## Requisitos

O projeto foi testado em Windows utilizando Python na versão `3.12`. A única biblioteca não nativa utilizada é `tabulate`. Recomendamos utilização de um ambiente e instalação desta biblioteca a partir do pip.

* `pip install tabulate`.

## Comandos

As informações das salas podem ser tanto em maiúsculas quanto minúsculas. O formato do dia da semana é abreviado em 3 letras (Seg, Ter, Qua, etc) e as horas são escritas do numero da hora seguido do 'h', logo 10h, 8h, etc.

Os comandos em si devem ser escritos em letra MINÚSCULA. 

Ao enviar comandos, atente-se com o envio seguindo o que foi estabelecido nos requisitos e as abreviações propostas. Nem todos os erros de entrada foram tratados completamente e podem gerar *crash*.

## Executando o Projeto

Para executar o servidor, rode em um terminal o comando:

* `python run_server.py`.

Para executar o cliente, escolha uma porta que não esteja sendo utilizada e rode em um terminal o comando:

* `python run_client -p port_num`

