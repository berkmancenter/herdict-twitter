#
#


tweets <- readLines("../Data/Training_Data_Processed.txt")

cat("\nJudge whether each Tweet mentions Internet censorship.\n\n")

judged <- length(readLines("../Data/Training_Data_Judgements.txt"))

conn <- file("../Data/Training_Data_Judgements.txt", "a")
for (i in seq(judged + 1, length(tweets))) {
  cat(tweets[i], "\n")
  resp <- readline("(y, n, a, q) ")
  while (!(resp %in% c("y", "n", "a", "q"))) {
    cat('Please enter one of ("y", "n", "a", "q").\n')
    resp <- readline("(y, n, a, q) ")
  }
  if (resp == "q") { break }
  writeLines(resp, conn)
}

close(conn)


