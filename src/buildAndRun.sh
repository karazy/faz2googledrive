 #Builds the dockerfile and runs it locally
 docker build --no-cache -t faz2drive .
 docker run -it faz2drive python ./execute_FAZ_loader.py