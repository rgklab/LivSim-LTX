library(causalMed)

library(survival)
library (plyr)

variable_setup <- function () {
  # expose
  a <- rnorm(10000, mean = 0, sd=1)
  # confounder
  d <- rnorm(10000, mean=0, sd=1)
  # mediator expo coefficient = 2 confounder_coefficient = 3
  b <- 2 * a + 3 * d + rnorm(100000, mean=0, sd=0.1)
  # distination expo_coefficient = 1.5 mediator_coefficient=2.3 confounder_coefficient=1.1
  c <- 1.5 * a + 1.1 * d + 2.3 * b + rnorm(100000, mean=0, sd=0.15)
  return_df <- data.frame('expose'= a, 'confounder'=d, 'mediator'=b, 'distination'=c)
  return(return_df)
}

feature_df <- variable_setup()
# out <- iorw(lm(distination ~ expose + confounder, data = feature_df), exposure = 'expose', mediator = 'mediator', family = 'bbinomial')
# summary(out)

data(lipdat)
dtbase <- lipdat[lipdat$time == 0, ]
out <- iorw(coxph(Surv(os, cvd) ~ bmi + age0 + smoke, data = dtbase),
exposure   = "smoke",
mediator   = "hdl",
family     = "gaussian")

summary(out)
# # d <- 10

