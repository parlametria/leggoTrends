#!/usr/bin/env Rscript
library(tidyverse)
library(futile.logger)

source(here::here("scripts/popularity/process_popularity.R"))

if (!require(optparse)) {
  install.packages("optparse")
  suppressWarnings(suppressMessages(library(optparse)))
}

option_list = list(
  make_option(
    c("-t", "--tt"),
    type = "character",
    default = NULL,
    help = "caminho do arquivo para a popularidade no Twitter [default= %default]",
    metavar = "character"
  ),
  make_option(
    c("-g", "--gt"),
    type = "character",
    default = here::here("data/pops/"),
    help = "nome da pasta destino dos arquivos de saída com a popoularidade do Google Trends [default= %default]",
    metavar = "character"
  ),
  make_option(
    c("-i", "--interesses_filepath"), 
    type="character", 
    default="data/interesses.csv",
    help="caminho do arquivo de interesses [default= %default]", 
    metavar="character"
    ),
  make_option(
    c("-p", "--proposicoes_filepath"), 
    type="character", 
    default="data/proposicoes.csv",
    help="caminho do arquivo de proposições [default= %default]", 
    metavar="character"
  ),
  make_option(
    c("-o", "--out"),
    type = "character",
    default = here::here("data/pressao.csv"),
    help = "caminho do arquivo de saída deste script [default= %default]",
    metavar = "character"
  )
)

opt_parser = OptionParser(option_list = option_list)
opt = parse_args(opt_parser)

twitter_trends_path <- opt$tt
interesses_filepath <- opt$interesses_filepath
proposicoes_filepath <- opt$proposicoes_filepath
pops_folderpath <- opt$gt
output_path <- opt$out

if (!file.exists(twitter_trends_path)) {
  stop(
    'Arquivo de trends do twitter não encontrado.
  Por favor, execute o script localizado em:
  ./scripts/tweets_from_last_days/export_tweets_from_last_days.R'
  )
}

if (!dir.exists(pops_folderpath)) {
  stop(
    'Diretório de trends do twitter não encontrado.
  Por favor, execute o script localizado em:
  ./fetch_google_trends.py'
  )
}


flog.info("Gerando dados de popularidade do Google Trends e Twitter...")
popularity <- combine_indexes(twitter_trends_path,
                              pops_folderpath,
                              interesses_filepath,
                              proposicoes_filepath)

write_csv(popularity, paste0(output_path))

flog.info("Feito!")
