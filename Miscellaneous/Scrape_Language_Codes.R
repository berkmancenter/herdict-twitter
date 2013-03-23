# This script scrapes the codes from the corresponding Wikipedia article.
# Herdict groups reports by country using ISO 3166-1 alpha-2 codes.


library(XML)


dat <- readHTMLTable("http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2")

dat <- dat[[4]][, c("Country name", "Code")]
names(dat) <- c("Country", "Code")

write.csv(dat, "../../Data/Country_Codes.csv",
          row.names = FALSE, col.names = FALSE)


