#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

# test if there is at least one argument: if not, return an error
if (length(args)!=1) {
  stop("Input csv file argument must be supplied (report.csv)", call.=FALSE)
}

csv_filename = args[1]

# run the script
stats = read.csv(csv_filename, header=TRUE, sep=",")

subjects = unique(stats$SUBJ)
tools = unique(stats$TOOL)
budgets = unique(stats$BUD)


calculateCorrelations <- function() {
	for(subj in subjects) {
		for (tool in tools) {
			for (budget in budgets) {
				cat("subject:", subj)
				cat("\n")

				cat("tool: ", tool)
				cat("\n")

				cat("budget:",budget)
				cat("\n")

				rows  = subset(stats,SUBJ==subj & TOOL==tool & BUD==budget)
				epa_coverage = rows$EPA
				pit_score = rows$PIMUT

				cat("min(epa_coverage)",min(epa_coverage))	
				cat("\n")
				cat("max(epa_coverage)",max(epa_coverage))	
				cat("\n")
				cat("mean(epa_coverage)", mean(epa_coverage))
				cat("\n")


			        cat("min(pit_score)",min(pit_score))
        			cat("\n")
        			cat("max(pit_score)",max(pit_score))
        			cat("\n")
				cat("mean(pit_score)", mean(pit_score))
				cat("\n")

				cat("cor(epa_coverage,pit_score)", cor(epa_coverage,pit_score))
				cat("\n")
				cat("\n")
			}
		}
	}
}


calculateCorrelations()


