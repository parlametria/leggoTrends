FROM python:3.6
WORKDIR leggo-trends
RUN apt-get update && apt-get install -y r-base
RUN R -e "install.packages('tidyverse',dependencies=TRUE, repos='http://cran.rstudio.com/')" 
RUN R -e "install.packages('lubridate',dependencies=TRUE, repos='http://cran.rstudio.com/')"
RUN R -e "install.packages('optparse',dependencies=TRUE, repos='http://cran.rstudio.com/')"
RUN pip3 install pandas
RUN pip install git+https://github.com/GeneralMills/pytrends
RUN pip install unidecode
COPY . .
CMD Rscript gera_entrada_google_trends.R -p data/proposicoes.csv -a data/apelidos.csv && python fetch_google_trends.py data/apelidos.csv data/pops/
