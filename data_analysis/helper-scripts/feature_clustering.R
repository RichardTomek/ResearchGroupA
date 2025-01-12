required_packages <- c("cluster", "R.utils", "RHRV", "tidyverse")

# Calculate rise and fall features
calculate_rise_fall_features <- function(rr_intervals) {
  diffs <- diff(rr_intervals)
  rises <- which(diffs > 0)
  falls <- which(diffs < 0)
  
  rise_times <- numeric()
  current_rise <- c()
  
  for(i in 1:(length(diffs)-1)) {
    if(diffs[i] > 0) {
      current_rise <- c(current_rise, diffs[i])
    } else if(length(current_rise) > 0) {
      rise_times <- c(rise_times, sum(current_rise))
      current_rise <- c()
    }
  }
  
  fall_times <- numeric()
  current_fall <- c()
  
  for(i in 1:(length(diffs)-1)) {
    if(diffs[i] < 0) {
      current_fall <- c(current_fall, abs(diffs[i]))
    } else if(length(current_fall) > 0) {
      fall_times <- c(fall_times, sum(current_fall))
      current_fall <- c()
    }
  }
  
  max_rise <- if(length(rise_times) > 0) max(rise_times) else NA
  max_fall <- if(length(fall_times) > 0) max(fall_times) else NA
  mean_rise <- if(length(rise_times) > 0) mean(rise_times) else NA
  mean_fall <- if(length(fall_times) > 0) mean(fall_times) else NA
  rise_rate <- length(rises) / length(diffs)
  fall_rate <- length(falls) / length(diffs)
  
  return(list(
    max_rise_time = max_rise,
    max_fall_time = max_fall,
    mean_rise_time = mean_rise,
    mean_fall_time = mean_fall,
    rise_rate = rise_rate,
    fall_rate = fall_rate
  ))
}

# Calculate time domain features
calculate_time_features <- function(rr_intervals) {
  mean_rr <- mean(rr_intervals)
  sdnn <- sd(rr_intervals)
  rmssd <- sqrt(mean(diff(rr_intervals)^2))
  
  nn50 <- sum(abs(diff(rr_intervals)) > 0.05)
  pnn50 <- (nn50 / length(diff(rr_intervals))) * 100
  
  hist_data <- hist(rr_intervals, breaks = "FD", plot = FALSE)
  tri_index <- length(rr_intervals) / max(hist_data$counts)
  
  cv <- (sdnn / mean_rr) * 100
  
  return(list(
    mean_rr = mean_rr,
    sdnn = sdnn,
    rmssd = rmssd,
    nn50 = nn50,
    pnn50 = pnn50,
    tri_index = tri_index,
    cv = cv
  ))
}

# Calculate nonlinear features
calculate_nonlinear_features <- function(rr_intervals) {
  rr_n <- rr_intervals[-length(rr_intervals)]
  rr_n1 <- rr_intervals[-1]
  
  sd1 <- sd(diff(rr_intervals) / sqrt(2))
  sd2 <- sqrt(2 * var(rr_intervals) - sd1^2)
  
  calculate_sample_entropy <- function(series, m = 2, r = 0.2 * sd(series)) {
    n <- length(series)
    template_matches <- function(template, m) {
      count <- 0
      for(i in 1:(n-m+1)) {
        if(all(abs(series[template:(template+m-1)] - series[i:(i+m-1)]) < r)) count <- count + 1
      }
      return(count - 1)
    }
    
    A <- sum(sapply(1:(n-m), function(i) template_matches(i, m+1)))
    B <- sum(sapply(1:(n-m), function(i) template_matches(i, m)))
    
    if(B == 0) return(NA)
    -log(A/B)
  }
  
  sample_ent <- tryCatch({
    calculate_sample_entropy(rr_intervals)
  }, error = function(e) NA)
  
  return(list(
    sd1 = sd1,
    sd2 = sd2,
    sd1_sd2_ratio = sd1/sd2,
    sample_entropy = sample_ent
  ))
}

