#
#
#


library(twitteR)

setwd("..")


unescape <- function(string) {
  string <- gsub("&quot;", '"', string)
  string <- gsub("&apos;", "'", string)
  string <- gsub("&lt;", "<", string)
  string <- gsub("&gt;", ">", string)
  string <- gsub("&amp;", "&", string)
  return(string)
}


verbs <- c("censor", "censored", "censoring", "censorship",
           "block", "blocked", "blocking",
           "filter", "filtered", "filtering")
nouns <- c("internet", "url", "urls", "site", "sites", "page", "pages",
           "web", "website", "websites", "webpage", "webpages", "net")
hashtags <- c("#webfreedom", "#netfreedom", "#censorship", "#gfw")

terms <- c(outer(verbs, nouns, paste), hashtags)

tweets <- character()
for (i in seq(length(terms))) {
  tweets <- c(tweets, searchTwitter(terms[i], n = 1500))
  Sys.sleep(1)
}

tweets <- unique(tweets)

tweets <- do.call("rbind", lapply(tweets, as.data.frame))
tweets <- tweets[, c("id", "screenName", "text", "created", "statusSource")]
names(tweets)[c(2, 5)] <- c("screen.name", "status.source")
tweets$text <- unescape(tweets$text)
tweets$status.source <- unescape(tweets$status.source)
tweets$status.source <- gsub("<.*?>", "", tweets$status.source)

tweets <- tweets[order(tweets$created), ]

write.csv(tweets, "Data/Tweets.csv", row.names = FALSE)


