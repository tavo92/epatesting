#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

# test if there is at least one argument: if not, return an error
if (length(args)!= 1) {
  stop("Input csv file argument must be supplied (report.csv)", call.=FALSE)
}

csv_filename = args[1]
# run the script
stats = read.csv(csv_filename, header=TRUE, sep=",")

subjects = unique(stats$SUBJ)
tools = unique(stats$TOOL)
budgets = unique(stats$BUD)

printHeader <- function()
{
	cat("subject", "Tx", "Tx", "TxExcep", "TxExcep", "TxPairs", "TxPairs", sep=", ")
	cat("\n")
	cat("subject", "DEF", "EPA", "DEF", "EPAEX", "DEF", "EPAP", sep=", ")
	cat("\n")
}

RQ1 <- function()
{
	for(subj in subjects)
	{
		name_subj = strsplit(subj, "[.]")[[1]]
		name_subj = tail(name_subj, n=1)
		cat(name_subj)
		for (budget in budgets)
		{
			# LINE:BRANCH:EXCEPTION
			default_rows  = subset(stats,SUBJ==subj & TOOL=='line_branch_exception' & BUD==budget)
			default_epa = round(mean(default_rows$EPACOV)*100, digits=2)
			default_epaex = round(mean(default_rows$EXCEPCOV)*100, digits=2)
			default_epap = round(mean(default_rows$ADJACCOV)*100, digits=2)
			
			# EPATRANSITION
			epatransition_rows  = subset(stats,SUBJ==subj & TOOL=='epatransition' & BUD==budget)
			epatransition_epa = round(mean(epatransition_rows$EPACOV)*100, digits=2)
			
			# EPATRANSITION_EPAEXCEPTION
			epatransition_epaexception_rows  = subset(stats,SUBJ==subj & TOOL=='epatransition_epaexception' & BUD==budget)
			epatransition_epaexception_epaex = round(mean(epatransition_epaexception_rows$EXCEPCOV)*100, digits=2)
			
			# EPAADJACENTEDGES
			edges_rows  = subset(stats,SUBJ==subj & TOOL=='epaadjacentedges' & BUD==budget)
			edges_epap = round(mean(edges_rows$ADJACCOV)*100, digits=2)
			
			cat(", ", default_epa, "%, ", epatransition_epa, "%, ", default_epaex, "%, ", epatransition_epaexception_epaex, "%, ", default_epap, "%, ", edges_epap,"%", sep="")
			cat("\n")
		}
	}
}

sink("table.csv")
printHeader()
RQ1()
sink()
