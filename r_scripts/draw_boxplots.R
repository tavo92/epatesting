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
			
        	                rows_default  = subset(stats,SUBJ==subj & TOOL=='evosuite_default' & BUD==budget)
                	        rows_epamixed  = subset(stats,SUBJ==subj & TOOL=='evosuite_epamixed' & BUD==budget)
                        	rows_epaalone  = subset(stats,SUBJ==subj & TOOL=='evosuite_epaalone' & BUD==budget)

				epa_coverage_default = rows_default$EPA
				epa_coverage_epamixed = rows_epamixed$EPA			

				boxplot(epa_coverage_default, epa_coverage_epamixed,main=c("budget:",budget),ylab="EPA Coverage",xlab=c("subject:",subj))

				pit_score_default = rows_default$PIMUT
				pit_score_epamixed = rows_epamixed$PIMUT

				boxplot(pit_score_default, pit_score_epamixed,main=c("budget:",budget),ylab="PIT Score",xlab=c("subject:",subj))


				line_default = rows_default$LINE
                                line_epamixed = rows_epamixed$LINE

				branch_default = rows_default$BRNCH
				branch_epamixed = rows_epamixed$BRNCH

				
				boxplot(line_default, line_epamixed, branch_default, branch_epamixed,main=c("budget:",budget),ylab="LINE/BRANCH",xlab=c("subject:",subj))

				err_prot_default = rows_default$ERRPROTKILLED
				err_prot_epamixed = rows_epamixed$ERRPROTKILLED


				boxplot(err_prot_default, err_prot_epamixed,main=c("budget:",budget),ylab="Protocol Error Killed",xlab=c("subject:",subj))



#boxplot(epa_coverage_default, 
#	epa_coverage_epamixed, 
#	pit_score_default, 
#	pit_score_epamixed, 
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


