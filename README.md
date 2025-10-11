
## Ambiente virtual python para execução dos scripts  

- Criar ambiente virtual caso não criado: python -m venv pvenv
- Ativar ambiente virtual: .\pvenv\script\activate 
- Estando no venv instale os requisitos caso não instalado: pip install -r .\requirements.txt
- Desativar ambiente virtual: deactivate

------------------------------------------
## Executando script gerador de video

- Manual de ajuda do script: 
~~~~bash
python .\script\gen.py -h
~~~~
Exemplo de comandos:  
~~~~python
# Cria video passando 
# !IMPORTANTE arquivo de audio apontado dentro do arquivo estar na mesma pasta do arquivo
python.exe .\gen.py .\ultrastar.txt
# Cria video passando imagem background especifica
# !IMPORTANTE arquivo de audio apontado dentro do arquivo estar na mesma pasta do arquivo
python.exe .\gen.py .\ultrastar.txt -bg "bg.jpg"
# Cria video passando imagem background especifica com caminho absoluto
# !IMPORTANTE arquivo de audio apontado dentro do arquivo estar na mesma pasta do arquivo
python.exe .\gen.py "c:\MinhaPasta\ultrastar.txt"
# Cria video especificando o arquivo de audio base
python.exe .\gen.py .\ultrastar.txt -a audio.mp3
~~~~
Obs.: 
 - Os videos são salvos ao final do processo na pasta .\Output na raiz do projeto. 
 - O nome atribuído ao arquivo final segue o padrão 'artist - title' onde ambas as variáveis são lidas do arquivo txt ultrastar.
 - Passar o audio que irá gerar o video final não faz alterar o arquivo txt onde consta o audio original.
 - Caso não seja passado o audio será utilizado o audio especificado no arquivo ultrastar txt.

------------------------------------------
## Sobre demais script
Todos os demais scripts podem e devem ser executados via inteface gráfica Tkinter, basta executar:
~~~~python
python .\main.py
~~~~
- gera_nfo : Gera o arquivo .nfo de informações que serão lidas por reprodutores como emby.
- gera_thumb : Gera a capa do vídeo que será lida em reprodutores como emby, bastando estar com mesmo nodo do video.
- normalizar_nomes : Normaliza nomes de arquivos, exemplo, existe "video v2.mp4" porem não existe um "video.mp4" então ele renomeia o arquivo.
- renomear_arquivos : A partir da planilha Song na aba Karaoke na coluna filename renomeia o arquivo apontado para o nome especificado em full_title.
- verificar_arquivos : Verifica os arquivos que faltam na planilha e os que faltam na pasta, confrontando a pasta com a planilha.
------------------------------------------
## Uso direto do FFMPEG no sistema 
Converter FLAC para MP3 320k
~~~~bash
C:\ffmpeg\bin\ffmpeg.exe -i 'musica.flac'  -c:a libmp3lame -b:a 320k music.mp3
~~~~
