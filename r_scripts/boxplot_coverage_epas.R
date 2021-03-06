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

createBoxPlot <- function() {
        for(subj in subjects) {
                for (budget in budgets) {

			if (budget=='600') {
			
				default_rows  = subset(stats,SUBJ==subj & TOOL=='line_branch_exception' & BUD==budget)
				epatransition_rows  = subset(stats,SUBJ==subj & TOOL=='epatransition' & BUD==budget)
				epatransition_epaexception_rows  = subset(stats,SUBJ==subj & TOOL=='epatransition_epaexception' & BUD==budget)
				edges_rows  = subset(stats,SUBJ==subj & TOOL=='epaadjacentedges' & BUD==budget)

				default_pit = default_rows$PIMUT
				epatransition_pit = epatransition_rows$PIMUT
				epatransition_epaexception_pit = epatransition_epaexception_rows$PIMUT
				edges_pit = edges_rows$PIMUT

				boxplot(default_pit, epatransition_pit, epatransition_epaexception_pit, edges_pit, names=c("default","epatr","epatr_epaexcep","edges"),main=c("budget:",budget),ylab="PIT Score",xlab=c("subject:",subj))


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

createBoxPlot()


