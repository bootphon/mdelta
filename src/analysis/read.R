library(plyr)
library(foreach)
library(doParallel)
library(magrittr)

add_frames_to_edge <- function(d) {
  frames_to_end <- max(d$time) - d$time
  d$second_half <- frames_to_end < d$time
  d$frames_to_end <- ifelse(second_half, frames_to_end, d$time)  
  return(d)
}

read_mdelta_byframe <- function(f) {
  mdelta_raw <- read.csv(f)
  result <- ddply(mdelta_raw, .(f_id), .parallel=TRUE, .fun=add_frames_to_edge)
  return(result)
}

read_all_mdelta <- function(fns, read_f=read_mdelta_byframe) {
  registerDoParallel()
  result <- ldply(fns, .fun=function(f) read_f(f), .parallel=TRUE)
  return(result)  
}