# Extract frequency features
extract_freq_features <- function(hrv.data) {
  fa <- hrv.data$FreqAnalysis[[1]]
  
  lf_power <- mean(fa$LF, na.rm = TRUE)
  hf_power <- mean(fa$HF, na.rm = TRUE)
  vlf_power <- mean(fa$VLF, na.rm = TRUE)
  ulf_power <- mean(fa$ULF, na.rm = TRUE)
  
  lf_hf_ratio <- mean(fa$LFHF, na.rm = TRUE)
  total_power <- ulf_power + vlf_power + lf_power + hf_power
  
  peak_lf <- max(fa$LF, na.rm = TRUE)
  peak_hf <- max(fa$HF, na.rm = TRUE)
  
  sd_lf <- sd(fa$LF, na.rm = TRUE)
  sd_hf <- sd(fa$HF, na.rm = TRUE)
  
  list(
    lf_power = lf_power,
    hf_power = hf_power,
    vlf_power = vlf_power,
    ulf_power = ulf_power,
    lf_hf_ratio = lf_hf_ratio,
    total_power = total_power,
    peak_lf = peak_lf,
    peak_hf = peak_hf,
    sd_lf = sd_lf,
    sd_hf = sd_hf
  )
}

# Main processing function
process_hrv_data <- function(combined_data, feature_set) {
  # Process RR intervals
  processed_data <- combined_data %>%
    mutate(
      rr_list = sapply(rr_intervalls, function(x) {
        if (is.na(x)) return(list(numeric()))
        if (x == "[]") return(list(numeric()))
        
        nums <- gsub("\\[|\\]", "", x) %>%
          strsplit(",") %>%
          `[[`(1) %>%
          trimws() %>%
          as.numeric()
        
        list(nums/1000)
      })
    )
  
  # Create expanded data with beat times
  expanded_data <- processed_data %>%
    unnest(rr_list) %>%
    group_by(session_label, task, round_number) %>%
    group_modify(~{
      bind_rows(
        tibble(rr_list = 0),
        .x
      )
    }) %>%
    mutate(beat_time = lag(cumsum(rr_list), default = 0)) %>%
    arrange(session_label, task, round_number, beat_time)
  
  # Create temporary directory for beat files
  dir_name <- "beat_files"
  if (!dir.exists(dir_name)) {
    dir.create(dir_name)
  }
  
  # Get unique combinations
  combinations <- expanded_data %>%
    select(session_label, task, round_number) %>%
    distinct()
  
  # Write beat files
  for(i in 1:nrow(combinations)) {
    current <- combinations[i,]
    
    current_data <- expanded_data %>%
      filter(
        session_label == current$session_label,
        task == current$task,
        round_number == current$round_number
      )
    
    filename <- file.path(dir_name, 
                          sprintf("%s_%s_round%d.beats", 
                                  current$session_label,
                                  current$task,
                                  current$round_number))
    
    write.table(current_data$beat_time,
                file = filename,
                row.names = FALSE,
                col.names = FALSE,
                quote = FALSE)
  }
  
  # Calculate features for each combination
  all_features <- list()
  
  for(i in 1:nrow(combinations)) {
    current <- combinations[i,]
    
    current_data <- expanded_data %>%
      filter(
        session_label == current$session_label,
        task == current$task,
        round_number == current$round_number
      )
    
    rr_intervals <- diff(current_data$beat_time)
    
    time_features <- calculate_time_features(rr_intervals)
    
    file_name <- sprintf("beat_files/%s_%s_round%d.beats", 
                         current$session_label,
                         current$task,
                         current$round_number)
    
    hrv.data <- CreateHRVData()
    hrv.data <- LoadBeatAscii(hrv.data, file_name)
    hrv.data <- BuildNIHR(hrv.data)
    hrv.data <- FilterNIHR(hrv.data)
    hrv.data <- InterpolateNIHR(hrv.data, freqhr = 4)
    hrv.data <- CreateFreqAnalysis(hrv.data)
    hrv.data <- CalculatePowerBand(hrv.data, 
                                   indexFreqAnalysis = 1,
                                   size = 8, 
                                   shift = 4, 
                                   type = "fourier",
                                   ULFmin = 0, ULFmax = 0.03, 
                                   VLFmin = 0.03, VLFmax = 0.05,
                                   LFmin = 0.05, LFmax = 0.15, 
                                   HFmin = 0.15, HFmax = 0.4)
    
    freq_features <- extract_freq_features(hrv.data)
    nonlinear_features <- calculate_nonlinear_features(rr_intervals)
    r_and_f_features <- calculate_rise_fall_features(rr_intervals)
    
    all_features[[i]] <- c(
      list(
        session_label = current$session_label,
        task = current$task,
        round_number = current$round_number
      ),
      time_features,
      freq_features,
      nonlinear_features,
      r_and_f_features
    )
  }
  
  # Convert features to dataframe
  features_df <- bind_rows(all_features)
  
  # Prepare data for clustering
  current_data <- features_df[feature_set]
  
  # Apply minmax scaling
  scaled_data <- as.data.frame(lapply(current_data, function(x) {
    (x - min(x)) / (max(x) - min(x))
  }))
  
  # Perform clustering
  set.seed(12345)
  km_result <- pam(scaled_data, 2)
  
  # Add clusters to features_df
  features_df$feature_cluster <- km_result$cluster
  
  # Merge clusters back to original data
  result <- combined_data %>%
    left_join(
      features_df %>% 
        select(session_label, task, round_number, feature_cluster),
      by = c("session_label", "task", "round_number")
    )
  
  # Clean up beat files
  unlink(dir_name, recursive = TRUE)
  
  return(result)
}

