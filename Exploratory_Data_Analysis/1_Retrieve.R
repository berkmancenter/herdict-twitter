# Uses the Twitter Search API to retrieve historical tweets that may
# express Internet censorship or inaccessibility.


library(twitteR)

verbs <- c("censor", "censored", "censoring", "censorship",
           "block", "blocked", "blocking",
           "filter", "filtered", "filtering",
           "down", "broke", "broken", "technical difficulty",
           "cant to", "can't to")  # To capture "can't {get, go} to"
nouns <- c("internet", "url", "urls", "site", "sites", "page", "pages",
           "web", "website", "websites", "webpage", "webpages", "net")
hashtags <- c("#webfreedom", "#netfreedom", "#censorship", "#gfw")

terms <- c(outer(verbs, nouns, paste), hashtags)

file.remove("../Data/Training_Data_Raw.txt")
for (i in seq(length(terms))) {
  tweets <- searchTwitter(terms[i], n = 25)
  tweets <- do.call("rbind", lapply(tweets, as.data.frame))
  if (is.null(dim(tweets))) { next }  # Retrieved no tweets.
  write.table(tweets$text, "../Data/Training_Data_Raw.txt", append = TRUE,
              row.names = FALSE, col.names = FALSE)
  Sys.sleep(2)
}

quit()


