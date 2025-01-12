# Load & Install packages based on a vector of strings
load_packages <- function(packages) {
  # Loop through each package
  lapply(packages, function(pkg) {
    # Check if package is installed
    if (!require(pkg, character.only = TRUE, quietly = TRUE)) {
      # If not installed, install it
      message(sprintf("Installing package: %s", pkg))
      install.packages(pkg, dependencies = TRUE)
      # Load the newly installed package
      library(pkg, character.only = TRUE)
    } else {
      # If already installed, just load it
      message(sprintf("Loading package: %s", pkg))
    }
  })
}
