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

calculateEffectSize <- function() {
	for(subj in subjects) {
        	for (budget in budgets) {

               		cat("subject:", subj)
                	cat("\n")

	                cat("budget:",budget)
        	        cat("\n")

			# LINE:BRANCH
			default_rows  = subset(stats,SUBJ==subj & TOOL=='evosuite_default' & BUD==budget)
			line_branch_errors = default_rows$ERRPROT_KILLED
			cat("length(LINE:BRANCH)=", length(line_branch_errors))
			cat("\n")
			
			# LINE:BRANCH:EXCEPTION
			default_rows  = subset(stats,SUBJ==subj & TOOL=='line_branch_exception' & BUD==budget)
			default_errors = default_rows$ERRPROT_KILLED
			cat("length(LINE:BRANCH:EXCEPTION)=", length(default_errors))
			cat("\n")
			
			# EPATRANSITION
			epatransition_rows  = subset(stats,SUBJ==subj & TOOL=='epatransition' & BUD==budget)
			epatransition_errors = epatransition_rows$ERRPROT_KILLED
			cat("length(EPATRANSITION)=", length(epatransition_errors))
			cat("\n")
			
			# EPATRANSITION:EPAEXCEPTION
			epatransition_epaexception_rows = subset(stats,SUBJ==subj & TOOL=='epatransition_epaexception' & BUD==budget)
			epatransition_epaexception_errors = epatransition_epaexception_rows$ERRPROT_KILLED
			cat("length(EPATRANSITION:EPAEXCEPTION)=", length(epatransition_epaexception_errors))
			cat("\n")
			
			# EPAADJACENTEDGES
			edges_rows = subset(stats,SUBJ==subj & TOOL=='epaadjacentedges' & BUD==budget)
			edges_errors = edges_rows$ERRPROT_KILLED
			cat("length(EPAADJACENTEDGES)=", length(edges_errors))
			cat("\n")

			# LINE:BRANCH:EXCEPTION:EPATRANSITION
			epamixed_rows  = subset(stats,SUBJ==subj & TOOL=='line_branch_exception_epatransition' & BUD==budget)
			line_branch_exception_epatransition_errors = epamixed_rows$ERRPROT_KILLED
			cat("length(LINE:BRANCH:EXCEPTION:EPATRANSITION)=", length(line_branch_exception_epatransition_errors))
			cat("\n")

			# LINE:BRANCH:EXCEPTION:EPATRANSITION:EPAEXCEPTION
			line_branch_exception_epatransition_epaexception_rows = subset(stats,SUBJ==subj & TOOL=='line_branch_exception_epatransition_epaexception' & BUD==budget)
			line_branch_exception_epatransition_epaexception_errors = line_branch_exception_epatransition_epaexception_rows$ERRPROT_KILLED
			cat("length(LINE:BRANCH:EXCEPTION:EPATRANSITION:EPAEXCEPTION)=", length(line_branch_exception_epatransition_epaexception_errors))
			cat("\n")

			# LINE:BRANCH:EXCEPTION:EPAADJACENTEDGES
			line_branch_exception_edges_rows = subset(stats,SUBJ==subj & TOOL=='line_branch_exception_epaadjacentedges' & BUD==budget)
			line_branch_exception_edges_errors = line_branch_exception_edges_rows$ERRPROT_KILLED
			cat("length(LINE:BRANCH:EXCEPTION:EPAADJACENTEDGES)=", length(line_branch_exception_edges_errors))
			cat("\n")

			cat("\n")

			cat("---------------------------------------------------------------------------------","\n")
        	        cat("\n")


			cat("LINE:BRANCH:EXCEPTION vs. LINE:BRANCH","\n")
        	        cat("\n")
			my_measureA = measureA(default_errors, line_branch_errors)
			cat("A12=", my_measureA, "\n")
			if (length(default_errors)==0) {
				cat("p-value","Error","\n")
			} else {
				my_p_value = wilcox.test(default_errors, line_branch_errors)$p.value	
				cat("p-value",my_p_value,"\n")
			}
        	        cat("\n")
					
			cat("LINE:BRANCH:EXCEPTION vs. EPATRANSITION","\n")
        	        cat("\n")
			my_measureA = measureA(default_errors, epatransition_errors)
			cat("A12=", my_measureA, "\n")
			if (length(default_errors)==0) {
				cat("p-value","Error","\n")
			} else {
				my_p_value = wilcox.test(default_errors, epatransition_errors)$p.value	
				cat("p-value",my_p_value,"\n")
			}
        	        cat("\n")

			cat("LINE:BRANCH:EXCEPTION vs. EPATRANSITION:EPAEXCEPTION","\n")
        	        cat("\n")
			my_measureA = measureA(default_errors, epatransition_epaexception_errors)
			cat("A12=", my_measureA, "\n")
			if (length(default_errors)==0) {
				cat("p-value","Error","\n")
			} else {
				my_p_value = wilcox.test(default_errors, epatransition_epaexception_errors)$p.value	
				cat("p-value",my_p_value,"\n")
			}
        	        cat("\n")


			cat("LINE:BRANCH:EXCEPTION vs. EPAADJACENTEDGES","\n")
        	        cat("\n")
			my_measureA = measureA(default_errors, edges_errors)
			cat("A12=", my_measureA, "\n")
			if (length(default_errors)==0) {
				cat("p-value","Error","\n")
			} else {
				my_p_value = wilcox.test(default_errors, edges_errors)$p.value	
				cat("p-value",my_p_value,"\n")
			}
        	        cat("\n")


			cat("LINE:BRANCH:EXCEPTION vs. LINE:BRANCH:EXCEPTION:EPATRANSITION","\n")
        	        cat("\n")
			my_measureA = measureA(default_errors, line_branch_exception_epatransition_errors)
			cat("A12=", my_measureA, "\n")
			if (length(default_errors)==0) {
				cat("p-value","Error","\n")
			} else {
				my_p_value = wilcox.test(default_errors, line_branch_exception_epatransition_errors)$p.value	
				cat("p-value",my_p_value,"\n")
			}
        	        cat("\n")


			cat("LINE:BRANCH:EXCEPTION vs. LINE:BRANCH:EXCEPTION:EPATRANSITION:EPAEXCEPTION","\n")
        	        cat("\n")
			my_measureA = measureA(default_errors, line_branch_exception_epatransition_epaexception_errors)
			cat("A12=", my_measureA, "\n")
			if (length(default_errors)==0) {
				cat("p-value","Error","\n")
			} else {
				my_p_value = wilcox.test(default_errors, line_branch_exception_epatransition_epaexception_errors)$p.value	
				cat("p-value",my_p_value,"\n")
			}
        	        cat("\n")


			cat("LINE:BRANCH:EXCEPTION vs. LINE:BRANCH:EXCEPTION:EPAADJACENTEDGES","\n")
        	        cat("\n")
			my_measureA = measureA(default_errors, line_branch_exception_edges_errors)
			cat("A12=", my_measureA, "\n")
			if (length(default_errors)==0) {
				cat("p-value","Error","\n")
			} else {
				my_p_value = wilcox.test(default_errors, line_branch_exception_edges_errors)$p.value
				cat("p-value",my_p_value,"\n")
			}
        	        cat("\n")
        	        cat("\n")
		}
	}
}

calculateEffectSize()

