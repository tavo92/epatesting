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

		for (budget in budgets) {
			cat("subject:", subj)
			cat("\n")

			cat("budget:",budget)
			cat("\n")

			rows  = subset(stats,SUBJ==subj & BUD==budget)
			
			line_coverage = rows$LINE
			branch_coverage = rows$BRNCH
			epa_transition_coverage = rows$EPA
			epa_exception_coverage = rows$EXCEP
			epa_adjacent_edges_coverage = rows$ADJAC
			found_protocol_errors = rows$ERRPROT

			cat("cor(line_coverage,found_protocol_errors)", cor(line_coverage,found_protocol_errors))
			cat("\n")

			cat("cor(branch_coverage,found_protocol_errors)", cor(branch_coverage,found_protocol_errors))
			cat("\n")

			cat("cor(epa_transition_coverage,found_protocol_errors)", cor(epa_transition_coverage,found_protocol_errors))
			cat("\n")
			cat("cor(epa_exception_coverage,found_protocol_errors)", cor(epa_exception_coverage,found_protocol_errors))
			cat("\n")
			cat("cor(epa_adjacent_edges_coverage,found_protocol_errors)", cor(epa_adjacent_edges_coverage,found_protocol_errors))
			cat("\n")
			cat("\n")


			for (tool in tools) {
				cat("subject:", subj)
				cat("\n")

				cat("tool: ", tool)
				cat("\n")

				cat("budget:",budget)
				cat("\n")

				rows  = subset(stats,SUBJ==subj & TOOL==tool & BUD==budget)

				line_coverage = rows$LINE
				branch_coverage = rows$BRNCH
				epa_transition_coverage = rows$EPA
				epa_exception_coverage = rows$EXCEP
				epa_adjacent_edges_coverage = rows$ADJAC
				found_protocol_errors = rows$ERRPROT


				cat("cor(line_coverage,found_protocol_errors)", cor(line_coverage,found_protocol_errors))
				cat("\n")

				cat("cor(branch_coverage,found_protocol_errors)", cor(branch_coverage,found_protocol_errors))
				cat("\n")

				cat("cor(epa_transition_coverage,found_protocol_errors)", cor(epa_transition_coverage,found_protocol_errors))
				cat("\n")

				cat("cor(epa_exception_coverage,found_protocol_errors)", cor(epa_exception_coverage,found_protocol_errors))
				cat("\n")

				cat("cor(epa_adjacent_edges_coverage,found_protocol_errors)", cor(epa_adjacent_edges_coverage,found_protocol_errors))
				cat("\n")

				cat("\n")
			}
		}
	}
}


calculateCorrelations()