# Example usage:

feature_set <- list(
  # "all" = names(features_df)[-exclude_cols],  # all features except metadata and sample_entropy
  "time_domain" = c("mean_rr", "sdnn", "rmssd", "nn50", "pnn50", "tri_index", "cv",
                    "max_rise_time", "max_fall_time", "mean_rise_time", "mean_fall_time", "rise_rate", "fall_rate"),
  
  "freq_domain" = c("lf_power", "hf_power", "lf_hf_ratio", "total_power", "peak_lf", "peak_hf", "sd_lf", "sd_hf"),
  
  "nonlinear" = c("sd1", "sd2", "sd1_sd2_ratio"),
  
  # Focused feature combinations
  "variability_focused" = c("sdnn", "rmssd", "sd1", "sd2", "tri_index", "cv", "max_rise_time", "max_fall_time"),
  
  "ratio_based" = c("lf_hf_ratio", "sd1_sd2_ratio", "pnn50", "cv"),
  
  "power_metrics" = c("lf_power", "hf_power", "total_power", "peak_lf", "peak_hf"),
  
  "temporal_and_spectral" = c("sdnn", "rmssd", "lf_power", "hf_power", "lf_hf_ratio", "mean_rise_time", "mean_fall_time"),
  
  "short_term_variability" = c("rmssd", "pnn50", "hf_power", "sd1", "rise_rate", "fall_rate"),
  
  "long_term_variability" = c("sdnn", "lf_power", "sd2", "tri_index"),
  
  "distribution_focused" = c("tri_index", "cv", "sd_lf", "sd_hf", "sdnn"),
  
  "minimal_complete" = c("rmssd", "lf_hf_ratio", "sd1_sd2_ratio", "total_power"),
  
  # Physiological interpretations
  "parasympathetic_focused" = c("rmssd", "pnn50", "hf_power", "sd1", "peak_hf", "sd_hf"),
  
  "sympathetic_focused" = c("lf_power", "sdnn", "sd2", "peak_lf", "sd_lf"),
  
  "peak_and_spread" = c("peak_lf", "peak_hf", "sd_lf", "sd_hf", "tri_index"),
  
  "geometric_measures" = c("tri_index", "sd1", "sd2", "sd1_sd2_ratio"),
  
  "normalized_metrics" = c("cv", "pnn50", "lf_hf_ratio", "sd1_sd2_ratio"),
  
  "power_and_geometry" = c("total_power", "lf_hf_ratio", "sd1", "sd2", "tri_index"),
  
  "composite_variability" = c("sdnn", "rmssd", "tri_index", "total_power", "sd1_sd2_ratio"),
  
  "frequency_detailed" = c("lf_power", "hf_power", "peak_lf", "peak_hf", "sd_lf", "sd_hf", "lf_hf_ratio"),
  
  "time_detailed" = c("mean_rr", "sdnn", "rmssd", "nn50", "pnn50", "tri_index", "cv"),
  
  "robust_metrics" = c("tri_index", "total_power", "sd2", "cv", "mean_rr"),
  
  "statistical_moments" = c("mean_rr", "sdnn", "cv", "tri_index"),
  
  "autonomic_balance" = c("lf_hf_ratio", "sd1_sd2_ratio", "total_power", "rmssd"),
  
  # Dynamic response feature sets
  "dynamic_response" = c("max_rise_time", "max_fall_time", "mean_rise_time", "mean_fall_time", "rise_rate", "fall_rate", "rmssd", "sd1"),
  
  "rate_change_patterns" = c("rise_rate", "fall_rate", "lf_hf_ratio", "sd1_sd2_ratio", "mean_rise_time", "mean_fall_time"),
  
  "acceleration_focused" = c("max_rise_time", "max_fall_time", "peak_lf", "peak_hf", "sd1", "rmssd"),
  
  "temporal_dynamics" = c("mean_rise_time", "mean_fall_time", "sdnn", "tri_index", "total_power", "rise_rate", "fall_rate"),
  
  "change_magnitude" = c("max_rise_time", "max_fall_time", "peak_lf", "peak_hf", "sdnn", "total_power"),
  
  "response_symmetry" = c("rise_rate", "fall_rate", "mean_rise_time", "mean_fall_time", "lf_hf_ratio", "sd1_sd2_ratio"),
  
  "adaptation_metrics" = c("rise_rate", "fall_rate", "rmssd", "sd1", "hf_power", "mean_rise_time", "mean_fall_time")
)


