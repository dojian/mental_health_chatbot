load.package <- function (package1, ...)  {   
  packages <- c(package1, ...)
  # Loop through vector of packages. If it is installed, load. 
  # If not, install then load.
  for(package in packages){
    if(package %in% rownames(installed.packages()))
      do.call('library', list(package))
    else {
      if(package == "d3heatmap"){
        install.packages("devtools")
        devtools::install_github("rstudio/d3heatmap", dependencies = T)
      }
      else{
        install.packages(package, repos = "http://cran.us.r-project.org")
        do.call("library", list(package))
      }
    }
  } 
}

load.package("dplyr", "tidyr", "data.table", "ggplot2", "stringr", "openxlsx", "highcharter", "knitr", "DT", "heatmaply", "plotly", "kableExtra")

setwd("C:/Users/jfan/Desktop/w210")
df = fread("esconv_processed.csv")


### VIZ 1: # Conversation Turns per Session ### 
n_turns = df %>% group_by(convo_id) %>% summarize(turns = max(num_turns))
n_turns_min = min(n_turns$turns)
n_turns_max = max(n_turns$turns)
n_turns_med = median(n_turns$turns)
hist_turns = n_turns %>% group_by(turns) %>% summarize(count = n()) %>% mutate(percent = round(count / nrow(n_turns) * 100, 1))

### VIZ 2: Session Problem Type Distribution
pt = df %>% group_by(convo_id) %>% summarize(problem_type = first(problem_type))
n_pt = pt %>% group_by(problem_type) %>% summarize(count = n()) %>% mutate(percent = round(count / nrow(n_turns) * 100, 1))
n_pt = n_pt[order(n_pt$count, decreasing =T),]
n_pt$problem_type = str_replace_all(n_pt$problem_type, "_", " ") %>% str_to_title()

### VIZ 3: Session Emotion Type Distribution 
et = df %>% group_by(convo_id) %>% summarize(emotion_type = first(emotion_type))
n_et = et %>% group_by(emotion_type) %>% summarize(count = n()) %>% mutate(percent = round(count / nrow(n_turns) * 100, 1))
n_et = n_et[order(n_et$count, decreasing =T),]
n_et$emotion_type = str_replace_all(n_et$emotion_type, "_", " ") %>% str_to_title()

### VIZ 4: Initial and Final Emotional Intensity Change 
emotion_initial_final = df %>% group_by(convo_id) %>% summarize(emotion_intensity_initial = first(emotion_intensity_initial), emotion_intensity_final = first(emotion_intensity_final))
source = "emotion_intensity_initial"
target = "emotion_intensity_final"
flow_counts_source = emotion_initial_final %>% group_by(emotion_intensity_initial) %>% summarize(n = n()) %>% data.frame()
colnames(flow_counts_source) = c(source, "n_source")
flow_counts_source$label = paste0("Initial (", flow_counts_source$emotion_intensity_initial, "): ", flow_counts_source$n)
flow_counts_target = emotion_initial_final %>% group_by(emotion_intensity_final) %>% summarize(n = n()) %>% data.frame()
colnames(flow_counts_target) = c(target, "n_target")
#flow_counts_target = rbind(flow_counts_target, data.frame(emotion_intensity_final = 5, n_target = 0))
flow_counts_target$label = paste0("Final (", flow_counts_target$emotion_intensity_final, "): ", flow_counts_target$n)

flow_stats = emotion_initial_final %>% group_by(across(all_of(c("emotion_intensity_initial", "emotion_intensity_final")))) %>% summarize(n = n())
flow_stats = merge(flow_stats, flow_counts_source, by = source, all.x = T)
#flow_stats = rbind(flow_stats, data.frame(emotion_intensity_initial = 5, emotion_intensity_final = 5, n = 0, n_source = 278, label = "Initial (5): 278"))
flow_stats$percent_source = round(flow_stats$n / flow_stats$n_source * 100, 1)
flow_stats$percent_total = round(flow_stats$n/(sum(flow_stats$n)) * 100, 1)

