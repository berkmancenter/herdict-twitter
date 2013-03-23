# Uses the Twitter Search API to retrieve historical Tweets that may
# express Internet censorship or inaccessibility.


library(twitteR)

setwd("../Stream_And_Classify/Data")

verbs <- c("censor", "censored", "censoring", "censorship",
           "block", "blocked", "blocking",
           "filter", "filtered", "filtering",
           "down", "broke", "broken", "technical difficulty",
           "cant to", "can%27t to")  # To capture "can't {get, go} to"
nouns <- c("internet", "url", "urls", "site", "sites", "page", "pages",
           "web", "website", "websites", "webpage", "webpages", "net",
           "http%3A%2F%2F")  # To capture a generic URL.
hashtags <- c("%23webfreedom", "%23netfreedom", "%23censorship", "%23gfw")

terms <- c(outer(verbs, nouns, paste), hashtags)

#file.remove("Training_Data_Raw.csv")
for (i in seq_along(terms)) {
  tweets <- searchTwitter(terms[i], n = 1500)
  tweets <- do.call("rbind", lapply(tweets, as.data.frame))
  if (is.null(dim(tweets))) next  # Retrieved no tweets.
  write.table(tweets, "Training_Data_Raw.csv", append = TRUE,
              sep = ",", row.names = FALSE, col.names = FALSE,
              qmethod = "double")
  Sys.sleep(2)
}

quit()


