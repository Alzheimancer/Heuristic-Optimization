uef <- read.csv("weightsReturnRiskRatio4.csv",header=FALSE)
ccef <- read.csv("final_stored_4.csv",header=FALSE)
error_horizontal <- rep(1,2001)
dim <- 98
for(i in 1:2001)
{
  x_less_dist <- 100
  y_less_dist <- 100
  x_more_dist <- 100
  y_more_dist <- 100
  ys <- ccef[dim+1,i] 
  xs <- ccef[dim+2,i]
  for(j in 1:2001)
  {
    yj <- uef[dim+1,j]
    xj <- uef[dim+2,j]
    if(xj<xs)
      if(x_less_dist > (xs-xj))
        {
        x_less_dist <- xs-xj
        x_less <- xj
        y_less <- yj
      }
    else
      if(x_more_dist >(xj-xs)){
        x_more_dist <- xj-xs
        x_more <- xj
        y_more <- yj
        
      }
        
#     
#     if(yj<ys)
#       if(y_less_dist>(ys-yj))
#         y_less_dist <- ys-yj
#     else
#       if(y_more_dist >(yj-ys))
#         y_more_dist <- yj-ys
  }
  #error_vertical[i] <- yk_min + (yj_min-yk_min)*((xs-xk_min)/(xj_min-xk_min+0.000001))
  yss <- y_more + (y_less-y_more)*((xs-x_more)/(x_less-x_more))
  error_horizontal[i]<- 100*abs((ys-yss)/yss)
  #print(i)
  #print(yss)
  #print(ys)
  #print(error_horizontal[i])
  
  
}

error_horizontal_frame <- data.frame(error_horizontal)
write.csv(error_horizontal_frame,"horizontal_error_4.csv",row.names=FALSE,col.names=FALSE)

