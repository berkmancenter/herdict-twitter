#
#


setwd("../../Data")

tweets <- read.csv("Training_Data_Raw.csv",
                   col.names = c("text", "favorited", "replyToSN",
                                 "created", "truncated", "replyToSID",
                                 "id", "replyToUID", "statusSource",
                                 "screenName"),
                   stringsAsFactors = FALSE, encoding = "UTF-8")

tweets <- tweets$text

# Replace whitespace characters with spaces.
tweets <- gsub("[[:space:]]+", " ", tweets)

# Trim leading and trailing whitespace.
tweets <- gsub("^\\s+|\\s+$", "", tweets)

# Unescape character entities.
tweets <- gsub("&quot;", '"', tweets)
tweets <- gsub("&quot;", '"', tweets)
tweets <- gsub("&lt;", "<", tweets)
tweets <- gsub("&gt;", ">", tweets)
tweets <- gsub("&amp;", "&", tweets)

# Remove tweets containing fewer than four words.
tweets <- tweets[sapply(strsplit(tweets, " "), length) >= 4]

# Remove retweets.
tmp <- sapply(strsplit(tweets, " "), function(x) "rt" %in% tolower(x))
tweets <- tweets[!tmp]

# Remove duplicate tweets.
tweets <- tweets[!duplicated(tweets)]

# Remove tweets with identical rolling substrings.
window.length <- 50
for (i in seq_len(140 - window.length)) {
  tweets <- tweets[!duplicated(substring(tweets, i, window.length + i))]
}

# Remove tweets containing URLs that are identical except for their URLs.
has.url <- grepl("http://|https://", tweets)
tmp <- strsplit(tweets[has.url], " ")
tmp <- lapply(tmp, function(x) x[grep("http", x, invert = TRUE)])
has.url[has.url == TRUE] <- !duplicated(tmp)
tweets <- tweets[!has.url]

# Order tweets alphabetically.
#tweets <- sort(tweets)

# Randomly order tweets.
tweets <- tweets[sample(length(tweets))]

# Remove near matches based on Levenshtein edit distance.
#tmp <- lapply(tweets, agrep, tweets, value = TRUE)

conn <- file("Training_Data_Normalized.txt", "w")
writeLines(tweets, conn)
close(conn)

# Strip non-ASCII characters.
system("tr -cd '\11\12\15\40-\176' < Training_Data_Normalized.txt > Training_Data_Clean.txt")

quit()


