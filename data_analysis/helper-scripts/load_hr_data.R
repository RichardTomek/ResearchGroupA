# Essential the same steps as we are doing in main.Rmd but allows us to load the data in another notebook without having to copy all the code

file_mapping <- c(
  "ball_task_lab_run_18_12.csv" = "ball_task",
  "math_task_lab_run_18_12.csv" = "math_task",
  "video_one_lab_run_18_12.csv" = "video_one",
  "video_two_lab_run_18_12.csv" = "video_two"
)

# Read all files and assign them to the workspace with desired names
walk2(
  names(file_mapping),
  file_mapping,
  ~assign(
    .y,
    read_csv(here("data", .x)),
    envir = .GlobalEnv
  )
)

video_one <- video_one %>%
  mutate(session_label = paste(session_code, label, sep = "_")) %>%
  group_by(session_label) %>%
  mutate(heart_rate_z = (heart_rate - mean(heart_rate, na.rm = TRUE)) / sd(heart_rate, na.rm = TRUE)) %>%
  mutate(
    time_recorded = ymd_hms(time_recorded),
    # Calculate time elapsed in minutes from first recording of each session
    time_elapsed = as.numeric(
      difftime(time_recorded, 
               min(time_recorded),
               units = "sec")
    )
  ) %>%
  ungroup()

video_two <- video_two %>%
  mutate(session_label = paste(session_code, label, sep = "_")) %>%
  group_by(session_label) %>%
  mutate(heart_rate_z = (heart_rate - mean(heart_rate, na.rm = TRUE)) / sd(heart_rate, na.rm = TRUE)) %>%
  mutate(
    time_recorded = ymd_hms(time_recorded),
    # Calculate time elapsed in minutes from first recording of each session
    time_elapsed = as.numeric(
      difftime(time_recorded, 
               min(time_recorded),
               units = "sec")
    )
  ) %>%
  ungroup()

ball_task <- ball_task %>%
  mutate(session_label = paste(session_code, label, sep = "_")) %>%
  group_by(session_label, round_number) %>%
  mutate(heart_rate_z = (heart_rate - mean(heart_rate, na.rm = TRUE)) / sd(heart_rate, na.rm = TRUE)) %>%
  mutate(
    time_recorded = ymd_hms(time_recorded),
    # Calculate time elapsed in minutes from first recording of each session
    time_elapsed = as.numeric(
      difftime(time_recorded, 
               min(time_recorded),
               units = "sec")
    )
  ) %>%
  ungroup()

math_task <- math_task %>%
  mutate(session_label = paste(session_code, label, sep = "_")) %>%
  group_by(session_label, round_number) %>%
  mutate(heart_rate_z = (heart_rate - mean(heart_rate, na.rm = TRUE)) / sd(heart_rate, na.rm = TRUE)) %>%
  mutate(
    time_recorded = ymd_hms(time_recorded),
    # Calculate time elapsed in minutes from first recording of each session
    time_elapsed = as.numeric(
      difftime(time_recorded, 
               min(time_recorded),
               units = "sec")
    )
  ) %>%
  ungroup()

# This first calculates the correct round number and then re-calculates the normalized HR and elapsed time based on the new round numbers
ball_task <- ball_task %>%
  # First ensure data is ordered chronologically within each participant
  arrange(session_label, time_recorded) %>%
  group_by(session_label) %>%
  mutate(
    # Calculate time difference between consecutive readings
    time_diff = as.numeric(difftime(
      time_recorded, 
      lag(time_recorded, default = first(time_recorded)),
      units = "secs"
    )),
    # Create new round numbers based on gaps > 10s
    round_number = cumsum(time_diff > 10 | row_number() == 1)
  ) %>%
  # Now recalculate z-scores and time_elapsed based on new rounds
  group_by(session_label, round_number) %>%
  mutate(
    heart_rate_z = (heart_rate - mean(heart_rate, na.rm = TRUE)) / sd(heart_rate, na.rm = TRUE),
    time_elapsed = as.numeric(
      difftime(time_recorded, 
               min(time_recorded),
               units = "sec")
    )
  ) %>%
  ungroup()


math_task <- math_task %>%
  # First ensure data is ordered chronologically within each participant
  arrange(session_label, time_recorded) %>%
  group_by(session_label) %>%
  mutate(
    # Calculate time difference between consecutive readings
    time_diff = as.numeric(difftime(
      time_recorded, 
      lag(time_recorded, default = first(time_recorded)),
      units = "secs"
    )),
    # Create new round numbers based on gaps > 10s
    round_number = cumsum(time_diff > 10 | row_number() == 1)
  ) %>%
  # Now recalculate z-scores and time_elapsed based on new rounds
  group_by(session_label, round_number) %>%
  mutate(
    heart_rate_z = (heart_rate - mean(heart_rate, na.rm = TRUE)) / sd(heart_rate, na.rm = TRUE),
    time_elapsed = as.numeric(
      difftime(time_recorded, 
               min(time_recorded),
               units = "sec")
    )
  ) %>%
  ungroup()

# Create combined DF
combined_task_data <- bind_rows(
  ball_task %>% mutate(task = "ball"),
  math_task %>% mutate(task = "math")
)

# Modified data preparation function
df_to_ts <- function(ball_task, math_task) {
  combined_data <- bind_rows(
    ball_task %>% mutate(task = "ball"),
    math_task %>% mutate(task = "math")
  )
  
  ts_list <- combined_data %>%
    group_by(session_label, round_number, task) %>%
    arrange(time_elapsed) %>%
    summarise(
      ts = list(as.numeric(heart_rate_z)),  # Explicitly convert to numeric
      .groups = "drop"
    )
  
  # Convert to a list of numeric vectors
  ts_data <- ts_list$ts
  names(ts_data) <- paste(ts_list$session_label, ts_list$round_number, ts_list$task)
  
  # Verify data is numeric
  if(!all(sapply(ts_data, is.numeric))) {
    stop("Not all time series are numeric")
  }
  
  # Store metadata
  attr(ts_data, "metadata") <- ts_list %>% select(-ts)
  
  return(ts_data)
}