#
#
#

options(stringsAsFactors = FALSE)

library(tm)


judgements <- readLines("../Data/Training_Data_Judgements.txt")

tweets <- readLines("../Data/Training_Data_Processed.txt", encoding = "UTF-8")


control <- list(stopwords = TRUE,
                removePunctuation = TRUE,
                removeNumbers = TRUE,
                minDocFreq = 2)


ComputeTermFrequencies <- function(tdm) {
  mat <- as.matrix(tdm)
  df <- data.frame(term = rownames(mat), frequency = rowSums(mat))
  df$occurs <- sapply(seq(nrow(mat)),
                      function(x) length(which(mat[x, ] > 0)) / ncol(mat))
  df$density <- df$frequency / sum(df$frequency)
  return(df[order(-df$occurs), ])
}


corpus <- Corpus(VectorSource(tweets[judgements == "y"]))
tdm <- TermDocumentMatrix(corpus, control)
y.term.frequencies <- ComputeTermFrequencies(tdm)

corpus <- Corpus(VectorSource(tweets[judgements == "n"]))
tdm <- TermDocumentMatrix(corpus, control)
n.term.frequencies <- ComputeTermFrequencies(tdm)


ClassifyTweet <- function(tweet, training.df, prior = .5, c = 1e-6) {
  corpus <- Corpus(VectorSource(tweet))
  tdm <- TermDocumentMatrix(corpus, control)
  freq <- rowSums(as.matrix(tdm))
  intersection <- intersect(rownames(freq), training.df$term)
  if (length(intersection) == 0) {
    return(prior * c ^ length(freq))
  } else {
    probs <- training.df$occurance[match(intersection, training.df$term)]
    return(prior * prod(match.probs * c ^ (length(freq) - length(intersection))))
  }
}


s <- sample.int(length(judgements), 50)
testing.data <- data.frame(tweets = tweets[s], judgements = judgements[s])

y.test <- sapply(testing.data$tweets, ClassifyTweet,
                 training.df = y.term.frequencies)
n.test <- sapply(testing.data$tweets, ClassifyTweet,
                 training.df = n.term.frequencies)

res <- y.test > n.test
table(res)

table(testing.data$judgements)


