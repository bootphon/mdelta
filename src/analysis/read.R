library(plyr)
library(foreach)
library(doParallel)
library(magrittr)

DEFAULT_FRAME_RATE <- 100
DEFAULT_MDELTA_CUTOFFS <- c(0.0, 0.02, 0.04)

frames_to_sec <- function(x) {
  return(x/DEFAULT_FRAME_RATE)
}

sec_to_frames <- function(x) {
  return(round(x*DEFAULT_FRAME_RATE))
}

add_frames_to_edge <- function(d) {
  frames_to_end <- max(d$time) - d$time
  d$second_half <- frames_to_end < d$time
  d$frames_to_end <- ifelse(d$second_half, frames_to_end, d$time)  
  d$prop_of_file <- d$time/max(d$time)
  return(d)
}

read_mdelta_byframe <- function(f) {
  mdelta_raw <- read.csv(f, strip.white=TRUE)
  result <- ddply(mdelta_raw, .(f_id), .parallel=TRUE, .fun=add_frames_to_edge)
  result$time_sec <- frames_to_sec(result$time)
  return(result)
}

read_all_mdelta <- function(fns, read_f=read_mdelta_byframe) {
  registerDoParallel()
  result <- ldply(fns, .fun=function(f) read_f(f), .parallel=TRUE)
  return(result)  
}

read_intervals <- function(fn, ...) {
  return(read.csv(fn, ...))
}

cutoff_mdelta <- function(cutoff, intervals) {
  return(intervals %$% m_delta >= cutoff)
}

random_toss <- function(to_toss, intervals, seed=1) {
  n <- nrow(intervals)
  set.seed(seed)
  rows_to_toss <- sample(1:n, to_toss)
  set.seed(NULL)
  result <- !(1:n %in% rows_to_toss)
  return(result)
}

write_some_intervals <- function(intervals, file, which_ones_fn,
                                 to_frames=TRUE) {
  if (to_frames) {
    intervals$start <- sec_to_frames(intervals$start)
    intervals$end <- sec_to_frames(intervals$end)
  }
  if ("inverted" %in% names(intervals)) {
    intervals <- intervals[intervals$inverted == F,]
  }
  which_ones <- which_ones_fn(intervals)
  intervals <- intervals %$% intervals[which_ones,c("f_id","start","end")]
  write.table(intervals, file=file, row.names=F, col.names=T, quote=F, sep=",")
}

write_mdelta_intervals <- function(intervals, file, cutoff, to_frames=TRUE) {
  which_ones_fn <- partial(cutoff_mdelta, cutoff=cutoff)
  write_some_intervals(intervals, file, which_ones_fn, to_frames)
}

write_random_intervals <- function(intervals, file, to_toss, to_frames=TRUE,
                                   seed=round(to_toss)) {
  which_ones_fn <- partial(random_toss, to_toss=to_toss, seed=seed)
  write_some_intervals(intervals, file, which_ones_fn, to_frames)
}
