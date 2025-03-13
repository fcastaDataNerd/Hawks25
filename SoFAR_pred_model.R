## Model for predicting NECBL STATS SO FAR

##BAtters
necbl_hitters <- read_csv('all_hitters_NECBL.csv')
all_bat1 <- read_csv('allbat11.csv')

all_bat1<- all_bat1 %>%
  mutate(nameyear = paste(Name,year))

necbl_hitters<- necbl_hitters %>%
  mutate(nameyear = paste(Name,Year))


comb_bat <- left_join(necbl_hitters, all_bat1, by = "nameyear")

comb_bat <- comb_bat %>%
  mutate(real_conf______ = ifelse(division == 1, conference, division))
###
model1 <- lm(NECBL_OPS ~ as.factor(real_conf______) + GP+H + HR + K + RBI + BA + OBPct + SlgPct + Yr
             ,data = comb_bat)

summary(model1)
###

comb_bat1 <- na.omit(comb_bat)

library(randomForest)
library(caret)
library(ggplot2)

# Define the formula
formula <- NECBL_OPS ~ as.factor(real_conf______) + GP + H + HR + K + RBI + BA + OBPct + SlgPct + Yr

comb_bat <- comb_bat %>%
  filter(!is.na(NECBL_OPS))

sum(is.na(comb_bat$NECBL_OPS))


# Set up 5-fold cross-validation
train_control <- trainControl(method = "cv", number = 5)

# Define the grid of hyperparameters to tune
tune_grid <- expand.grid(
  mtry = c(2, 4, 6, 8),  # Number of variables randomly sampled at each split
  ntree = c(100, 500, 1000)  # Number of trees in the forest
)

# Train the Random Forest model with grid search
rf_model <- train(
  formula,
  data = comb_bat,
  method = "rf",
  trControl = train_control,
  tuneGrid = tune_grid,
  importance = TRUE
)

# Print best model
print(rf_model)

# Get feature importance
importance_values <- varImp(rf_model, scale = TRUE)

# Plot feature importance
ggplot(importance_values) + 
  geom_bar(stat = "identity", aes(x = reorder(rownames(importance_values$importance), importance_values$importance[,1]), y = importance_values$importance[,1])) + 
  coord_flip() +
  labs(title = "Feature Importance", x = "Features", y = "Importance Score") +
  theme_minimal()



##### Pitchers
d1_pit <- read_csv('d1_pitching_2223.csv')
d2_pit <- read_csv('d2_pitching_2223.csv')
all_pit <- bind_rows(d1_pit, d2_pit)

write_csv(all_pit, 'allpitcsv1.csv')
all_pit <- read_csv('allpitcsv11.csv')


all_pit<- all_pit %>%
  mutate(nameyear = paste(Name,year))

necbl_pitchers <- read_csv('all_pitchers.csv')

necbl_pitchers<- necbl_pitchers %>%
  mutate(nameyear = paste(Name,Year))

all_pit<- all_pit %>%
  mutate(nameyear = paste(Name,year))


comb_pit <- left_join(necbl_pitchers, all_pit, by = "nameyear")

comb_pit <- comb_pit %>%
  mutate(real_conf______ = ifelse(division == 1, conference, division))

model1 <- lm(ERA.x ~ as.factor(real_conf______) + App + ERA.y + BB.y + SO.y +BF.y +Yr
             ,data = comb_pit)

summary(model1)

### Work on RF MODEL