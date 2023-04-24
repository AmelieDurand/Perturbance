FROM python:3.7
RUN apt-get update
RUN pip install pip --upgrade
RUN pip install Click==7.1.2\
  matplotlib==3.3.2\
  numpy==1.18.5\
  pandas==1.1.2\
  requests==2.24.0\
  sklearn==0.0\
  wget==3.2\
  tensorflow-gpu==2.3.1
RUN pip install deepgoplus
COPY . /deepgoplus/
WORKDIR /deepgoplus
RUN tar xzf ./data-1.0.6.tar.gz
# For Singularity, needs write permission
RUN chmod -R o+w /deepgoplus/

#Set bash shell as entrypoint
ENTRYPOINT [ "/bin/bash"]
