#!/usr/bin/env Rscript
# Nature-style QoS comparison using ggplot2 + patchwork
# Plots three metrics: Throughput, Delay, PLR

library(ggplot2)
library(patchwork)
library(Cairo)

# Nature publication theme
theme_nature <- function() {
  theme_classic(base_size = 7, base_family = "Arial") +
    theme(
      axis.line = element_line(size = 0.4),
      axis.ticks = element_line(size = 0.4),
      axis.text = element_text(size = 6),
      axis.title = element_text(size = 7),
      legend.position = "none",
      strip.background = element_blank(),
      strip.text = element_text(size = 6, face = "bold"),
      panel.grid.major.y = element_line(color = "gray90", size = 0.3),
      panel.grid.major.x = element_blank(),
      plot.margin = margin(5, 5, 5, 5)
    )
}

# Color scheme
colors <- c(
  "LAAVHA" = "#1f77b4",              # deep blue
  "LAAVHA\n(zero HO)" = "#a8d5f7",   # light blue
  "TOPSIS-Q" = "#7f7f7f",            # gray
  "GRA" = "#969696",
  "Strongest-Signal" = "#adadad",
  "VIKOR" = "#bababa"
)

# Load and process data
load_algorithm_data <- function(results_dir, algorithm_name) {
  pattern <- paste0(results_dir, "/", tolower(algorithm_name), "_seed*.csv")
  files <- Sys.glob(pattern)

  if (length(files) == 0) {
    warning(paste("No files found for", algorithm_name))
    return(NULL)
  }

  dfs <- lapply(seq_along(files), function(i) {
    df <- read.csv(files[i])
    df$file_index <- i - 1
    df
  })

  do.call(rbind, dfs)
}

# Calculate QoS metrics based on actual serving network
calculate_qos_metrics <- function(df) {
  # Split by file_index (each file is one run)
  runs <- split(df, df$file_index)

  metrics_list <- lapply(runs, function(run_df) {
    throughputs <- numeric(nrow(run_df))
    delays <- numeric(nrow(run_df))
    plrs <- numeric(nrow(run_df))

    for (i in 1:nrow(run_df)) {
      net <- run_df$current_net[i]

      if (net == 0) {  # 5G
        throughputs[i] <- run_df$throughput_5g[i]
        delays[i] <- run_df$delay_5g[i]
        plrs[i] <- run_df$plr_5g[i]
      } else if (net == 1) {  # LTE
        throughputs[i] <- run_df$throughput_lte[i]
        delays[i] <- run_df$delay_lte[i]
        plrs[i] <- run_df$plr_lte[i]
      } else if (net == 2) {  # WiFi
        throughputs[i] <- run_df$throughput_wifi[i]
        delays[i] <- run_df$delay_wifi[i]
        plrs[i] <- run_df$plr_wifi[i]
      }
    }

    data.frame(
      run_index = run_df$file_index[1],
      avg_throughput = mean(throughputs),
      avg_delay = mean(delays),
      avg_plr = mean(plrs) * 100,  # to percentage
      num_handovers = sum(run_df$handover)
    )
  })

  do.call(rbind, metrics_list)
}

# Extract zero-handover subset
extract_zero_handover <- function(metrics_df) {
  metrics_df[metrics_df$num_handovers == 0, ]
}

# Main execution
results_dir <- "/home/suwen/reproduce/experiments/results"

# Define algorithms to load
algorithms <- c("LAAVHA", "TOPSIS-Q", "GRA", "Strongest-Signal", "VIKOR")

# Load all data
cat("Loading data...\n")
all_metrics <- list()

for (alg in algorithms) {
  df <- load_algorithm_data(results_dir, alg)
  if (!is.null(df)) {
    metrics <- calculate_qos_metrics(df)
    all_metrics[[alg]] <- metrics
    cat(sprintf("%s: %d runs loaded\n", alg, nrow(metrics)))
  }
}

# Extract LAAVHA zero-handover subset
if ("LAAVHA" %in% names(all_metrics)) {
  zero_ho <- extract_zero_handover(all_metrics[["LAAVHA"]])
  all_metrics[["LAAVHA\n(zero HO)"]] <- zero_ho
  cat(sprintf("Found %d zero-handover runs\n", nrow(zero_ho)))
}

# Prepare data for plotting
algorithms_order <- c("LAAVHA", "LAAVHA\n(zero HO)", "TOPSIS-Q",
                      "GRA", "Strongest-Signal", "VIKOR")
algorithms_order <- algorithms_order[algorithms_order %in% names(all_metrics)]

