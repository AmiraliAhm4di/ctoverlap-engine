# Final report
# This script reads the exported CSV files and creates the final report plots and summary tables

library(dplyr)
library(ggplot2)
library(here)
library(readr)



output_tables <- here("outputs", "tables")
output_figures <- here("outputs", "figures")
output_report <- here("outputs", "report")
dir.create(output_figures, showWarnings = FALSE)
dir.create(output_report, showWarnings = FALSE)

# load the exported data
monthly_density <- read_csv(file.path(output_tables, "monthly_density_by_condition.csv"))
phase_density <- read_csv(file.path(output_tables, "monthly_density_by_condition_phase.csv"))
country_density <- read_csv(file.path(output_tables, "monthly_density_by_condition_country.csv"))
intervention_density <- read_csv(file.path(output_tables, "monthly_density_by_condition_intervention_type.csv"))

# convert the month columns into dates
monthly_density$month <- as.Date(paste0(monthly_density$month, "-01"))
phase_density$month <- as.Date(paste0(phase_density$month, "-01"))
country_density$month <- as.Date(paste0(country_density$month, "-01"))
intervention_density$month <- as.Date(paste0(intervention_density$month, "-01"))

cond_colors <- c("breast cancer" = "#F8766D", "colorectal cancer" = "#00BA38", "melanoma" = "#619CFF")




# keep the highest activity month for each condition
peaks <- monthly_density %>% group_by(condition_query) %>% slice_max(active_trial_count, n=1, with_ties=FALSE)
peaks$label <- paste0(peaks$active_trial_count, " trials\n", format(peaks$month, "%b %Y"))
peaks$label_y <- peaks$active_trial_count + rank(peaks$active_trial_count) * 20
last_active_month <- max(monthly_density$month[monthly_density$active_trial_count > 5])

p1 <- ggplot(monthly_density, aes(x = month, y = active_trial_count, color = condition_query)) +
  geom_line(size = 0.9) +
  geom_point(data = peaks, size = 2.5) +
  geom_text(data = peaks, aes(label = label, y = label_y), vjust = 0, size = 3.2, show.legend = F) +
  ylim(0, max(monthly_density$active_trial_count) * 1.3) +
  scale_color_manual(values = cond_colors) +
  scale_x_date(date_breaks = "5 years", date_labels = "%Y") +
  coord_cartesian(xlim = c(min(monthly_density$month), last_active_month)) +
  labs(title = "Monthly Active Clinical Trials by Cancer Condition",
       x = "Month", y = "Number of active trials", color = "Condition") +
  theme_minimal()

ggsave(file.path(output_figures, "monthly_trial_density_by_condition.png"), p1, width = 9, height = 5)

# make and export the peak summary table
peak_summary <- monthly_density %>%
  group_by(condition_query) %>%
  slice_max(active_trial_count, n = 1, with_ties = FALSE) %>%
  select(condition_query, month, active_trial_count, trial_count_total)
peak_summary$peak_year <- format(peak_summary$month, "%Y")
print(peak_summary)
write_csv(peak_summary, file.path(output_report, "peak_density_summary.csv"))



# find the peak for each condition and phase
phase_peak <- phase_density %>%
  filter(group_analyzed == TRUE, phase_bucket != "Unspecified / Not Applicable") %>%
  group_by(condition_query, phase_bucket) %>%
  slice_max(active_trial_count, n = 1, with_ties = FALSE)

phase_peak$bar_label <- paste0(phase_peak$active_trial_count, "\n", format(phase_peak$month, "%Y"))

p2 <- ggplot(phase_peak, aes(x = phase_bucket, y = active_trial_count, fill = condition_query)) +
  geom_col(position = "dodge") +
  geom_text(aes(label = bar_label), position = position_dodge(width = 0.9), vjust = -0.25, size = 3) +
  scale_fill_manual(values = cond_colors) +
  labs(title = "Peak Concurrent Trial Activity by Phase", x = "Trial phase", y = "Peak active trials", fill = "Condition") +
  theme_minimal() +
  scale_y_continuous(expand = expansion(mult = c(0, 0.12))) +
  theme(plot.title = element_text(face = "bold", size = 14),
      panel.grid.minor = element_blank())

