# Function for plotting HR data
plot_heart_rate <- function(data, x, y, group, title, subtitle, x_label, y_label, legend_title) {
  ggplot(data, aes_string(x = x, y = y)) +
    # Add individual session lines and points with very low opacity
    geom_point(aes_string(color = group), alpha = 0.1) +
    geom_line(aes_string(color = group, group = group), alpha = 0.1) +
    # Add smoothed trend line for each session with low opacity using stat_smooth
    stat_smooth(
      aes_string(color = group, group = group),
      geom = "line",
      method = "loess",
      alpha = 0.5,
      se = FALSE
    ) +
    # Add overall trend line (black) with higher opacity
    stat_smooth(
      color = "black",
      geom = "line",
      method = "loess",
      alpha = 0.8,
      se = TRUE,
      linewidth = 1.2
    ) +
    # Customize the appearance
    theme_minimal() +
    labs(
      title = title,
      subtitle = subtitle,
      x = x_label,
      y = y_label,
      color = legend_title
    ) +
    theme(
      legend.position = "right",
      panel.grid.minor = element_blank(),
      plot.title = element_text(hjust = 0.5, size = 14, face = "bold"),
      plot.subtitle = element_text(hjust = 0.5, size = 12),
      axis.title = element_text(size = 12),
      legend.title = element_text(size = 12),
      legend.text = element_text(size = 10)
    ) +
    # Use a colorblind-friendly palette
    scale_color_viridis_d()
}

plot_ts_clusters <- function(ts_data, clustering, k = 2) {
  # Handle cluster assignments based on clustering type
  if (inherits(clustering, "PartitionalTSClusters")) {
    # For partitional clustering, create a named vector of cluster assignments
    cluster_assignments <- setNames(
      clustering@cluster,
      names(ts_data)
    )
    use_centroids <- TRUE
    centroids <- clustering@centroids
  } else {
    # For hierarchical clustering, cluster assignments are already named
    cluster_assignments <- clustering@cluster
    use_centroids <- FALSE
  }
  
  # Convert the list of time series to a long format dataframe
  df <- do.call(rbind, lapply(names(ts_data), function(name) {
    data.frame(
      time = seq_along(ts_data[[name]]),
      value = ts_data[[name]],
      series = name,
      task = ifelse(grepl("math", name), "math", "ball"),
      cluster = cluster_assignments[name],
      row.names = NULL
    )
  }))
  
  # Create base plot
  p <- ggplot(df, aes(x = time, y = value)) +
    geom_line(aes(group = series, color = task), alpha = 0.2, linewidth = 0.8) +
    scale_color_manual(values = c(
      "ball" = "#1F77B4",
      "math" = "#FF7F0E"
    ))
  
  # Add either centroids or smoothed line based on clustering type
  if (use_centroids) {
    # Convert centroids to data frame for plotting
    centroid_df <- do.call(rbind, lapply(1:length(centroids), function(i) {
      data.frame(
        time = seq_along(centroids[[i]]),
        value = centroids[[i]],
        cluster = i
      )
    }))
    
    p <- p + geom_line(data = centroid_df, 
                       aes(x = time, y = value, group = 1),
                       color = "black",
                       alpha = 0.7,
                       linewidth = 0.8)
  } else {
    p <- p + stat_smooth(
      aes(group = 1),
      color = "black",
      method = "loess",
      se = TRUE,
      alpha = 0.7,
      linewidth = 0.8
    )
  }
  
  # Add remaining plot elements
  p + facet_wrap(~cluster, ncol = 1, 
                 labeller = labeller(cluster = function(x) paste("Cluster", x))) +
    theme_minimal() +
    theme(
      panel.grid.minor = element_blank(),
      panel.grid.major.x = element_blank(),
      panel.grid.major.y = element_line(color = "gray90"),
      text = element_text(family = "Arial"),
      plot.title = element_text(hjust = 0.5, size = 14, face = "bold"),
      plot.subtitle = element_text(hjust = 0.5, size = 12),
      axis.title = element_text(size = 12),
      legend.title = element_text(size = 12),
      legend.text = element_text(size = 10),
      legend.position = "right",
      strip.text = element_text(size = 12, face = "bold")
    ) +
    labs(
      title = "Time Series Clusters by Task Type",
      x = "Time Point",
      y = "Value",
      color = "Task Type"
    )
}