# Combine all metrics into long format
plot_data <- do.call(rbind, lapply(names(all_metrics), function(alg) {
  df <- all_metrics[[alg]]
  df$algorithm <- alg
  df
}))

# Ensure factor ordering
plot_data$algorithm <- factor(plot_data$algorithm, levels = algorithms_order)

# Create three subplots
p1 <- ggplot(plot_data, aes(x = algorithm, y = avg_throughput, fill = algorithm)) +
  geom_violin(alpha = 0.6, color = "black", size = 0.3, width = 0.7) +
  geom_jitter(aes(color = algorithm), width = 0.1, size = 1.5, alpha = 0.7,
              stroke = 0.2, shape = 21, fill = NA) +
  stat_summary(fun = mean, geom = "crossbar", width = 0.5,
               size = 0.3, color = "black", fatten = 2) +
  scale_fill_manual(values = colors) +
  scale_color_manual(values = colors) +
  labs(x = NULL, y = "Throughput (Mbps)") +
  theme_nature() +
  scale_x_discrete(labels = function(x) paste0(x, "\n(n=",
                                                sapply(x, function(a) sum(plot_data$algorithm == a)), ")"))

p2 <- ggplot(plot_data, aes(x = algorithm, y = avg_delay, fill = algorithm)) +
  geom_violin(alpha = 0.6, color = "black", size = 0.3, width = 0.7) +
  geom_jitter(aes(color = algorithm), width = 0.1, size = 1.5, alpha = 0.7,
              stroke = 0.2, shape = 21, fill = NA) +
  stat_summary(fun = mean, geom = "crossbar", width = 0.5,
               size = 0.3, color = "black", fatten = 2) +
  scale_fill_manual(values = colors) +
  scale_color_manual(values = colors) +
  labs(x = NULL, y = "Delay (ms)") +
  theme_nature() +
  scale_x_discrete(labels = function(x) paste0(x, "\n(n=",
                                                sapply(x, function(a) sum(plot_data$algorithm == a)), ")"))

p3 <- ggplot(plot_data, aes(x = algorithm, y = avg_plr, fill = algorithm)) +
  geom_violin(alpha = 0.6, color = "black", size = 0.3, width = 0.7) +
  geom_jitter(aes(color = algorithm), width = 0.1, size = 1.5, alpha = 0.7,
              stroke = 0.2, shape = 21, fill = NA) +
  stat_summary(fun = mean, geom = "crossbar", width = 0.5,
               size = 0.3, color = "black", fatten = 2) +
  scale_fill_manual(values = colors) +
  scale_color_manual(values = colors) +
  labs(x = NULL, y = "Packet Loss Rate (%)") +
  theme_nature() +
  scale_x_discrete(labels = function(x) paste0(x, "\n(n=",
                                                sapply(x, function(a) sum(plot_data$algorithm == a)), ")"))

# Combine panels with patchwork
combined <- p1 + p2 + p3 +
  plot_annotation(tag_levels = 'a', tag_suffix = ')') &
  theme(plot.tag = element_text(size = 9, face = "bold"))

# Save outputs
output_dir <- "/home/suwen/reproduce/vehicular_communications_submission/figures"
dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)

output_base <- file.path(output_dir, "qos_comparison_ggplot2")

# PDF output
cat("\nSaving PDF...\n")
Cairo(file = paste0(output_base, ".pdf"), type = "pdf",
      width = 7.2, height = 2.4, units = "in", dpi = 300)
print(combined)
dev.off()

# PNG output
cat("Saving PNG...\n")
Cairo(file = paste0(output_base, ".png"), type = "png",
      width = 7.2, height = 2.4, units = "in", dpi = 300)
print(combined)
dev.off()

cat("\n✓ Figures saved:\n")
cat(sprintf("  - %s.pdf\n", output_base))
cat(sprintf("  - %s.png\n", output_base))

# Print summary statistics
cat("\n=== Summary Statistics ===\n\n")
for (alg in algorithms_order) {
  if (alg %in% names(all_metrics)) {
    metrics <- all_metrics[[alg]]
    cat(sprintf("%s (n=%d):\n", alg, nrow(metrics)))
    cat(sprintf("  Throughput: %.2f ± %.2f Mbps\n",
                mean(metrics$avg_throughput), sd(metrics$avg_throughput)))
    cat(sprintf("  Delay: %.2f ± %.2f ms\n",
                mean(metrics$avg_delay), sd(metrics$avg_delay)))
    cat(sprintf("  PLR: %.3f ± %.3f %%\n\n",
                mean(metrics$avg_plr), sd(metrics$avg_plr)))
  }
}
