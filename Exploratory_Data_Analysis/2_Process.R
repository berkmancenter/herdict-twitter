#
#


unescape <- function(string) {
  string <- gsub("&quot;", '"', string)
  string <- gsub("&apos;", "'", string)
  string <- gsub("&lt;", "<", string)
  string <- gsub("&gt;", ">", string)
  string <- gsub("&amp;", "&", string)
  return(string)
}


tweets <- readLines("../Data/Training_Data_Raw.txt", encoding = "UTF-8")

tweets <- gsub('\\"', "", tweets)
tweets <- unescape(tweets)
tweets <- tweets[grep("http://|https://", tweets, invert = TRUE)]
tweets <- tweets[substr(tweets, 0, 2) != "RT"]
tweets <- tweets[!duplicated(tweets)]

conn <- file("../Data/Training_Data_Processed.txt", "w")
writeLines(tweets, conn)
close(conn)


quit()


