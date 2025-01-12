setwd("./helper-scripts")

library(here)
source("./load_packages.R")

required_packages <- c("tidyverse", "dtwclust", "RHRV")

# Call the function with your package vector
load_packages(required_packages)

source("./plotting.R")

source("./load_hr_data.R")
source("./shape_clustering.R")
source("./feature_clustering.R")




setwd("../")
