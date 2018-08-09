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
				pit_score = rows$PIMUT
				mj_score = rows$MJMUT

				cat("correlation pit_score,mj_score:", cor(pit_score, mj_score))
				cat("\n")
				cat("\n")
			}
		}
	}
}


calculateCorrelations()


