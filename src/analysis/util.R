manual_cache <- function(object, object_name, cache_dir="manual_cache") {
  dir.create(cache_dir, showWarnings = FALSE)
  save(object_name, file=paste0(file.path(cache_dir, object_name), ".RData"))
}
