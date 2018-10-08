#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

# test if there is at least one argument: if not, return an error
if (length(args)< 1) {
  stop("Input csv file argument must be supplied (report.csv)", call.=FALSE)
}

csv_filename = args[1]
# run the script
stats = read.csv(csv_filename, header=TRUE, sep=",")

subjects = unique(stats$SUBJ)
tools = unique(stats$TOOL)
budgets = unique(stats$BUD)

criterios <- list()
i = 2
while( i <= length(args))
{
	curr_criterio = args[i]
	if (!(curr_criterio %in% tools))
	{
	  stop("\nERROR!! Does not exists criterion '", curr_criterio, "' in '", csv_filename,"'\n", sep="")
	}
    criterios <- c(criterios, curr_criterio)
    i = i + 1
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


printHeader <- function()
{
	cat("subject")
	i = 1
	second_line = ""
	while(i <= length(criterios))
	{
		curr_criterio = criterios[[i]]		
		i = i + 1
		if (curr_criterio == "line_branch_exception")
		{
			next
		}
		# Repet for future table style
		cat(",", curr_criterio)
		cat(",", curr_criterio)
		second_line = c(second_line, ", A12, p-value")
	}
	cat("\n")
	cat("subject")
	cat(second_line)
	cat("\n")
}

calculateEffectSize <- function()
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
			default_errors = default_rows$PIMUT
			
			i = 1
			while(i <= length(criterios))
			{
				criterio = criterios[[i]]
				i = i + 1
				if (criterio == "line_branch_exception")
				{
					next
				}
				rows  = subset(stats,SUBJ==subj & TOOL==criterio & BUD==budget)
				errors = rows$PIMUT
				
				my_measureA = measureA(default_errors, errors)
				cat(", ", round(my_measureA, digits=4))
				if (length(default_errors)==0)
				{
					stop("ERROR!! Does not exists criterion line_branch_exception in file", csv_filename, call.=FALSE)
					return
				} else
				{
					my_p_value = wilcox.test(default_errors, errors)$p.value
					if (my_p_value < 0.005)
					{
						my_p_value = "\\textless 0.005"
					} else if (my_p_value < 0.05)
					{
						my_p_value = "\\textless 0.05"
					} else
					{
						my_p_value = round(my_p_value, digits=4)
					}
					cat(", ", my_p_value)
				}
			}
			cat("\n")
		}
	}
}


printHeader()
calculateEffectSize()