for(i in 2:5){
  for(j in 1:4){
    count = flow_stats[flow_stats[,source] == i & flow_stats[,target] == j, "n"]
    percent = flow_stats[flow_stats[,source] == i & flow_stats[,target] == j, "percent_source"]
    if(length(count) == 0){
      count = 0
      percent = 0
    }
    assign(paste0("fc_", i, "_", j), count)
    assign(paste0("fp_", i, "_", j), percent)
  }
}
node_labels = c(flow_counts_source[order(flow_counts_source[,source], decreasing = T), "label"],
                flow_counts_target[order(flow_counts_target[,target], decreasing = T), "label"])
node_labels = factor(node_labels, levels = node_labels)

# There are no sessions in which the emotion intensity grew from initial
link_values = c(fc_5_4, fc_5_3, fc_5_2, fc_5_1,
                fc_4_3, fc_4_2, fc_4_1, 
                fc_3_2, fc_3_1, fc_2_1) 
link_labels = c(fp_5_4, fp_5_3, fp_5_2, fp_5_1, 
                fp_4_3, fp_4_2, fp_4_1, 
                fp_3_2, fp_3_1, fp_2_1)

link_labels = paste0(link_values, " (", link_labels, "%)")

nodes = list(
  pad = 50,
  thickness = 20,
  line = list(
    color = "black",
    width = 0.5
  ),
  label = node_labels,
  hovertemplate = "%{label}<extra></extra>"
)
#Create links
links = list(
  source = c(0,0,0,0,1,1,1,2,2,3),
  target = c(4,5,6,7,5,6,7,6,7,7), # 4 is 4, 5 is 3, 6 is 2, 7 is 1
  value =  link_values,
  label = link_labels
)

### VIZ 5: Counselor Strategies Frequency
all_strategies = data.frame(strategy = df$strategy %>% str_split(", ") %>% unlist)
n_strategies_all = all_strategies %>% group_by(strategy) %>% summarize(count = n()) %>% mutate(percent = round(count / nrow(all_strategies) * 100, 1), group = "All")
n_strategies_all = n_strategies_all[order(n_strategies_all$count, decreasing =T),]
n_strategies_first = df %>% group_by(first_strategy) %>% summarize(count = n()) %>% mutate(percent = round(count / nrow(df) * 100, 1), group = "First Strategy") %>% rename("strategy" = "first_strategy")
n_strategies = rbind(n_strategies_all, n_strategies_first)

### VIZ 6: # Strategies used per turn 
strategies_count_turn = sapply(df$strategy %>% str_split(", "), length)
n_strategies_turn1 = sum(strategies_count_turn == 1)
n_strategies_turn2 = sum(strategies_count_turn == 2)
n_strategies_turn3 = sum(strategies_count_turn >= 3)
n_strategies_turn = data.frame(n_strategies = c("1", "2", "3+"), count = c(n_strategies_turn1, n_strategies_turn2, n_strategies_turn3)) %>% mutate(percent = round(count / length(strategies_count_turn) * 100, 1)) 

### VIZ 7: Common Sequence of Strategies Used (If counselor use multiple strategies)
mult_strategies = df[strategies_count_turn > 1,]
top_10_strats = mult_strategies %>% group_by(strategy) %>% summarize(Count = n()) %>% mutate(Percent = round(Count / sum(Count) * 100, 1))
top_10_strats = top_10_strats[order(top_10_strats$Count, decreasing= T),] %>% head(10)

### VIZ 8: Strategies Breakdown by Turn
strat_turn = df %>% group_by(num_turns, first_strategy) %>% summarize(count = n()) %>% mutate(percent = round(count / sum(count) * 100, 1))

### VIZ 9: User Turn Emotion and Strategy Used 
emotion_strategy = df %>% group_by(user_turn_emotion, first_strategy) %>% summarize(count = n()) %>% mutate(percent = round(count / sum(count) * 100, 1))
