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

printPitMutationScoreMedian <- function() {
	for(subj in subjects) {
		for (budget in budgets) {
			if (budget=='600') {
				cat("###############################################################\n")
				cat("subject:", subj)
				cat("\n")
				cat("budget:",budget)
				cat("\n")
				cat("###############################################################\n")

				
			# LINE:BRANCH
			default_rows  = subset(stats,SUBJ==subj & TOOL=='evosuite_default' & BUD==budget)
			line_branch_errors = default_rows$PIMUT
			cat("mean(LINE:BRANCH)=", mean(line_branch_errors))
			cat("\n")
			
			# LINE:BRANCH:EXCEPTION
			default_rows  = subset(stats,SUBJ==subj & TOOL=='line_branch_exception' & BUD==budget)
			default_errors = default_rows$PIMUT
			cat("mean(LINE:BRANCH:EXCEPTION)=", mean(default_errors))
			cat("\n")
			
			# EPATRANSITION
			epatransition_rows  = subset(stats,SUBJ==subj & TOOL=='epatransition' & BUD==budget)
			epatransition_errors = epatransition_rows$PIMUT
			cat("mean(EPATRANSITION)=", mean(epatransition_errors))
			cat("\n")
			
			# EPATRANSITION:EPAEXCEPTION
			epatransition_epaexception_rows = subset(stats,SUBJ==subj & TOOL=='epatransition_epaexception' & BUD==budget)
			epatransition_epaexception_errors = epatransition_epaexception_rows$PIMUT
			cat("mean(EPATRANSITION:EPAEXCEPTION)=", mean(epatransition_epaexception_errors))
			cat("\n")
			
			# EPAADJACENTEDGES
			edges_rows = subset(stats,SUBJ==subj & TOOL=='epaadjacentedges' & BUD==budget)
			edges_errors = edges_rows$PIMUT
			cat("mean(EPAADJACENTEDGES)=", mean(edges_errors))
			cat("\n")

			# LINE:BRANCH:EXCEPTION:EPATRANSITION
			epamixed_rows  = subset(stats,SUBJ==subj & TOOL=='line_branch_exception_epatransition' & BUD==budget)
			line_branch_exception_epatransition_errors = epamixed_rows$PIMUT
			cat("mean(LINE:BRANCH:EXCEPTION:EPATRANSITION)=", mean(line_branch_exception_epatransition_errors))
			cat("\n")

			# LINE:BRANCH:EXCEPTION:EPATRANSITION:EPAEXCEPTION
			line_branch_exception_epatransition_epaexception_rows = subset(stats,SUBJ==subj & TOOL=='line_branch_exception_epatransition_epaexception' & BUD==budget)
			line_branch_exception_epatransition_epaexception_errors = line_branch_exception_epatransition_epaexception_rows$PIMUT
			cat("mean(LINE:BRANCH:EXCEPTION:EPATRANSITION:EPAEXCEPTION)=", mean(line_branch_exception_epatransition_epaexception_errors))
			cat("\n")

			# LINE:BRANCH:EXCEPTION:EPAADJACENTEDGES
			line_branch_exception_edges_rows = subset(stats,SUBJ==subj & TOOL=='line_branch_exception_epaadjacentedges' & BUD==budget)
			line_branch_exception_edges_errors = line_branch_exception_edges_rows$PIMUT
			cat("mean(LINE:BRANCH:EXCEPTION:EPAADJACENTEDGES)=", mean(line_branch_exception_edges_errors))
			cat("\n")
			cat("\n")

#boxplot(epa_coverage_default, 
#	epa_coverage_epamixed, 
#	default_pit, 
#	line_branch_edges_pit, 
#	line_default, 
#	line_epamixed, 
#	branch_default, 
#	branch_epamixed, 
#	names=c("epa_default","epa_mixed","mut_default","mut_mixed","line_default","line_mixed","branch_default","branch_mixed"),
#	main=c(subj,budget))
			}
		}
	}
}

printPitMutationScoreMedian()


