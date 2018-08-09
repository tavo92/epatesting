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
        cat("Number of detected error protocols EvoSuite vs. EvoSuite+EPA", "\n")
        for(subj in subjects) {
		cat("subject: ", subj, "\n")
                for (budget in budgets) {
			cat("budget: ",budget,"\t")

                        rows_default  = subset(stats,SUBJ==subj & TOOL=='evosuite_default' & BUD==budget)
                        rows_epamixed  = subset(stats,SUBJ==subj & TOOL=='evosuite_epamixed' & BUD==budget)

                        err_prot_default = rows_default$ERRPROTKILLED
                        err_prot_epamixed = rows_epamixed$ERRPROTKILLED


			my_measureA = measureA(err_prot_default, err_prot_epamixed)
                        cat("A12=", my_measureA, "\t")


                        if (length(err_prot_default)==0) {
                                cat("(p-value","Error",")\n")
                        } else {
                                my_p_value = wilcox.test(err_prot_default, err_prot_epamixed)$p.value
                                cat("(p-value",my_p_value,")\n")
                        }
		}
	}
}

calculateEffectSizeTable()

