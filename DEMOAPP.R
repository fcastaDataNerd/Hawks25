library(shiny)
library(tidyverse)


ui <- fluidPage(
  titlePanel("NECBL Player Data"),
  
  # Tab structure
  tabsetPanel(
    # Pitchers Tab
    tabPanel("Pitchers",
             sidebarLayout(
               sidebarPanel(
                 selectInput("pitcher_team", "Select NECBL Team:", 
                             choices = unique(pitchers$NECBL_TEAM), 
                             selected = unique(pitchers$NECBL_TEAM)[1])
               ),
               mainPanel(
                 tableOutput("pitcher_table")
               )
             )
    ),
    
    # Batters Tab
    tabPanel("Batters",
             sidebarLayout(
               sidebarPanel(
                 selectInput("batter_team", "Select NECBL Team:", 
                             choices = unique(batters$NECBL_TEAM), 
                             selected = unique(batters$NECBL_TEAM)[1])
               ),
               mainPanel(
                 tableOutput("batter_table")
               )
             )
    )
  )
)

# Server
server <- function(input, output) {
  # Filtered pitcher data
  output$pitcher_table <- renderTable({
    pitchers %>% filter(NECBL_TEAM == input$pitcher_team)
  })
  
  # Filtered batter data
  output$batter_table <- renderTable({
    batters %>% filter(NECBL_TEAM == input$batter_team)
  })
}

# Run the Shiny app
shinyApp(ui = ui, server = server)