feature_set <- c(feature_set, list(
  # Mental stress indicators - might help identify math-induced stress
  "stress_response" = c("lf_hf_ratio", "mean_rr", "sdnn", "max_rise_time", "rise_rate"),
  
  # Physical engagement patterns - for ball catching activity
  "physical_reactivity" = c("max_fall_time", "sd1", "peak_hf", "mean_rise_time", "rise_rate"),
  
  # Attention and focus metrics
  "cognitive_load" = c("mean_rr", "sd2", "lf_power", "rise_rate", "fall_rate", "pnn50"),
  
  # Emotional state indicators
  "emotional_arousal" = c("sd1", "hf_power", "max_rise_time", "mean_fall_time", "lf_hf_ratio"),
  
  # Quick response patterns - relevant for ball catching
  "quick_adaptation" = c("rmssd", "sd1", "rise_rate", "fall_rate", "mean_rise_time"),
  
  # Anxiety indicators - might be elevated during math
  "anxiety_markers" = c("mean_rr", "sd1", "hf_power", "max_rise_time", "rise_rate"),
  
  # Flow state indicators - might be present during successful ball catching
  "flow_state" = c("sdnn", "total_power", "mean_fall_time", "fall_rate", "sd1_sd2_ratio"),
  
  # Mental effort without stress
  "focused_work" = c("mean_rr", "sd2", "lf_power", "mean_rise_time", "pnn50"),
  
  # Enjoyment indicators
  "positive_engagement" = c("sd1", "hf_power", "mean_fall_time", "fall_rate", "total_power"),
  
  # Task switching ability
  "adaptation_capacity" = c("sd1_sd2_ratio", "max_rise_time", "max_fall_time", "rmssd", "tri_index"),
  
  # Anticipatory response - relevant for ball catching
  "anticipatory" = c("rise_rate", "sd1", "mean_rise_time", "hf_power", "peak_hf"),
  
  # Mental processing load
  "processing_load" = c("mean_rr", "lf_power", "max_rise_time", "sd2", "pnn50"),
  
  # Performance pressure indicators
  "performance_pressure" = c("lf_hf_ratio", "max_rise_time", "sdnn", "rise_rate", "mean_rr"),
  
  # Relaxed engagement state
  "relaxed_focus" = c("sd1", "hf_power", "mean_fall_time", "total_power", "pnn50"),
  
  # Recovery patterns between events
  "inter_event_recovery" = c("mean_fall_time", "fall_rate", "sd1", "hf_power", "rmssd"),
  
  # Readiness for action
  "action_readiness" = c("rise_rate", "max_rise_time", "sd1", "mean_rr", "total_power"),
  
  # Sustained attention
  "sustained_attention" = c("sd2", "lf_power", "mean_rr", "pnn50", "tri_index"),
  
  # Challenge response
  "challenge_response" = c("max_rise_time", "lf_hf_ratio", "sdnn", "rise_rate", "total_power")
))

combined_data <- process_hrv_data(combined_data, feature_set[['parasympathetic_focused']])
