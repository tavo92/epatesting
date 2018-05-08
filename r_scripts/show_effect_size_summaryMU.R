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

calculateEffectSizeTable <- function() {
        for(subj in subjects) {
		cat("subject: ", subj, "\n")
                for (budget in budgets) {
			cat("budget: ",budget,"\t\n")

                        rows_default  = subset(stats,SUBJ==subj & TOOL=='evosuite_default' & BUD==budget)
                        rows_epamixed  = subset(stats,SUBJ==subj & TOOL=='evosuite_epamixed' & BUD==budget)
                        rows_epaalone  = subset(stats,SUBJ==subj & TOOL=='evosuite_epaalone' & BUD==budget)

                        epa_coverage_default = rows_default$EPA
                        protocol_score_default = rows_default$ERRPROT

                        epa_coverage_epamixed = rows_epamixed$EPA
                        protocol_score_epamixed = rows_epamixed$ERRPROT

                        epa_coverage_epaalone = rows_epaalone$EPA
                        protocol_score_epaalone = rows_epaalone$ERRPROT

			my_measureA = measureA(protocol_score_default, protocol_score_epamixed)
                        
			cat("Default vs Mixed A12=", my_measureA, "\t\n")

		         my_measureA = measureA(protocol_score_default, protocol_score_epaalone)
                        cat("Default vs Alone A12=", my_measureA, "\t\n")

			  my_measureA = measureA(protocol_score_epamixed, protocol_score_epaalone)
                        cat("Mixed vs Alone A12=", my_measureA, "\t\n")



                        if (length(protocol_score_default)==0) {
                                cat("(p-value","Error",")\n")
                        } else {
                                my_p_value = wilcox.test(protocol_score_default, protocol_score_epamixed)$p.value
                                cat("(p-value",my_p_value,")\n")
                        }
		}
	}
}

calculateEffectSizeTable()

