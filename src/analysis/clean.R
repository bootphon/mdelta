library(stats)
library(pryr)

DEFAULT_CUTOFF_FRAMES <- 50
DEFAULT_LOESS_FIXED_SPAN <- 10
DEFAULT_NA_REPLACE <- -0.001

cut_mdelta <- function(d, cutoff_frames=DEFAULT_CUTOFF_FRAMES) {
  d$m_delta[d$frames_to_end < 50] <- NA
  return(d)
}

loess_span <- function(n_frames_on_either_side, n_total_frames) {
  n_span_frames <- 2*n_frames_on_either_side + 1
  result <- min(1.0, n_span_frames/n_total_frames)
  return(result)
}

smooth_mdelta <- function(d, loess_fixed_span=DEFAULT_LOESS_FIXED_SPAN,
                          col_name="m_delta") {
  span <- loess_span(loess_fixed_span, max(d$time))
  m <- loess(m_delta ~ time, data=d, span=span)
  smoothed_values <- predict(m)
  smoothed_values[is.na(d$m_delta)] <- NA
  d[[col_name]] <- smoothed_values
  d <- d[d$direction=="positive", -which(colnames(d) == "direction")]
  return(d)
}

between <- function(x, start, end) {
  return(x >= start & x <= end)
}

invert <- function(intervals, final_time) {
  new_start <- intervals %$% c(0.0, end)
  new_end <- intervals %$% c(start, final_time)
  result <- data.frame(start=new_start, end=new_end)
  return(result)
}

mean_na <- partial(mean, na.rm=T)
median_na <- partial(median, na.rm=T)

intervals_average_mdelta <- function(intervals, mdelta_d, stat=mean_na,
                                     invert=FALSE){
  registerDoParallel()
  if (invert) {
    intervals <- invert(intervals, max(mdelta_d$time_sec))
  }
  result <- mdelta_d %$% ddply(intervals, .(start, end), .parallel=TRUE,
         .fun=function(d) d %$%
              data.frame(m_delta=stat(m_delta[between(time_sec, start, end)])))
  return(result)
}

intervals_and_inverted <- function(intervals, mdelta_d, stat=mean_na) {
  res <- intervals_average_mdelta(intervals, mdelta_d, stat=stat)
  res$inverted <- F
  res_i <- intervals_average_mdelta(intervals, mdelta_d, stat=stat, invert=T)
  res_i$inverted <- T
  return(rbind(res, res_i))
}

replace_na <- function(d, na_replace=DEFAULT_NA_REPLACE) {
  d$m_delta[is.na(d$m_delta)] <- na_replace
  return(d)
}