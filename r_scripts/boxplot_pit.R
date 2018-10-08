#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

# test if there is at least one argument: if not, return an error
if (length(args)<2) {
  stop("Input csv file argument must be supplied (report.csv) and a subject name (or list) (ex: com.example.socket.Socket)", call.=FALSE)
}

csv_filename = args[1]

# run the script
stats = read.csv(csv_filename, header=TRUE, sep=",")

subjects_in_file = unique(stats$SUBJ)
tools = unique(stats$TOOL)
budgets = unique(stats$BUD)

subjects <- list()
if (length(args) == 2)
{
	if (args[2] == "ALL")
	{
		subjects = subjects_in_file
	}
} else
{
	i = 2
	while( i <= length(args))
	{
		curr_subj = args[i]
		if (!(curr_subj %in% subjects_in_file))
		{
			cat("WARN! Does not exists subject '", curr_subj, "' in '", csv_filename,"'\n", sep="")
			i = i + 1
			next
		}
		subjects <- c(subjects, curr_subj)
		i = i + 1
	}
}

createBoxPlot <- function()
{
	for(subj in subjects)
	{
		for (budget in budgets)
		{
			if (budget=='600')
			{
				default_rows  = subset(stats,SUBJ==subj & TOOL=='line_branch_exception' & BUD==budget)
				line_branch_exception_epatransition_rows  = subset(stats,SUBJ==subj & TOOL=='line_branch_exception_epatransition' & BUD==budget)
				line_branch_exception_epatransition_epaexception_rows  = subset(stats,SUBJ==subj & TOOL=='line_branch_exception_epatransition_epaexception' & BUD==budget)
				line_branch_exception_edges_rows  = subset(stats,SUBJ==subj & TOOL=='line_branch_exception_epaadjacentedges' & BUD==budget)

				default_pit = default_rows$PIMUT
				line_branch_exception_epatransition_pit = line_branch_exception_epatransition_rows$PIMUT
				line_branch_exception_epatransition_epaexception_pit = line_branch_exception_epatransition_epaexception_rows$PIMUT
				line_branch_exception_edges_pit = line_branch_exception_edges_rows$PIMUT

				name_subj = strsplit(subj, "[.]")[[1]]
				name_subj = tail(name_subj, n=1)
				outputname = paste("def_plus_epa_criterion_",name_subj,".pdf",sep = "")
				pdf(outputname)
				budget_txt = paste("Budget: ", budget, " segs", sep="")
				boxplot(default_pit, line_branch_exception_epatransition_pit, line_branch_exception_epatransition_epaexception_pit, line_branch_exception_edges_pit, names=c("default","def+epatr","def+epatr_epaexc","def+edges"),main=c(name_subj),ylab="PIT Score",xlab=budget_txt)
				
				default_rows  = subset(stats,SUBJ==subj & TOOL=='line_branch_exception' & BUD==budget)
				epatransition_rows  = subset(stats,SUBJ==subj & TOOL=='evosuite_epaalone' & BUD==budget)
				epatransition_epaexception_rows  = subset(stats,SUBJ==subj & TOOL=='epatransition_epaexception' & BUD==budget)
				edges_rows  = subset(stats,SUBJ==subj & TOOL=='epaadjacentedges' & BUD==budget)

				default_pit = default_rows$PIMUT
				epatransition_pit = epatransition_rows$PIMUT
				epatransition_epaexception_pit = epatransition_epaexception_rows$PIMUT
				edges_pit = edges_rows$PIMUT
				
				outputname = paste("only_epa_criterion_",name_subj,".pdf",sep = "")
				pdf(outputname)
				boxplot(default_pit, epatransition_pit, epatransition_epaexception_pit, edges_pit, names=c("default","epatr","epatr_epaexcep","edges"),main=c(name_subj),ylab="PIT Score",xlab=budget_txt)
			}
		}
	}
}

createBoxPlot()