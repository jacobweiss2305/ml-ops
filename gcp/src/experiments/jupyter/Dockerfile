FROM python:3.9-slim-buster

# Update aptitude with new repo
RUN apt-get update

# Linux tooling
RUN apt-get -y install git curl htop

# Install Github CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
&& chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
&& apt update \
&& apt install gh -y

RUN pip install jupyterlab

CMD ["jupyter-lab","--ip=0.0.0.0","--no-browser","--allow-root"]