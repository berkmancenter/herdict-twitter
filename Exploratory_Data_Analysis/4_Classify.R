#
#
#


options(stringsAsFactors = FALSE)

library(ggplot2)
library(tm)


ComputeTermFrequencies <- function(tdm) {
  mat <- as.matrix(tdm)
  df <- data.frame(term = rownames(mat), frequency = rowSums(mat))
  df$occurs <- sapply(seq(nrow(mat)),
                      function(x) length(which(mat[x, ] > 0)) / ncol(mat))
  df$density <- df$frequency / sum(df$frequency)
  return(df)
}

ClassifyTweet <- function(tweet, training.df, prior = .5, c = 1e-4) {
  corpus <- Corpus(VectorSource(tweet))
  tdm <- TermDocumentMatrix(corpus, control)
  freq <- rowSums(as.matrix(tdm))
  intersection <- intersect(rownames(freq), training.df$term)
  if (length(intersection) < 1) {
    return(prior * c ^ length(freq))
  } else {
    probs <- training.df$occurs[match(intersection, training.df$term)]
    return(prior * prod(probs * c ^ (length(freq) - length(intersection))))
  }
}


judgements <- readLines("../Data/Training_Data_Judgements.txt")
tweets <- readLines("../Data/Training_Data_Processed.txt", encoding = "UTF-8")

# Drop ambiguous judgements.
tweets <- tweets[judgements %in% c("y", "n")]
judgements <- judgements[judgements %in% c("y", "n")]

# Use the size of the smallest set of judgements as the size of the training
# data sets. This imposes the assumption of equal prior probabilities.
training.length <- min(sum(judgements == "y"), sum(judgements == "n"))

control <- list(tolower = TRUE,
                removePunctuation = TRUE,
                removeNumbers = TRUE,
                stopwords = TRUE,
                stemming = TRUE,
                minDocFreq = 2)

# Compute training data sets for "yes" and "no" judgements.
y.training.tweets <- sample(tweets[judgements == "y"], training.length)
corpus <- Corpus(VectorSource(y.training.tweets))
tdm <- TermDocumentMatrix(corpus, control)
y.training.df <- ComputeTermFrequencies(tdm)

n.training.tweets <- sample(tweets[judgements == "n"], training.length)
corpus <- Corpus(VectorSource(n.training.tweets))
tdm <- TermDocumentMatrix(corpus, control)
n.training.df <- ComputeTermFrequencies(tdm)

# Test classifier on a sample of judgements. Use priors learned from
# repeated trials.
for (trial in 1:10) {
  s <- sample.int(length(judgements), 75)
  testing.df <- data.frame(tweet = tweets[s], judgement = judgements[s])
  testing.df$prob.y <- sapply(testing.df$tweet, ClassifyTweet,
                              training.df = y.training.df, prior = .15)
  testing.df$prob.n <- sapply(testing.df$tweet, ClassifyTweet,
                              training.df = n.training.df, prior = .85)
  testing.df <- within(testing.df, guess <- ifelse(prob.y > prob.n, "y", "n"))
  cat("\n\nTrial ", trial, ":\n", sep = "")
  print(with(testing.df, table(judgement, guess)))
}


