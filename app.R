library(shiny)
library(tidyverse)
library(DT)
library(plotly)

pitch_df <- read_csv("NECBL_2024_Pitches.csv", show_col_types = FALSE)
pitching_df <- read_csv("necbl_combined_pitching_stats.csv", show_col_types = FALSE)
batting_df <- read_csv("necbl_combined_batting_stats.csv", show_col_types = FALSE)

# UI
ui <- fluidPage(
  titlePanel("NECBL 2024 Dashboard"),
  
  tabsetPanel(
    tabPanel("Pitching Dashboard",
             br(),
             selectInput("selected_pitcher", "Select Pitcher:",
                         choices = unique(na.omit(pitch_df$Pitcher))),
             DTOutput("pitch_table"),
             plotlyOutput("pitch_plot", height = "500px")
    ),
    
    tabPanel("Batting Percentiles",
             br(),
             fluidRow(
               column(4,
                      numericInput("minPA", "Minimum PA:", value = 0, min = 0, step = 10)
               ),
               column(4,
                      selectInput("team", "Select Team:",
                                  choices = c("All", unique(batting_df$Team)),
                                  selected = "All")
               )
             ),
             DTOutput("batting_table")
    ),
    
    tabPanel("Pitching Percentiles",
             br(),
             fluidRow(
               column(4,
                      numericInput("minIP", "Minimum IP:", value = 0, min = 0, step = 5)
               ),
               column(4,
                      selectInput("pitch_team", "Select Team:",
                                  choices = c("All", unique(pitching_df$Team)),
                                  selected = "All")
               )
             ),
             DTOutput("pitching_percentiles_table")
    )
  )
)

# Server
server <- function(input, output) {
  
  output$pitch_table <- renderDT({
    req(input$selected_pitcher)
    
    df <- pitch_df %>% filter(Pitcher == input$selected_pitcher)
    
    summary <- df %>%
      group_by(AutoPitchType) %>%
      summarise(
        Usage = n(),
        AvgVelocity = mean(RelSpeed, na.rm = TRUE),
        AvgSpinRate = mean(SpinRate, na.rm = TRUE),
        AvgIVB = mean(InducedVertBreak, na.rm = TRUE),
        AvgHB = mean(HorzBreak, na.rm = TRUE),
        .groups = "drop"
      ) %>%
      mutate(UsagePct = round(100 * Usage / sum(Usage), 1)) %>%
      select(AutoPitchType, UsagePct, AvgVelocity, AvgSpinRate, AvgIVB, AvgHB) %>%
      round(2)
    
    datatable(summary, rownames = FALSE, options = list(dom = 't'))
  })
  
  output$pitch_plot <- renderPlotly({
    req(input$selected_pitcher)
    
    df <- pitch_df %>% filter(Pitcher == input$selected_pitcher)
    
    plot_ly(df,
            x = ~HorzBreak,
            y = ~InducedVertBreak,
            color = ~AutoPitchType,
            type = 'scatter',
            mode = 'markers') %>%
      layout(
        xaxis = list(title = "Horizontal Break", range = c(-25, 25)),
        yaxis = list(title = "Vertical Break", range = c(-25, 25))
      )
  })
  
  output$batting_table <- renderDT({
    df <- batting_df %>%
      filter(if (input$team != "All") Team == input$team else TRUE) %>%
      filter(PA >= input$minPA) %>%
      mutate(
        OBP_Pctl = percent_rank(OBP) * 100,
        SLG_Pctl = percent_rank(SLG) * 100,
        OPS_Pctl = percent_rank(OPS) * 100,
        wOBA_Pctl = percent_rank(wOBA) * 100,
        xwOBA_Pctl = percent_rank(xwOBA_adjusted) * 100,
        Diff_Pctl = percent_rank(diff_adjusted) * 100,
        xwOBA_per_BIP_Pctl = percent_rank(xwOBA_per_BIP) * 100
      ) %>%
      mutate(across(c(wOBA, xwOBA_adjusted, diff_adjusted, xwOBA_per_BIP,
                      OBP_Pctl, SLG_Pctl, OPS_Pctl, wOBA_Pctl, xwOBA_Pctl, Diff_Pctl, xwOBA_per_BIP_Pctl),
                    ~round(.x, 3)))
    
    datatable(df %>%
                select(Player, Team, PA, wOBA, xwOBA_adjusted, diff_adjusted, xwOBA_per_BIP,
                       wOBA_Pctl, xwOBA_Pctl, Diff_Pctl, xwOBA_per_BIP_Pctl,
                       OBP_Pctl, SLG_Pctl, OPS_Pctl),
              options = list(pageLength = 25),
              rownames = FALSE) %>%
      formatStyle(
        columns = c('wOBA_Pctl', 'xwOBA_Pctl', 'Diff_Pctl', 'xwOBA_per_BIP_Pctl',
                    'OBP_Pctl', 'SLG_Pctl', 'OPS_Pctl'),
        background = styleColorBar(c(0, 100), 'lightblue'),
        backgroundSize = '90% 60%',
        backgroundRepeat = 'no-repeat',
        backgroundPosition = 'center'
      )
  })
  
  
  output$pitching_percentiles_table <- renderDT({
    df <- pitching_df %>%
      filter(if (input$pitch_team != "All") Team == input$pitch_team else TRUE) %>%
      filter(IP >= input$minIP) %>%
      mutate(
        ERA_Pctl = (1 - percent_rank(ERA)) * 100,
        WHIP_Pctl = (1 - percent_rank(WHIP)) * 100,
        FIP_Pctl = (1 - percent_rank(FIP)) * 100
      ) %>%
      mutate(across(c(ERA, WHIP, FIP, ERA_Pctl, WHIP_Pctl, FIP_Pctl), ~round(.x, 3)))
    
    datatable(df %>% select(Player, Team, IP, ERA, ERA_Pctl, WHIP, WHIP_Pctl, FIP, FIP_Pctl)
,
              options = list(pageLength = 25),
              rownames = FALSE) %>%
      formatStyle(
        columns = c('ERA_Pctl', 'WHIP_Pctl', 'FIP_Pctl'),
        background = styleColorBar(c(0, 100), 'lightblue'),
        backgroundSize = '90% 60%',
        backgroundRepeat = 'no-repeat',
        backgroundPosition = 'center'
      )
  })
}

# Run the application 
shinyApp(ui = ui, server = server)
