setwd("~/Desktop/InterIIT Tech/code_csv")
getwd()
temp = read.csv("port4_cv.csv",header=FALSE)
Dmat <- as.matrix(temp,rownames.force = NA)

p1 <- read.csv("~/Desktop/InterIIT Tech/code_csv/p4.csv",header = TRUE)
dvec <- c(p1$return)
dvecMatrix <- matrix(dvec)
dvecMatrixTranspose <- t(dvecMatrix)
originalReturnRisk <- read.csv("~/Desktop/InterIIT Tech/code_csv/portef4.csv",sep=" ",header = TRUE)



A <- matrix(c(rep(1,98)), ncol=1)
Amat <- cbind(A, diag(98), -diag(98))
class(Amat)
bvec <- c(1,rep(0,98),rep(-1,98))

library("quadprog", lib.loc="~/R/i686-pc-linux-gnu-library/3.1")


#value <- data.frame(risk = numeric(), retur = numeric(),ratio = numeric(), stringsAsFactors = FALSE)
#rvalue <- data.frame(y = numeric(), stringsAsFactors = FALSE)
table <- data.frame(matrix(NA_real_, nrow = 101, ncol = 2000))
count <- 1
while(count <=2000){
  lambda <- count/2000
  ans <- solve.QP(2*lambda*Dmat,(1-lambda)*dvec,Amat,bvec=bvec, meq=1)
  #solution <- data.frame(ans$solution)
  
  #solutionMatrix <- matrix(ans$solution)
  #s <- toString(count)
  #name <- paste("port1/","solution","_",s,".csv")
  #value <- rbind(value, data.frame(x = ans$value))
  #write.table(solution, file =name ,row.names=FALSE,col.names=FALSE)
  count <- count + 1
  solutionMatrix <- matrix(ans$solution)
  solutionMatrixTranspose <- t(solutionMatrix)
  risk <- solutionMatrixTranspose %*% Dmat %*% solutionMatrix
  #print(risk)
  #value <- rbind(value, data.frame(x = risk, y = retur))
  retur <- dvecMatrixTranspose %*% solutionMatrix
  #print(retur)
  ratio <- retur/risk
  weightsRiskReturn<- c(ans$solution,retur,risk,ratio)
  table[count] <- weightsRiskReturn
  
  #value <- rbind(value, data.frame(risk = risk, retur = retur, ratio=ratio ))
  #rvalue <- rbind(rvalue, data.frame(y = retur))
  
  
  
  
}
write.table(table, file ="weightsReturnRiskRatio4.csv",sep=",",row.names=FALSE,col.names=FALSE)
#write.table(rvalue, file ="return1_values.csv",row.names=FALSE,col.names=FALSE)

#attach(mtcars)
#par(mfrow=c(2,2))
#p1 <- plot(value$x,value$y)
#p2<- plot(originalReturnRisk$V2, originalReturnRisk$V1)
#plot(value$x,value$y,type="l",col="red",xlim=c(5,15), ylim=c(35,85))
#lines(originalReturnRisk$V2, originalReturnRisk$V1,col="green")
#plot(value$x,value$y, type="l", col="red" )
#par(new=TRUE)
#plot(originalReturnRisk$V2, originalReturnRisk$V1, col="green" )