ggsave(file.path(output_figures, "peak_trial_density_by_phase.png"), p2, width = 11, height = 6.5)




# keep the top ten countries for each condition
country_peak <- country_density %>%
  filter(group_analyzed == TRUE, !is.na(country)) %>%
  group_by(condition_query, country) %>%
  slice_max(active_trial_count, n = 1, with_ties = FALSE) %>%
  group_by(condition_query) %>%
  slice_max(active_trial_count, n = 10, with_ties = FALSE) %>%
  ungroup()


p3 <- ggplot(country_peak, aes(x = reorder(country, active_trial_count), y = active_trial_count, fill = condition_query)) +
  geom_col() +
  geom_text(aes(label = active_trial_count), hjust = -0.1, size = 3) +
  coord_flip() +
  facet_wrap(~condition_query, scales = "free_y") +
  scale_fill_manual(values = cond_colors) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.15))) +
  labs(title = "Countries With the Highest Concurrent Trial Activity", x = "", y = "Peak active trials") +
  guides(fill = "none") +
  theme_minimal()


ggsave(file.path(output_figures, "top_countries_by_peak_trial_density.png"), p3, width = 12, height = 8)



# clean the intervention names and keep the top ten for each condition
intervention_peak <- intervention_density %>%
  filter(group_analyzed == TRUE, !is.na(intervention_type)) %>%
  mutate(intervention_label = tools::toTitleCase(tolower(gsub("_", " ", intervention_type)))) %>%
  group_by(condition_query, intervention_type) %>%
  slice_max(active_trial_count, n = 1, with_ties = FALSE) %>%
  group_by(condition_query) %>%
  slice_max(active_trial_count, n = 10, with_ties = FALSE)
intervention_peak <- ungroup(intervention_peak)

p4 <- ggplot(intervention_peak, aes(x = reorder(intervention_label, active_trial_count), y = active_trial_count, fill = condition_query)) +
  geom_col() +
  geom_text(aes(label = active_trial_count), hjust = -0.1, size = 3) +
  coord_flip() +
  facet_wrap(~condition_query, scales = "free_y") +
  scale_fill_manual(values = cond_colors) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.15))) +
  labs(title = "Highest Concurrent Trial Activity by Intervention Type", x = "", y = "Peak active trials") +
  guides(fill = "none") +
  theme_minimal()

ggsave(file.path(output_figures, "top_intervention_types_by_peak_density.png"), p4, width = 12, height = 8, dpi = 300)



benchmark_results <- read_csv(file.path(output_tables, "benchmark_results.csv"))

benchmark_summary <- benchmark_results %>%
  select(condition, trial_count, sweep_line_runtime, brute_force_runtime, speedup, outputs_match) %>%
  mutate(sweep_line_ms = round(sweep_line_runtime * 1000, 1),
         brute_force_ms = round(brute_force_runtime * 1000, 1),
         speedup = round(speedup, 2))

print(benchmark_summary)
write_csv(benchmark_summary, file.path(output_report, "benchmark_summary.csv"))


# combine both runtimes so they can be plotted together
bench_long <- bind_rows(
  data.frame(condition = benchmark_summary$condition, method = "Sweep-line",
             runtime_ms = benchmark_summary$sweep_line_ms),
  data.frame(condition = benchmark_summary$condition, method = "Brute force",
             runtime_ms = benchmark_summary$brute_force_ms)
)


p5 <- ggplot(bench_long, aes(x = condition, y = runtime_ms, fill = method)) +
  geom_col(position = "dodge") +
  geom_text(aes(label = paste0(runtime_ms, " ms")), position = position_dodge(width = 0.9), vjust = -0.3, size = 3.5) +
  labs(title = "Sweep-Line vs Brute-Force Runtime", x = "Condition", y = "Runtime (ms)", fill = "Method") +
  theme_minimal() +
  theme(legend.position = "top")

ggsave(file.path(output_figures, "sweep_line_runtime_comparison.png"), p5, width = 8, height = 5.5)

print("done processing")
