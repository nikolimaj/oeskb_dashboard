library(shiny)
library(ggplot2)
library(dplyr)

# Load Data and Preprocess
data <- read.csv("player_games_joined.csv", stringsAsFactors=TRUE)

names(data) <- paste0(
  toupper(substr(names(data), 1, 1)),
  substr(names(data), 2, nchar(names(data)))
)

data <- data %>%
  mutate(Heim = ifelse(Heim == "True", TRUE, FALSE)) %>%
  mutate(Datum = as.Date(Datum, format="%Y-%m-%d")) %>%
  filter(
    # remove extreme outliers (probably coming from players giving up mid game)
    Kegel > quantile(Kegel, 0.001, na.rm = TRUE) - 1.5 * IQR(Kegel, na.rm = TRUE)

  )


ui <- fluidPage(
  tags$head(
    tags$link(rel = "stylesheet", type = "text/css", href = "styles.css")
  ),
  
  fluidRow(
    column(width = 8,
           h1("ÖSKB - Dashboard")
    ),
    column(width = 4,
           tags$img(src = "oeskb_logo.png", height = "100px", style = "float: right;")
    )
  ),
  
  
  sidebarLayout(
    sidebarPanel(
      dateRangeInput("date_range", "Zeitraum:",
                     start = min(data$Datum), end = max(data$Datum)),
      checkboxGroupInput("geschlecht", "Geschlecht:",
                         choices = list("weiblich" = "w", "männlich" = "m"),
                         selected = c("w", "m")),
      checkboxGroupInput("liga", "Liga:",
                         choices = unique(data$Liga), selected = unique(data$Liga)),
      sliderInput("birth_year", "Jahrgang",
                  min = min(data$Jahrgang, na.rm = TRUE),
                  max = max(data$Jahrgang, na.rm = TRUE),
                  value = range(data$Jahrgang, na.rm = TRUE),
                  step = 1),
      selectizeInput("selected_names", "Spielerauswahl:",
                     choices = NULL,
                     multiple = TRUE,
                     options = list(placeholder = 'Spieler suchen'))
    ),
    
    mainPanel(
      tabsetPanel(
        id = "main_tabs",
        tabPanel("Verteilungen",
                 br(),
                 fluidRow(
                   column(4,
                          selectInput("distribution_group", "Gruppieren nach:",
                                      choices = c("Liga", "Geschlecht", "Spieler" = "Name"),
                                      selected = "Liga")
                   )
                 ),
                 br(),
                 fluidRow(
                   column(12,
                          h4("Dichteverteilung"),
                          plotOutput("density", height = "300px")
                   )
                 ),
                 
                 fluidRow(
                   column(6,
                          h4("Boxplot"),
                          plotOutput("boxplot", height = "300px")
                   ),
                   column(6,
                          h4("Violinplot"),
                          plotOutput("violin", height = "300px")
                   )
                 ),
        ),
        
        tabPanel("Time Line",
                 br(),
                 plotOutput("timeplot", height = "400px")),
        tabPanel("Info",
                 fluidPage(
                   h3("Über den Datensatz"),
                   p(
                     "Diese App visualisiert die Daten vom ",
                     a("ÖSKB-Ergebnisdienst", href = "https://oeskb.at/app/#/Ergebnisdienst/Verband/NationaleLigen", target = "_blank"),
                     " und eignet sich für den direkten Vergleich von Ligen und einzelnen SpielerInnen."
                   )
                 )
        )
      )
    )
  )
)


server <- function(input, output) {
  
  filtered_data <- reactive({
    data %>%
      filter(
        Datum >= input$date_range[1] & Datum <= input$date_range[2],
        Geschlecht %in% input$geschlecht,
        Liga %in% input$liga,
        Jahrgang >= input$birth_year[1] & Jahrgang <= input$birth_year[2],
        Kegel > quantile(Kegel, 0.001, na.rm = TRUE) - 1.5 * IQR(Kegel, na.rm = TRUE),
      )
  })
  
  previous_choices <- reactiveVal(NULL)
  
  observe({
    
    new_choices <- sort(unique(filtered_data()$Name))
    current_selection <- isolate(input$selected_names)
    valid_selection <- intersect(current_selection, new_choices)
    
    # Get previous choices (NULL on first run)
    old_choices <- previous_choices()
    
    # Only update if the choices or valid selection changed
    if (is.null(old_choices) || !identical(old_choices, new_choices)) {
      previous_choices(new_choices)  # Update stored choices
      
      updateSelectizeInput(
        inputId = "selected_names",
        choices = new_choices,
        selected = valid_selection,
        server = TRUE
      )
    }
  })
  
  name_filter <- reactive({
    selected <- input$selected_names
    group_by_name <- input$distribution_group == "Name" || input$main_tabs == "Time Line"
    
    all_names <- sort(unique(filtered_data()$Name))
    
    # Logic if single players are relevant
    if (group_by_name) {
      if (is.null(selected) || length(selected) == 0) {
        if (length(all_names) <= 10) {
          # If ≤10 players exist overall, show all
          valid_names <- all_names
        } else {
          # If >10 players and none selected, show none
          return(filtered_data() %>% filter(FALSE))
        }
      } else {
        # Limit to 10 selected players
        valid_names <- head(selected, 10)
      }
    } else {
      # If group is Liga or Geschlecht
      if (is.null(selected) || length(selected) == 0) {
        valid_names <- all_names
      } else {
        valid_names <- selected
      }
    }
    
    filtered_data() %>%
      filter(Name %in% valid_names)
  })
  
  validate_filters <- function(filtered_msg = "Keine Daten verfügbar für die ausgewählten Filter.",
                               name_msg = "Keine Spieler ausgewählt, wählen Sie mindestens einen Spieler aus") {
    df1 <- filtered_data()
    validate(need(nrow(df1) > 0, filtered_msg))
    
    df2 <- name_filter()
    validate(need(nrow(df2) > 0, name_msg))
    
    return(df2)
  }
  
  output$density <- renderPlot({
    df <- validate_filters()
    
    ggplot(df, aes(x = Kegel, fill = .data[[input$distribution_group]])) +
      geom_density(alpha = 0.5) +
      labs(x = "Kegel", y = "Dichte", fill = input$distribution_group) +
      theme_minimal()
  })
  
  output$boxplot <- renderPlot({
    df <- validate_filters()
  
    ggplot(df, aes(x = .data[[input$distribution_group]], y = Kegel)) +
      geom_boxplot() +
      labs(x = input$distribution_group, y = "Kegel") +
      theme_minimal()
  })
  
  output$violin <- renderPlot({
    df <- validate_filters()

    ggplot(df, aes(x = .data[[input$distribution_group]], y = Kegel)) +
      geom_violin(fill = "lightgreen") +
      labs(x = input$distribution_group, y = "Kegel") +
      theme_minimal()
  })
  
  output$timeplot <- renderPlot({
    df <- validate_filters()
    
    ggplot(df, aes(x = as.Date(Datum), y = Kegel, color = Name)) +
      geom_smooth(se = FALSE, method = "loess", span = 0.9) +
      labs(x = "Date", y = "Kegel", color = "Spielerin")
  })
}

# Run the application 
shinyApp(ui = ui, server = server)

