FROM rocker/tidyverse:3.6.2

WORKDIR leggo-trends

RUN apt-get update
RUN apt-get install libssl-dev libxml2-dev libcurl4-openssl-dev libgit2-dev vim less -y 
COPY DESCRIPTION .

RUN R -e "install.packages('lubridate',dependencies=TRUE, repos='http://cran.rstudio.com/')"
RUN R -e "install.packages('optparse',dependencies=TRUE, repos='http://cran.rstudio.com/')"
RUN R -e "install.packages('here',dependencies=TRUE, repos='http://cran.rstudio.com/')"
RUN R -e "install.packages('dotenv', dependencies=TRUE, repos='http://cran.rstudio.com/')"
RUN R -e "install.packages('aweek', dependencies=TRUE, repos='http://cran.rstudio.com/')"
RUN R -e "install.packages('futile.logger', dependencies=TRUE, repos='http://cran.rstudio.com/')"

RUN apt-get update
RUN apt-get install -y python3-pip

RUN pip3 install pandas
RUN pip3 install --upgrade --user git+https://github.com/GeneralMills/pytrends
RUN pip3 install unidecode
RUN pip3 install -U python-dotenv

COPY . .