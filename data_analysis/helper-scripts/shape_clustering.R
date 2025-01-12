time_series_data = df_to_ts(ball_task, math_task)


clustering <- tsclust(time_series_data, type="p", distance="dtw", k=2, centroid="pam", args = list(dist.params = list(window.size = 20)))

# Usage:
# plot_ts_clusters(ts_cluster_data, clustering, k = 2)


# First, let's extract the cluster assignments
cluster_assignments <- clustering@cluster

# Create a mapping dataframe from the metadata we stored
mapping_df <- attr(time_series_data, "metadata") %>%
  mutate(
    shape_cluster = cluster_assignments,  # Changed name here
    # Recreate the names to match with how we named the time series
    ts_name = paste(session_label, round_number, task)
  )

# Now we can join this back to the original combined data
combined_data <- bind_rows(
  ball_task %>% mutate(task = "ball"),
  math_task %>% mutate(task = "math")
)

# Add the cluster information
combined_data <- combined_data %>%
  left_join(
    mapping_df %>% select(session_label, round_number, task, shape_cluster),  # Changed here
    by = c("session_label", "round_number", "task")
  )
