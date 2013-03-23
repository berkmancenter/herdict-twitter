# Preprocesses historical Tweets for labelling with MTurk.


setwd("../Stream_And_Classify/Data")

tweets <- read.csv("Training_Data_Raw.csv",
                   col.names = c("text", "favorited", "reply.to.user.name",
                                 "datetime", "truncated", "reply.to.status.id",
                                 "status.id", "reply.to.user.id", "source",
                                 "user.name"),
                   colClasses = c("character", "NULL", "NULL", "POSIXct",
                                  "NULL", "NULL", "character", "NULL",
                                  "character", "character"),
                   stringsAsFactors = FALSE, encoding = "UTF-8")

# Extract tweet source.
tweets$source <- gsub("&lt;.*?&gt;", "", tweets$source)

# Strip non-ASCII characters.
tweets$text <- iconv(tweets$text, "UTF-8", "ASCII", sub = "")
tweets$source <- iconv(tweets$source, "UTF-8", "ASCII", sub = "")

# Replace whitespace characters with spaces.
tweets$text <- gsub("[[:space:]]+", " ", tweets$text)

# Trim leading and trailing whitespace.
tweets$text <- gsub("^\\s+|\\s+$", "", tweets$text)

# Unescape character entities.
tweets$text <- gsub("&quot;", '"', tweets$text)
tweets$text <- gsub("&quot;", '"', tweets$text)
tweets$text <- gsub("&lt;", "<", tweets$text)
tweets$text <- gsub("&gt;", ">", tweets$text)
tweets$text <- gsub("&amp;", "&", tweets$text)

# Remove tweets$text containing fewer than four words.
tweets <- tweets[sapply(strsplit(tweets$text, " "), length) >= 4, ]

# Remove retweets$text.
tmp <- sapply(strsplit(tweets$text, " "), function(x) "rt" %in% tolower(x))
tweets <- tweets[!tmp, ]

# Remove duplicate tweets$text.
tweets <- tweets[!duplicated(tweets$text), ]

# Remove tweets$text with identical rolling substrings.
window.length <- 50
for (i in seq_len(140 - window.length)) {
  tweets <- tweets[!duplicated(substring(tweets$text, i, window.length + i)), ]
}

# Remove tweets$text containing URLs that are identical except for their URLs.
has.url <- grepl("http://|https://", tweets$text)
tmp <- strsplit(tweets$text[has.url], " ")
tmp <- lapply(tmp, function(x) x[grep("http", x, invert = TRUE)])
has.url[has.url == TRUE] <- !duplicated(tmp)
tweets <- tweets[!has.url, ]

# Randomly order tweets$text.
tweets <- tweets[sample(length(tweets$text)), ]

# Remove near matches based on Levenshtein edit distance.
#tmp <- lapply(tweets$text, agrep, tweets$text, value = TRUE)

write.csv(tweets, "Training_Data_Clean.csv", row.names = FALSE)

quit()


