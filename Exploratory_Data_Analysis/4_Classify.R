#
#
#

options(stringsAsFactors = FALSE)

library(ggplot2)
library(tm)


tweets <- read.csv("Data/Training_Data.csv", fileEncoding = "UTF-8")

corpus <- Corpus(VectorSource(tweets$text[tweets$censorship = "n"]))
control <- list(stopwords = TRUE,
                removePunctuation = TRUE,
                removeNumbers = TRUE,
                minDocFreq = 2)
tdm <- TermDocumentMatrix(corpus, control)





