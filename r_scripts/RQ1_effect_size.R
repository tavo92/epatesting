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
	cat("subject", "Tx EPA", "Tx EPA", "TxExcep EPAEX", "TxExcep EPAEX", "TxPairs EPAP", "TxPairs EPAP", sep=", ")
	cat("\n")
	cat("subject", "A12", "p-value", "A12", "p-value", "A12", "p-value", sep=", ")
	cat("\n")
}

measureA <- function(a,b){

        if(length(a)==0 & length(b)==0){
                return(0.5)
        } else if(length(a)==0){
                ## motivation is that we have no data for "a" but we do for "b".
                ## maybe the process generating "a" always fail (eg out of memory)
                return(0)
        } else if(length(b)==0){
                return(1)
        } 

        r = rank(c(a,b))
        r1 = sum(r[seq_along(a)])

        m = length(a)
        n = length(b)
        A = (r1/m - (m+1)/2)/n

        return(A)

}

pValueRefactor <- function(p_value)
{
	if (p_value < 0.005)
	{
		p_value = "< 0.005"
	} else if (p_value < 0.05)
	{
		p_value = "< 0.05"
	} else
	{
		p_value = round(p_value, digits=4)
	}
	return (p_value)
}

RQ1 <- function()
{
	for(subj in subjects)
	{
		name_subj = strsplit(subj, "[.]")[[1]]
		name_subj = tail(name_subj, n=1)
		for (budget in budgets)
		{
			# LINE:BRANCH:EXCEPTION
			default_rows  = subset(stats,SUBJ==subj & TOOL=='line_branch_exception' & BUD==budget)
			default_epa = default_rows$EPA
			default_epaex = default_rows$EXCEP
			default_epap = default_rows$ADJAC
						
			# EPATRANSITION
			epatransition_rows  = subset(stats,SUBJ==subj & TOOL=='epatransition' & BUD==budget)
			epatransition_epa = epatransition_rows$EPA
			epatransition_a12 = measureA(default_epa, epatransition_epa)
			epatransition_p_value = pValueRefactor(wilcox.test(default_epa, epatransition_epa)$p.value)
			
			# EPATRANSITION_EPAEXCEPTION
			epatransition_epaexception_rows  = subset(stats,SUBJ==subj & TOOL=='epatransition_epaexception' & BUD==budget)
			epatransition_epaexception_epaex = epatransition_epaexception_rows$EXCEP
			epatransition_epaexception_a12 = measureA(default_epaex, epatransition_epaexception_epaex)
			epatransition_epaexception_p_value = pValueRefactor(wilcox.test(default_epaex, epatransition_epaexception_epaex)$p.value)
			
			# EPAADJACENTEDGES
			edges_rows  = subset(stats,SUBJ==subj & TOOL=='epaadjacentedges' & BUD==budget)
			edges_epap = edges_rows$ADJAC
			epedges_a12 = measureA(default_epap, edges_epap)
			edges_p_value = pValueRefactor(wilcox.test(default_epap, edges_epap)$p.value)
			
			
			cat(name_subj, epatransition_a12, epatransition_p_value, epatransition_epaexception_a12, epatransition_epaexception_p_value, epedges_a12, edges_p_value, sep=", ")
			cat("\n")
		}
	}
}

sink("table.csv")
printHeader()
RQ1()
sink()